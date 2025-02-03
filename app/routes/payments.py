import os

import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config.dependencies import get_accounts_email_notificator, get_current_user
from app.config.settings import get_settings
from app.database.models.accounts import UserModel
from app.database.models.orders import OrderModel, OrderStatusEnum
from app.database.models.payments import (
    PaymentItemModel,
    PaymentModel,
    PaymentStatusEnum,
)
from app.database.session import get_db
from app.notifications.interfaces import EmailSenderInterface

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
settings = get_settings()


@router.get("/pay")
def create_checkout_session(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    order = db.query(OrderModel).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your order"
        )

    if order.status != OrderStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not pending"
        )

    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Order #{order.id}",
                        "description": "Movies purchase",
                    },
                    "unit_amount": int(order.total_amount * 100),
                },
                "quantity": 1,
            }
        ],
        metadata={
            "order_id": order.id,
            "user_id": current_user.id,
        },
        mode="payment",
        success_url=(
            f"{settings.BASE_URL}/payments/success?session_id={{CHECKOUT_SESSION_ID}}"
        ),
        cancel_url=f"{settings.BASE_URL}/payments/cancel",
    )
    return RedirectResponse(checkout_session.url, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    email_sender: EmailSenderInterface = Depends(get_accounts_email_notificator),
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["metadata"]["order_id"]

        order = db.query(OrderModel).filter_by(id=order_id).first()
        if order:
            order.status = OrderStatusEnum.PAID

            payment = PaymentModel(
                user_id=order.user_id,
                order_id=order.id,
                amount=order.total_amount,
                status=PaymentStatusEnum.SUCCESSFUL,
                external_payment_id=session.id,
            )
            db.add(payment)
            db.flush()

            for order_item in order.items:
                payment_item = PaymentItemModel(
                    payment_id=payment.id,
                    order_item_id=order_item.id,
                    price_at_payment=order_item.price_at_order,
                )
                db.add(payment_item)

            db.commit()

            watch_link = f"{settings.BASE_URL}/movies/purchased"
            background_tasks.add_task(
                email_sender.send_payment_success_email,
                email=order.user.email,
                user_name=order.user.profile.first_name or "Customer",
                amount=f"${order.total_amount:.2f}",
                watch_link=watch_link,
            )

    return {}


@router.get("/success")
def payment_success(session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            return {"message": "Payment successful! You can now watch your movies."}
        return {"message": "Payment is being processed."}
    except stripe.error.StripeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session ID"
        )


@router.get("/cancel")
def payment_canceled(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    order = (
        db.query(OrderModel)
        .filter(
            OrderModel.user_id == current_user.id,
            OrderModel.status == OrderStatusEnum.PENDING
        )
        .order_by(OrderModel.created_at.desc())
        .first()
    )

    if order:
        order.status = OrderStatusEnum.CANCELED
        db.commit()

    return {"message": "Payment was canceled."}


@router.post("/refund/{order_id}")
def refund_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    order = db.query(OrderModel).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your order"
        )

    if order.status != OrderStatusEnum.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not paid"
        )

    payment = db.query(PaymentModel).filter_by(order_id=order_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    try:
        refund = stripe.Refund.create(payment_intent=payment.external_payment_id)

        payment.status = PaymentStatusEnum.REFUNDED
        order.status = OrderStatusEnum.CANCELED
        db.commit()

        return {"status": "refunded", "refund_id": refund.id}
    except stripe.error.StripeError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/history")
def payment_history(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    payments = (
        db.query(PaymentModel)
        .filter_by(user_id=current_user.id)
        .order_by(PaymentModel.created_at.desc())
        .all()
    )
    return payments
