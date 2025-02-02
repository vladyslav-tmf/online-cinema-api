import datetime
from decimal import Decimal

from pydantic import BaseModel

from database.models.payments import PaymentStatusEnum
from schemas.orders import OrderSchema, OrderItemSchema
from schemas.users import UserSchema


class PaymentListSchema(BaseModel):
    created_at: datetime.datetime
    amount: Decimal
    status: PaymentStatusEnum

    model_config = {"from_attributes": True}


class PaymentSchema(BaseModel):
    id: int
    user_id: int
    order_id: int
    created_at: datetime.datetime
    status: PaymentStatusEnum
    amount: Decimal
    user: UserSchema
    order: OrderSchema
    items: list["PaymentItemSchema"]

    model_config = {"from_attributes": True}


class PaymentItemSchema(BaseModel):
    id: int
    payment_id: int
    order_item_id: int
    price_at_payment: Decimal
    payment: PaymentSchema
    order_item: OrderItemSchema

    model_config = {"from_attributes": True}
