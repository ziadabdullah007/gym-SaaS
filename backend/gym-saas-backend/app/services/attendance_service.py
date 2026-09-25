from datetime import datetime,timezone
from fastapi import HTTPException
from app.models.attendance import Attendance
from app.models.member import Member
from app.models.subscription import Subscription
from app.models.guest_invitation import GuestInvitation
from app.repositories.attendance_repository import AttendanceRepository

class AttendanceService:
    @staticmethod
    def check_in(db,gym_id,member_id,guests=None):
        guests=guests or []
        member=db.query(Member).filter(Member.id==member_id,Member.gym_id==gym_id).first()
        if not member: raise HTTPException(404,"Member not found")
        active=db.query(Attendance).filter(Attendance.member_id==member_id,Attendance.check_out_time.is_(None)).first()
        if active: raise HTTPException(400,"Member is already checked in")
        now=datetime.now(timezone.utc)
        subscription=(db.query(Subscription)
            .join(Member,Subscription.member_id==Member.id)
            .filter(Subscription.member_id==member_id,Member.gym_id==gym_id,Subscription.status=="active",Subscription.start_date<=now.date(),Subscription.end_date>=now.date())
            .order_by(Subscription.end_date.desc()).first())
        if not subscription: raise HTTPException(400,"Member does not have an active subscription")
        if subscription.payment_status == "overdue":
            raise HTTPException(403,f"Check-in blocked. Outstanding payment: {subscription.remaining_amount:.2f} EGP")
        if subscription.payment_status == "unpaid":
            raise HTTPException(403,"Check-in blocked. Subscription payment is not active.")
        remaining=max(0,(subscription.invitation_limit or 0)-(subscription.invitations_used or 0))
        if len(guests)>remaining: raise HTTPException(400,f"Only {remaining} invitations remaining")
        try:
            obj=Attendance(member_id=member_id,check_in_time=now,check_out_time=None,created_at=now)
            db.add(obj); db.flush()
            for guest in guests:
                db.add(GuestInvitation(gym_id=gym_id,subscription_id=subscription.id,member_id=member_id,attendance_id=obj.id,guest_name=guest.name,guest_phone=guest.phone,guest_age=guest.age,guest_weight=guest.weight,visit_date=now,created_at=now))
            subscription.invitations_used=(subscription.invitations_used or 0)+len(guests)
            member.last_visit_at=now
            db.commit(); db.refresh(obj); return obj
        except Exception:
            db.rollback(); raise

    @staticmethod
    def check_out(db,gym_id,attendance_id):
        obj=AttendanceRepository.get_by_id(db,attendance_id,gym_id)
        if not obj:raise HTTPException(404,"Attendance not found")
        if obj.check_out_time:raise HTTPException(400,"Attendance already checked out")
        obj.check_out_time=datetime.now(timezone.utc);db.commit();db.refresh(obj);return obj
    @staticmethod
    def list(db,gym_id):return AttendanceRepository.get_all(db,gym_id)
