from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from schemas.movies import MovieSchema


class CartItemBaseSchema(BaseModel):
    movie_id: int

    model_config = ConfigDict(from_attributes=True)


class CartItemCreateSchema(CartItemBaseSchema):
    pass


class CartItemResponseSchema(CartItemBaseSchema):
    id: int
    cart_id: int
    added_at: datetime
    movie: MovieSchema

    model_config = ConfigDict(from_attributes=True)


class CartBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CartResponseSchema(CartBaseSchema):
    id: int
    user_id: int
    cart_items: list[CartItemResponseSchema]

    @property
    def total_price(self) -> Decimal:
        return Decimal(sum(item.movie.price for item in self.cart_items))
