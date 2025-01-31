import datetime
from decimal import Decimal

from pydantic import BaseModel

from database.models.movies import MovieModel
from database.models.orders import OrderStatusEnum
from schemas.examples.orders import order_schema_example, order_item_schema_example


class OrderSchema(BaseModel):
    id: int
    user_id: int
    created_at: datetime.datetime
    status: OrderStatusEnum
    total_amount: Decimal
    movies: list[MovieModel]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                order_schema_example
            ]
        }
    }


class OrderItemSchema(BaseModel):
    id: int
    order_id: int
    movie_id: int
    price_at_order: Decimal

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                order_item_schema_example
            ]
        }
    }
