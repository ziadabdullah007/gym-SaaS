import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, String, Integer, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class GuestInvitation(Base):
    __tablename__ = "guest_invitations"
    __table_args__ = (Index("ix_guest_invitations_gym_phone", "gym_id", "guest_phone"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gym_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("gyms.id"))
    subscription_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subscriptions.id"))
    member_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("members.id"))
    attendance_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("attendance.id"))
    guest_name: Mapped[str] = mapped_column(String(255))
    guest_phone: Mapped[str] = mapped_column(String(50))
    guest_age: Mapped[int | None] = mapped_column(Integer)
    guest_weight: Mapped[float | None] = mapped_column(Numeric(6, 2))
    visit_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    subscription = relationship("Subscription", back_populates="guest_invitations")
    attendance = relationship("Attendance", back_populates="guest_invitations")
    member = relationship("Member")
