from fastapi import HTTPException
from app.models.subscription import Subscription
from app.models.member import Member
from app.models.plan import Plan
from app.repositories.subscription_repository import SubscriptionRepository

class SubscriptionService:
    @staticmethod
    def create(db,gym_id,data):
        member=db.query(Member).filter(Member.id==data["member_id"],Member.gym_id==gym_id).first()
        plan=db.query(Plan).filter(Plan.id==data["plan_id"],Plan.gym_id==gym_id).first()
        if not member or not plan:
            raise HTTPException(400,"Member and plan must belong to the current gym")
        obj=Subscription(
            status="active",
            invitation_limit=plan.max_invitations or 0,
            invitations_used=0,
            freeze_limit_days=plan.max_freeze_days or 0,
            freeze_used_days=0,
            **data
        )
        db.add(obj); db.commit(); db.refresh(obj); return obj

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

    @staticmethod
    def freeze(db,id,gym_id,days,reason=None):
        from datetime import date, datetime, timedelta, timezone
        from app.models.subscription_freeze import SubscriptionFreeze
        obj=SubscriptionRepository.get_by_id(db,id,gym_id)
        if not obj: raise HTTPException(404,"Subscription not found")
        if obj.status != "active": raise HTTPException(400,"Only active subscriptions can be frozen")
        remaining=max(0,(obj.freeze_limit_days or 0)-(obj.freeze_used_days or 0))
        if days > remaining: raise HTTPException(400,f"Only {remaining} freeze days remaining")
        start=max(date.today(),obj.start_date)
        end=start+timedelta(days=days-1)
        obj.end_date=obj.end_date+timedelta(days=days)
        obj.freeze_used_days=(obj.freeze_used_days or 0)+days
        db.add(SubscriptionFreeze(subscription_id=obj.id,start_date=start,end_date=end,days=days,reason=reason,created_at=datetime.now(timezone.utc)))
        db.commit();db.refresh(obj);return obj
