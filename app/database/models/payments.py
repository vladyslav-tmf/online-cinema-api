from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.sql import func

from app.database.models.base import Base


class PaymentStatusEnum(str, Enum):
    SUCCESSFUL = "successful"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class PaymentModel(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    status: Mapped[PaymentStatusEnum] = mapped_column(
        SQLAlchemyEnum(PaymentStatusEnum),
        nullable=False,
        default=PaymentStatusEnum.SUCCESSFUL,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    external_payment_id: Mapped[str | None] = mapped_column(String(255))

    user: Mapped["UserModel"] = relationship(back_populates="payments")
    order: Mapped["OrderModel"] = relationship(back_populates="payments")
    items: Mapped[list["PaymentItemModel"]] = relationship(
        back_populates="payment", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<PaymentModel(id={self.id}, amount={self.amount}, status={self.status})>"
        )


class PaymentItemModel(Base):
    __tablename__ = "payment_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE"), nullable=False
    )
    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False
    )
    price_at_payment: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    payment: Mapped["PaymentModel"] = relationship(back_populates="items")
    order_item: Mapped["OrderItemModel"] = relationship(back_populates="payment_items")

    def __repr__(self):
        return f"<PaymentItemModel(id={self.id}, price={self.price_at_payment})>"
