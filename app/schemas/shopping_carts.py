import datetime
from pydantic import BaseModel

from app.database.models.accounts import UserModel
from app.database.models.shopping_carts import CartItemModel


class CartSchema(BaseModel):
    id: int
    user_id: int
    user: UserModel
    cart_items: list[CartItemModel]

    model_config = {
        "from_attributes": True
    }


class CartItemSchema(BaseModel):
    id: int
    cart_id: int
    movie_id: int
    added_at: datetime

    model_config = {
        "from_attributes": True
    }
