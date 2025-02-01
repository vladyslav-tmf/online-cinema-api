import datetime
from decimal import Decimal

from pydantic import BaseModel

from database.models.payments import PaymentStatusEnum


class PaymentSchema(BaseModel):
    created_at: datetime.datetime
    amount: Decimal
    status: PaymentStatusEnum

    model_config = {
        "from_attributes": True
    }
