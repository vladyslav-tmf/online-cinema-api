from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from starlette import status

from app.config.dependencies import get_current_user
from app.database.models.accounts import UserModel
from app.database.models.movies import MovieModel
from app.database.models.orders import OrderItemModel, OrderModel
from app.database.models.payments import PaymentModel, PaymentStatusEnum
from app.database.models.shopping_carts import CartItemModel, CartModel
from app.database.session import get_db
from app.schemas.shopping_carts import (
    CartItemCreateSchema,
    CartItemResponseSchema,
    CartResponseSchema,
)

router = APIRouter()


def check_movie_availability(movie_id: int, user_id: int, db: Session) -> None:
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found"
        )

    purchased = (
        db.query(OrderItemModel)
        .join(OrderModel)
        .join(PaymentModel)
        .filter(
            OrderItemModel.movie_id == movie_id,
            OrderModel.user_id == user_id,
            PaymentModel.status == PaymentStatusEnum.SUCCESSFUL,
        )
        .first()
    )

    if purchased:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already purchased this movie",
        )


@router.get("/", response_model=CartResponseSchema,
            summary="Get user's cart",
            description="Retrieves the current user's cart.",
            responses={
    200: {
        "description": "Successfully retrieved the user's cart or created a new one.",
    },
    404: {
        "description": "Cart not found and failed to create a new one.",
    }
})
def get_cart(
    current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)
):
    cart = (
        db.query(CartModel)
        .options(joinedload(CartModel.cart_items).joinedload(CartItemModel.movie))
        .filter(CartModel.user_id == current_user.id)
        .first()
    )

    if not cart:
        cart = CartModel(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


@router.post("/items/", response_model=CartItemResponseSchema,
             summary="Add item to cart",
             description="This endpoint adds an item to the user's cart. If the item already exists in the cart, an error is returned.",
             responses={
                 201: {
                     "description": "Item successfully added to the cart.",
                 },
                 400: {
                     "description": "Item already exists in the cart.",
                 },
                 404: {
                     "description": "Cart not found or item not available.",
                 }
             }
             )
def add_item_to_cart(
    item_data: CartItemCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_movie_availability(item_data.movie_id, current_user.id, db)

    cart = db.query(CartModel).filter(CartModel.user_id == current_user.id).first()

    if not cart:
        cart = CartModel(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    try:
        cart_item = CartItemModel(cart_id=cart.id, movie_id=item_data.movie_id)
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        cart_item = (
            db.query(CartItemModel)
            .options(joinedload(CartItemModel.movie))
            .filter(CartItemModel.id == cart_item.id)
            .first()
        )
        return cart_item
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item already exists in cart",
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Remove item from cart",
               description="This endpoint removes an item from the user's cart.",
               responses={
                   204: {
                       "description": "Item successfully removed from the cart."
                   },
                   404: {
                       "description": "Cart or item not found in cart.",
                   }
               }
               )
def remove_item_from_cart(
    item_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = db.query(CartModel).filter(CartModel.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )

    cart_item = (
        db.query(CartItemModel)
        .filter(CartItemModel.id == item_id, CartItemModel.cart_id == cart.id)
        .first()
    )
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart"
        )

    db.delete(cart_item)
    db.commit()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT,
               summary="Clear cart",
               description="This endpoint removes all items from the user's cart.",
               responses={
                   204: {
                       "description": "All items successfully removed from the cart."
                   },
                   404: {
                       "description": "Cart not found.",
                   }
               }
               )
def clear_cart(
    current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)
):
    cart = db.query(CartModel).filter(CartModel.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )

    db.query(CartItemModel).filter(CartItemModel.cart_id == cart.id).delete()
    db.commit()
