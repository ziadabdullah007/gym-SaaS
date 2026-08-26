from fastapi import HTTPException
from app.models.subscription import Subscription
from app.models.member import Member
from app.models.plan import Plan
from app.repositories.subscription_repository import SubscriptionRepository
class SubscriptionService:
    @staticmethod
    def create(db,gym_id,data):
        member=db.query(Member).filter(Member.id==data["member_id"],Member.gym_id==gym_id).first(); plan=db.query(Plan).filter(Plan.id==data["plan_id"],Plan.gym_id==gym_id).first()
        if not member or not plan: raise HTTPException(400,"Member and plan must belong to the current gym")
        obj=Subscription(status="active",**data); db.add(obj); db.commit();db.refresh(obj);return obj
    @staticmethod
    def list(db,gym_id): return SubscriptionRepository.get_all(db,gym_id)
    @staticmethod
    def get(db,id,gym_id): return SubscriptionRepository.get_by_id(db,id,gym_id)
    @staticmethod
    def update(db,id,gym_id,data):
        obj=SubscriptionRepository.get_by_id(db,id,gym_id)
        if not obj:return None
        for k,v in data.items():
            if v is not None:setattr(obj,k,v)
        db.commit();db.refresh(obj);return obj
