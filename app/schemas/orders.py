import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.database.models.orders import OrderStatusEnum
from app.schemas.examples.orders import order_item_schema_example, order_schema_example
from app.schemas.movies import MovieSchema
from app.schemas.shopping_carts import CartItemResponseSchema


class OrderSchema(BaseModel):
    id: int
    user_id: int
    created_at: datetime.datetime
    status: OrderStatusEnum
    total_amount: Decimal
    movies: list[MovieSchema]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"examples": [order_schema_example]},
    }


class OrderCreateSchema(BaseModel):
    order_items: list[CartItemResponseSchema]

    model_config = {"from_attributes": True}


class OrderListResponseSchema(BaseModel):
    order: OrderSchema
    prev_page: str | None
    next_page: str | None
    total_pages: int
    total_items: int


class OrderItemSchema(BaseModel):
    order_id: int
    movie_id: int
    price_at_order: Decimal

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"examples": [order_item_schema_example]},
    }
