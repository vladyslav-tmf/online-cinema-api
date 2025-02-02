from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette import status

from database.models.shopping_carts import CartModel, CartItemModel
from database.models.movies import MovieModel
from schemas.shopping_carts import CartSchema, CartItemSchema
from database.session import get_db
from config.dependencies import get_current_user
from database.models.accounts import UserModel


router = APIRouter()


@router.get("/cart/", response_model=CartSchema)
def get_cart(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart = db.query(CartModel).filter(
        CartModel.user_id == current_user.id
    ).first()
    if not cart:
        cart = CartModel(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.post("/cart/items/", response_model=CartItemSchema)
def add_item_to_cart(
    movie_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart = db.query(CartModel).filter(
        CartModel.user_id == current_user.id
    ).first()
    if not cart:
        cart = CartModel(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    movie = db.query(MovieModel).filter(
        MovieModel.id == movie_id
    ).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    try:
        cart_item = CartItemModel(cart_id=cart.id, movie_id=movie_id)
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item already in cart"
        )


@router.delete(
    "/cart/items/{item_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_item_from_cart(
    item_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart = db.query(CartModel).filter(
        CartModel.user_id == current_user.id
    ).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    cart_item = db.query(CartItemModel).filter(
        CartItemModel.id == item_id,
        CartItemModel.cart_id == cart.id
    ).first()
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart"
        )

    db.delete(cart_item)
    db.commit()


@router.delete("/cart/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart = db.query(CartModel).filter(
        CartModel.user_id == current_user.id
    ).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    db.query(CartItemModel).filter(
        CartItemModel.cart_id == cart.id
    ).delete()
    db.commit()
