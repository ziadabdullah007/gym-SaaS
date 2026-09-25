from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException
from app.models.subscription import Subscription
from app.models.member import Member
from app.models.plan import Plan
from app.models.payment import Payment
from app.repositories.subscription_repository import SubscriptionRepository

MIN_PAYMENT_RATIO = 0.50
MAX_PAYMENT_TERM_DAYS = 30

class SubscriptionService:
    @staticmethod
    def _sync_statuses(db, gym_id):
        today=date.today()
        rows=(db.query(Subscription)
            .filter(Subscription.member.has(gym_id=gym_id),
                    Subscription.status.in_(["active", "pending"])).all())
        changed=False
        for row in rows:
            if row.end_date < today and row.status in {"active", "pending"}:
                row.status="expired"; changed=True
            elif row.start_date <= today <= row.end_date and row.status == "pending":
                row.status="active"; changed=True
        if changed:
            db.commit()

    @staticmethod
    def _validate_initial_payment(amount, paid, due_date, start_date):
        minimum = round(float(amount) * MIN_PAYMENT_RATIO, 2)
        if paid < minimum:
            raise HTTPException(400, f"Initial payment must be at least 50% of the plan price ({minimum:.2f} EGP)")
        if paid > float(amount) + 0.009:
            raise HTTPException(400, "Initial payment cannot exceed the subscription price")
        if paid < float(amount) - 0.009:
            if not due_date:
                raise HTTPException(400, "Payment due date is required when the subscription is not fully paid")
            agreement_date = date.today()
            latest = agreement_date + timedelta(days=MAX_PAYMENT_TERM_DAYS)
            if due_date < agreement_date or due_date > latest:
                raise HTTPException(400, "Payment due date must be within 30 days from today")
        elif due_date and due_date > date.today() + timedelta(days=MAX_PAYMENT_TERM_DAYS):
            raise HTTPException(400, "Payment due date cannot be more than 30 days from today")

    @staticmethod
    def create(db,gym_id,data):
        SubscriptionService._sync_statuses(db,gym_id)
        member=db.query(Member).filter(Member.id==data["member_id"],Member.gym_id==gym_id).first()
        plan=db.query(Plan).filter(Plan.id==data["plan_id"],Plan.gym_id==gym_id,Plan.status=="active").first()
        if not member or not plan:
            raise HTTPException(400,"Member and plan must belong to the current gym")
        active=db.query(Subscription).filter(Subscription.member_id==member.id,Subscription.status=="active",Subscription.end_date>=date.today()).first()
        if active:
            raise HTTPException(409,"Member already has an active subscription. Use Renew instead.")
        amount=float(plan.price)
        submitted_amount=float(data.pop("amount"))
        if abs(submitted_amount-amount)>0.009:
            raise HTTPException(400,"Subscription amount must match the selected plan price")
        paid=float(data.pop("initial_payment_amount"))
        method=data.pop("initial_payment_method")
        due=data.pop("payment_due_date",None)
        SubscriptionService._validate_initial_payment(amount,paid,due,data["start_date"])
        today=date.today()
        if data["start_date"] > today:
            subscription_status="pending"
        elif data["start_date"] <= today <= data["end_date"]:
            subscription_status="active"
        else:
            subscription_status="expired"
        obj=Subscription(
            status=subscription_status, amount=amount, payment_due_date=None if paid>=amount-0.009 else due,
            invitation_limit=plan.max_invitations or 0, invitations_used=0,
            freeze_limit_days=plan.max_freeze_days or 0, freeze_used_days=0, **data
        )
        try:
            db.add(obj); db.flush()
            db.add(Payment(subscription_id=obj.id,amount=paid,payment_method=method,status="completed",payment_date=datetime.now(timezone.utc)))
            db.commit(); db.refresh(obj); return obj
        except Exception:
            db.rollback(); raise

    @staticmethod
    def renew(db,gym_id,subscription_id,data):
        SubscriptionService._sync_statuses(db,gym_id)
        current=SubscriptionRepository.get_by_id(db,subscription_id,gym_id)
        if not current: raise HTTPException(404,"Subscription not found")
        if current.status != "active": raise HTTPException(400,"Only an active subscription can be renewed")
        if current.remaining_amount > 0.009:
            raise HTTPException(400,"Pay the current subscription balance before renewing")
        pending=db.query(Subscription).filter(Subscription.member_id==current.member_id,Subscription.status=="pending").first()
        if pending:
            raise HTTPException(409,"A renewal is already pending for this member")
        plan=db.query(Plan).filter(Plan.id==data["plan_id"],Plan.gym_id==gym_id,Plan.status=="active").first()
        if not plan: raise HTTPException(400,"Plan not found")
        amount=float(plan.price); paid=float(data["initial_payment_amount"]); due=data.get("payment_due_date")
        renewal_start=current.end_date+timedelta(days=1)
        # The payment agreement is made today, even though the renewed membership starts later.
        SubscriptionService._validate_initial_payment(amount,paid,due,date.today())
        new_end=renewal_start + timedelta(days=30*plan.duration_months) - timedelta(days=1)
        new_status="active" if renewal_start <= date.today() <= new_end else "pending"
        obj=Subscription(
            member_id=current.member_id, plan_id=plan.id, start_date=renewal_start, end_date=new_end,
            status=new_status, amount=amount, auto_renew=False,
            payment_due_date=None if paid>=amount-0.009 else due,
            invitation_limit=plan.max_invitations or 0, invitations_used=0,
            freeze_limit_days=plan.max_freeze_days or 0, freeze_used_days=0
        )
        try:
            db.add(obj); db.flush()
            db.add(Payment(subscription_id=obj.id,amount=paid,payment_method=data.get("initial_payment_method","cash"),status="completed",payment_date=datetime.now(timezone.utc)))
            db.commit(); db.refresh(obj); return obj
        except Exception:
            db.rollback(); raise

    @staticmethod
    def list(db,gym_id):
        SubscriptionService._sync_statuses(db,gym_id)
        return SubscriptionRepository.get_all(db,gym_id)

    @staticmethod
    def get(db,id,gym_id):
        SubscriptionService._sync_statuses(db,gym_id)
        return SubscriptionRepository.get_by_id(db,id,gym_id)

    @staticmethod
    def update(db,id,gym_id,data):
        obj=SubscriptionRepository.get_by_id(db,id,gym_id)
        if not obj:return None
        if obj.status != "active": raise HTTPException(400,"Only active subscriptions can be edited")
        for k,v in data.items():
            if v is not None:setattr(obj,k,v)
        db.commit();db.refresh(obj);return obj

    @staticmethod
    def cancel(db,id,gym_id):
        obj=SubscriptionRepository.get_by_id(db,id,gym_id)
        if not obj: raise HTTPException(404,"Subscription not found")
        if obj.status == "cancelled": raise HTTPException(400,"Subscription is already cancelled")
        obj.status="cancelled"; db.commit(); db.refresh(obj); return obj

    @staticmethod
    def freeze(db,id,gym_id,days,reason=None):
        from app.models.subscription_freeze import SubscriptionFreeze
        obj=SubscriptionRepository.get_by_id(db,id,gym_id)
        if not obj: raise HTTPException(404,"Subscription not found")
        if obj.status != "active": raise HTTPException(400,"Only active subscriptions can be frozen")
        if obj.payment_status == "overdue": raise HTTPException(400,"Overdue subscriptions cannot be frozen until payment is settled")
        remaining=max(0,(obj.freeze_limit_days or 0)-(obj.freeze_used_days or 0))
        if days > remaining: raise HTTPException(400,f"Only {remaining} freeze days remaining")
        start=max(date.today(),obj.start_date)
        end=start+timedelta(days=days-1)
        obj.end_date=obj.end_date+timedelta(days=days)
        obj.freeze_used_days=(obj.freeze_used_days or 0)+days
        db.add(SubscriptionFreeze(subscription_id=obj.id,start_date=start,end_date=end,days=days,reason=reason,created_at=datetime.now(timezone.utc)))
        db.commit();db.refresh(obj);return obj
