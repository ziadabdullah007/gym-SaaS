import uuid
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Date, Numeric, Boolean, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("members.id"))
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    auto_renew: Mapped[bool] = mapped_column(Boolean)
    payment_due_date: Mapped[date | None] = mapped_column(Date)
    invitation_limit: Mapped[int] = mapped_column(Integer, default=0)
    invitations_used: Mapped[int] = mapped_column(Integer, default=0)
    freeze_limit_days: Mapped[int] = mapped_column(Integer, default=0)
    freeze_used_days: Mapped[int] = mapped_column(Integer, default=0)
    member = relationship("Member", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")
    guest_invitations = relationship("GuestInvitation", back_populates="subscription")
    freezes = relationship("SubscriptionFreeze", back_populates="subscription")

    @property
    def invitations_remaining(self):
        return max(0, (self.invitation_limit or 0) - (self.invitations_used or 0))

    @property
    def freeze_remaining_days(self):
        return max(0, (self.freeze_limit_days or 0) - (self.freeze_used_days or 0))

    @property
    def plan_name(self):
        return self.plan.name if self.plan is not None else None

    @property
    def paid_amount(self):
        total = sum((Decimal(str(p.amount or 0)) for p in (self.payments or [])), Decimal("0"))
        return float(total)

    @property
    def remaining_amount(self):
        return max(0.0, float(self.amount or 0) - self.paid_amount)

    @property
    def payment_status(self):
        remaining = self.remaining_amount
        if remaining <= 0.009:
            return "paid"
        if self.paid_amount <= 0.009:
            return "unpaid"
        if self.payment_due_date and self.payment_due_date < date.today():
            return "overdue"
        return "partially_paid"

    @property
    def check_in_allowed(self):
        today = date.today()
        return (
            self.status == "active"
            and self.start_date <= today <= self.end_date
            and self.payment_status in {"paid", "partially_paid"}
            and not (self.payment_status == "overdue")
        )
