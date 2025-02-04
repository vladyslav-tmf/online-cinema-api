import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config.dependencies import get_current_user
from app.database.models.accounts import UserGroupEnum, UserModel
from app.database.models.orders import OrderItemModel, OrderModel, OrderStatusEnum
from app.database.session import get_db
from app.routes.shopping_carts import check_movie_availability
from app.schemas.orders import OrderCreateSchema, OrderListResponseSchema, OrderSchema

router = APIRouter()


@router.get(
    "/",
    response_model=OrderListResponseSchema,
    summary="Get a list of orders",
    description=(
        "Fetches a paginated list of orders, optionally filtered by users, date, "
        "and status. Only admins can see all orders, "
        "while regular users can only see their own orders."
    ),
    responses={
        200: {
            "description": "A list of orders",
        },
        404: {
            "description": "No orders found",
        },
    },
)
def get_order_list(
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
    users: list[int] = Query(ge=1, description="filter by users"),
    date: datetime.datetime = Query(description="filter by date"),
    status: str = Query(description="filter by status"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    offset = (page - 1) * per_page

    query = db.query(OrderModel).order_by()
    if users:
        query = query.filter(OrderModel.user_id.in_(users))
    if status:
        query = query.filter_by(status=status)
    if date:
        query = query.filter_by(date=date)

    total_items = query.count()
    if current_user.group == UserGroupEnum.USER:
        query.filter_by(user_id=current_user.id)
    order = query.offset(offset).limit(per_page)

    if not order:
        raise HTTPException(status_code=404, detail="No orders found.")

    total_pages = (total_items + per_page - 1) // per_page

    response = OrderListResponseSchema(
        orders=OrderSchema.model_validate(order),
        prev_page=(
            f"/theater/movies/?page={page - 1}&per_page={per_page}"
            if page > 1
            else None
        ),
        next_page=(
            f"/theater/movies/?page={page + 1}&per_page={per_page}"
            if page < total_pages
            else None
        ),
        total_pages=total_pages,
        total_items=total_items,
    )
    return response


def check_pending_orders(movie_ids: list[int], user_id: int, db: Session) -> None:
    pending_orders = (
        db.query(OrderModel)
        .filter(
            OrderModel.user_id == user_id, OrderModel.status == OrderStatusEnum.PENDING
        )
        .all()
    )

    for order in pending_orders:
        order_movie_ids = [item.movie_id for item in order.items]
        if any(movie_id in order_movie_ids for movie_id in movie_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have pending orders with these movies",
            )


@router.post(
    "/",
    response_model=None,
    summary="Create a new order",
    description=(
        "Creates a new order for the currently authenticated user. "
        "The cart items are checked for availability and duplicates."
    ),
    responses={
        303: {
            "description": "Redirects to the payment page for the created order",
        },
        409: {
            "description": "Conflict: Duplicate or empty cart",
        },
        400: {
            "description": "Bad request: Invalid input data",
        },
    },
)
def create_order(
    order_data: OrderCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        movie_ids = [item.movie_id for item in order_data.order_items]
        check_pending_orders(movie_ids, current_user.id, db)

        order = OrderModel(user_id=current_user.id)

        db.add(order)
        db.flush()
        db.refresh(order)

        if not order_data.order_items:
            raise HTTPException(status_code=409, detail="Your cart is empty")

        total_amount = Decimal("0")

        for order_item in order_data.order_items:
            existing_order_item = (
                db.query(OrderItemModel)
                .filter_by(order_id=order.id, movie_id=order_item.movie_id)
                .first()
            )

            check_movie_availability(order_item.movie_id, current_user.id, db)

            if existing_order_item:
                raise HTTPException(
                    status_code=409,
                    detail=f"Duplicate purchase of movie with ID {order_item.movie_id}",
                )

            price_at_order = Decimal(str(order_item.movie.price))
            item = OrderItemModel(
                order_id=order.id,
                movie_id=order_item.movie_id,
                price_at_order=price_at_order,
            )

            total_amount += price_at_order

            db.add(item)
            db.flush()
            db.refresh(item)

        order.total_amount = total_amount

        db.commit()

        return RedirectResponse(
            url=f"/payments/pay?order_id={order.id}", status_code=303
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid input data.")


@router.post(
    "/{order_id}/cancel",
    summary="Cancel an order",
    description=(
        "Cancels the specified order. "
        "If the order is already paid, it redirects to the payment refund page."
    ),
    responses={
        200: {
            "description": "Redirects to the payment refund page if the order is paid",
        },
        403: {
            "description": (
                "Forbidden: User does not have permission to cancel the order"
            ),
        },
        404: {
            "description": "Not found: The order with the given ID was not found",
        },
    },
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    order = db.query(OrderModel).filter_by(id=order_id).first()

    if order.user_id != current_user.id and current_user.group != UserGroupEnum.ADMIN:
        raise HTTPException(status_code=403, detail="You don't have permissions.")

    if not order:
        raise HTTPException(
            status_code=404, detail="Order with the given ID was not found."
        )

    if order.status == OrderStatusEnum.PAID:
        return RedirectResponse(url="/payments/refund", status_code=303)
    order.status = OrderStatusEnum.CANCELED

    db.commit()


@router.delete(
    "/{order_id}",
    status_code=204,
    summary="Delete an order",
    description=(
        "Deletes the specified order. "
        "The user must be the one who created the order or an admin."
    ),
    responses={
        204: {
            "description": "Order deleted successfully",
        },
        403: {
            "description": (
                "Forbidden: User does not have permission to delete the order"
            ),
        },
        404: {
            "description": "Not found: The order with the given ID was not found",
        },
    },
)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    order = db.query(OrderModel).filter_by(id=order_id).first()

    if order.user_id != current_user.id and current_user.group != UserGroupEnum.ADMIN:
        raise HTTPException(status_code=403, detail="You don't have permissions.")

    if not order:
        raise HTTPException(
            status_code=404, detail="Order with the given ID was not found."
        )

    db.delete(order)
    db.commit()
    return {"detail": "Order deleted successfully."}
