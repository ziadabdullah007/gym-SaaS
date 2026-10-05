from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel


class MemberAppSubscription(BaseModel):
    id: UUID
    plan_name: str | None
    start_date: date
    end_date: date
    status: str
    amount: float
    paid_amount: float
    remaining_amount: float
    payment_status: str
    payment_due_date: date | None
    days_until_payment_due: int | None
    check_in_allowed: bool


class MemberAppPayment(BaseModel):
    id: UUID
    subscription_id: UUID
    amount: float
    payment_method: str
    status: str
    payment_date: datetime


class MemberAppProfileResponse(BaseModel):
    id: UUID
    username: str | None
    name: str
    first_name: str
    last_name: str
    email: str | None
    phone: str
    date_of_birth: date | None
    gender: str | None
    height: float | None
    weight: float | None
    status: str
    app_access_enabled: bool
    joined_at: datetime
    last_visit_at: datetime | None
    subscription: MemberAppSubscription | None
    subscriptions: list[MemberAppSubscription]
    payments: list[MemberAppPayment]


class MemberAppQrResponse(BaseModel):
    qr_token: str
    expires_in: int
