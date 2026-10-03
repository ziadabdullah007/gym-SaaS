import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Member(Base):
    __tablename__ = "members"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gym_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("gyms.id"))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50))
    username: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    height: Mapped[float | None] = mapped_column(Numeric(5, 2))
    weight: Mapped[float | None] = mapped_column(Numeric(5, 2))
    status: Mapped[str] = mapped_column(String(50))
    app_access_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    entry_qr_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_reset_code_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_visit_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    gym = relationship("Gym", back_populates="members")
    subscriptions = relationship("Subscription", back_populates="member")
    attendance_records = relationship("Attendance", back_populates="member")
    body_measurements = relationship("BodyMeasurement", back_populates="member")
    guest_invitations = relationship("GuestInvitation", back_populates="member")

    @property
    def app_has_password(self) -> bool:
        return bool(self.password_hash)
