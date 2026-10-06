from datetime import datetime, timezone, timedelta
from time import perf_counter
import logging
import hashlib
import jwt
from jwt import InvalidTokenError
from app.core.config import settings
from fastapi import HTTPException
from app.models.attendance import Attendance
from app.models.member import Member
from app.models.subscription import Subscription
from app.models.guest_invitation import GuestInvitation
from app.repositories.attendance_repository import AttendanceRepository

logger = logging.getLogger("gym_aura.attendance")

class AttendanceService:
    @staticmethod
    def _get_eligible_subscription(db, member, now):
        subscription = (db.query(Subscription)
            .filter(Subscription.member_id == member.id, Subscription.status == "active",
                    Subscription.start_date <= now.date(), Subscription.end_date >= now.date())
            .order_by(Subscription.end_date.desc()).first())
        if not subscription:
            raise HTTPException(400, "Member does not have an active subscription")
        if subscription.payment_status == "overdue":
            raise HTTPException(403, f"Check-in blocked. Outstanding payment: {subscription.remaining_amount:.2f} EGP")
        if subscription.payment_status == "unpaid":
            raise HTTPException(403, "Check-in blocked. Subscription payment is not active.")
        return subscription

    @staticmethod
    def check_in(db, gym_id, member_id=None, qr_token=None):
        """Check a member in and emit server-side timing diagnostics.

        The diagnostics deliberately log timings only; QR tokens and other secrets
        are never logged. This makes it possible to distinguish JWT/QR work from
        Supabase/DB latency when a scan appears to take many seconds.
        """
        t0 = perf_counter()
        timings = {}
        source = "qr" if qr_token else "manual"
        member = None
        try:
            # QR verification / member lookup
            step = perf_counter()
            if qr_token:
                try:
                    claims = jwt.decode(qr_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                    if claims.get("typ") != "gymflow_entry_qr" or claims.get("gym_id") != str(gym_id):
                        raise HTTPException(401, "Invalid QR code")
                    member = db.query(Member).filter(
                        Member.id == claims.get("sub"), Member.gym_id == gym_id
                    ).first()
                except InvalidTokenError:
                    token_hash = hashlib.sha256(qr_token.encode("utf-8")).hexdigest()
                    member = db.query(Member).filter(
                        Member.gym_id == gym_id, Member.entry_qr_token_hash == token_hash
                    ).first()
            else:
                member = db.query(Member).filter(
                    Member.id == member_id, Member.gym_id == gym_id
                ).first()
            timings["qr_or_member_lookup_ms"] = round((perf_counter() - step) * 1000, 2)

            if not member:
                raise HTTPException(404, "Invalid QR code or member not found" if qr_token else "Member not found")

            # Duplicate attendance lookup
            now = datetime.now(timezone.utc)
            step = perf_counter()
            duplicate = db.query(Attendance).filter(
                Attendance.member_id == member.id,
                Attendance.check_in_time >= now - timedelta(seconds=90)
            ).first()
            timings["duplicate_check_ms"] = round((perf_counter() - step) * 1000, 2)
            if duplicate:
                raise HTTPException(409, "A check-in was already recorded moments ago")

            # Subscription / payment eligibility lookup
            step = perf_counter()
            subscription = AttendanceService._get_eligible_subscription(db, member, now)
            timings["subscription_check_ms"] = round((perf_counter() - step) * 1000, 2)

            # Insert + commit
            obj = Attendance(
                member_id=member.id,
                subscription_id=subscription.id,
                source=source,
                check_in_time=now,
                check_out_time=None,
                created_at=now,
            )
            step = perf_counter()
            db.add(obj)
            member.last_visit_at = now
            db.commit()
            timings["insert_commit_ms"] = round((perf_counter() - step) * 1000, 2)

            step = perf_counter()
            db.refresh(obj)
            timings["refresh_ms"] = round((perf_counter() - step) * 1000, 2)
            return obj
        except HTTPException:
            raise
        except Exception:
            db.rollback()
            raise
        finally:
            timings["total_ms"] = round((perf_counter() - t0) * 1000, 2)
            member_ref = str(member.id) if member else "unknown"
            logger.info(
                "ATTENDANCE_CHECKIN_TIMING source=%s gym_id=%s member_id=%s timings=%s",
                source, gym_id, member_ref, timings
            )

    @staticmethod
    def register_guests(db, gym_id, attendance_id, guests):
        attendance = AttendanceRepository.get_by_id(db, attendance_id, gym_id)
        if not attendance:
            raise HTTPException(404, "Attendance not found")
        subscription = db.query(Subscription).filter(Subscription.id == attendance.subscription_id).first()
        if not subscription:
            raise HTTPException(400, "Subscription linked to this visit is unavailable")
        already = db.query(GuestInvitation).filter(GuestInvitation.attendance_id == attendance.id).count()
        remaining = max(0, (subscription.invitation_limit or 0) - (subscription.invitations_used or 0))
        if len(guests) > remaining:
            raise HTTPException(400, f"Only {remaining} invitations remaining")
        if already:
            raise HTTPException(409, "Guests have already been registered for this visit")
        now = attendance.check_in_time
        try:
            for guest in guests:
                db.add(GuestInvitation(gym_id=gym_id, subscription_id=subscription.id,
                    member_id=attendance.member_id, attendance_id=attendance.id, guest_name=guest.name,
                    guest_phone=guest.phone, guest_age=guest.age, guest_weight=guest.weight,
                    visit_date=now, created_at=datetime.now(timezone.utc)))
            subscription.invitations_used = (subscription.invitations_used or 0) + len(guests)
            db.commit()
            db.refresh(attendance)
            return attendance
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def check_out(db,gym_id,attendance_id):
        obj=AttendanceRepository.get_by_id(db,attendance_id,gym_id)
        if not obj: raise HTTPException(404,"Attendance not found")
        if obj.check_out_time: raise HTTPException(400,"Attendance already checked out")
        obj.check_out_time=datetime.now(timezone.utc); db.commit(); db.refresh(obj); return obj

    @staticmethod
    def list(db,gym_id): return AttendanceRepository.get_all(db,gym_id)
