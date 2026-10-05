from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from datetime import datetime

class GuestInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=1, max_length=50)
    age: int | None = Field(default=None, ge=1, le=120)
    weight: float | None = Field(default=None, ge=0, le=500)

class AttendanceCheckIn(BaseModel):
    member_id: UUID | None = None
    qr_token: str | None = Field(default=None, min_length=20, max_length=1024)

    @model_validator(mode="after")
    def require_one_identifier(self):
        if bool(self.member_id) == bool(self.qr_token):
            raise ValueError("Provide exactly one of member_id or qr_token")
        return self

class AttendanceResponse(BaseModel):
    id: UUID
    member_id: UUID
    subscription_id: UUID | None = None
    source: str = "manual"
    check_in_time: datetime
    check_out_time: datetime | None
    created_at: datetime
    guest_count: int = 0
    model_config = {"from_attributes": True}

class GuestRegistration(BaseModel):
    guests: list[GuestInput] = Field(min_length=1, max_length=20)
