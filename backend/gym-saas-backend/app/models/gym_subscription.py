import uuid
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class GymSubscription(Base):
    __tablename__ = "gym_subscriptions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gym_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("gyms.id"))
    saas_plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("saas_plans.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50))
    saas_plan = relationship("SaaSPlan", back_populates="gym_subscriptions")
    gym = relationship("Gym", back_populates="gym_subscriptions")
