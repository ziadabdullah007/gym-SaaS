from datetime import datetime,timezone
from fastapi import HTTPException
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.repositories.payment_repository import PaymentRepository

class PaymentService:
    @staticmethod
    def create(db,gym_id,data):
        if data.get("idempotency_key"):
            existing=db.query(Payment).filter(Payment.idempotency_key==data["idempotency_key"]).first()
            if existing:
                return existing
        sub=db.query(Subscription).filter(Subscription.id==data["subscription_id"],Subscription.member.has(gym_id=gym_id)).first()
        if not sub: raise HTTPException(404,"Subscription not found")
        remaining=sub.remaining_amount
        amount=float(data["amount"])
        if amount > remaining + 0.009:
            raise HTTPException(400,f"Payment cannot exceed the remaining balance of {remaining:.2f} EGP")
        if remaining <= 0.009:
            raise HTTPException(400,"This subscription is already fully paid")
        obj=Payment(status="completed",payment_date=datetime.now(timezone.utc),**data)
        db.add(obj)
        try:
            db.flush()
            if remaining-amount <= 0.009:
                sub.payment_due_date=None
            db.commit();db.refresh(obj);return obj
        except Exception:
            db.rollback(); raise
    @staticmethod
    def list(db,gym_id):return PaymentRepository.get_all(db,gym_id)
    @staticmethod
    def get(db,id,gym_id):return PaymentRepository.get_by_id(db,id,gym_id)
