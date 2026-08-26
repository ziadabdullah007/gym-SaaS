from datetime import datetime,timezone
from fastapi import HTTPException
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.repositories.payment_repository import PaymentRepository
class PaymentService:
    @staticmethod
    def create(db,gym_id,data):
        sub=db.query(Subscription).filter(Subscription.id==data["subscription_id"],Subscription.member.has(gym_id=gym_id)).first()
        if not sub: raise HTTPException(404,"Subscription not found")
        obj=Payment(status="completed",payment_date=datetime.now(timezone.utc),**data); db.add(obj); db.commit();db.refresh(obj);return obj
    @staticmethod
    def list(db,gym_id):return PaymentRepository.get_all(db,gym_id)
    @staticmethod
    def get(db,id,gym_id):return PaymentRepository.get_by_id(db,id,gym_id)
