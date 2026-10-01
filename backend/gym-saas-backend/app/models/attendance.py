import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("members.id"))
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("subscriptions.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="manual", nullable=False)
    check_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    check_out_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    member = relationship("Member", back_populates="attendance_records")
    guest_invitations = relationship("GuestInvitation", back_populates="attendance")

    @property
    def guest_count(self):
        return len(self.guest_invitations or [])
