from datetime import date, timedelta
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.models.gym import Gym
from app.models.member import Member
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.attendance import Attendance
from app.models.gym_subscription import GymSubscription
from app.models.saas_plan import SaaSPlan
class DashboardService:
    @staticmethod
    def saas(db):
        return {"total_gyms":db.query(func.count(Gym.id)).scalar(),"active_gyms":db.query(func.count(Gym.id)).filter(Gym.status=="active").scalar(),"saas_subscriptions":db.query(func.count(GymSubscription.id)).scalar(),"saas_revenue":float(db.query(func.coalesce(func.sum(SaaSPlan.price),0)).join(GymSubscription, GymSubscription.saas_plan_id==SaaSPlan.id).scalar() or 0),"plan_distribution":[{"plan":n,"count":c} for n,c in db.query(SaaSPlan.name,func.count(GymSubscription.id)).outerjoin(GymSubscription).group_by(SaaSPlan.name).all()],"recent_subscriptions":[{"id":str(s.id),"gym_id":str(s.gym_id),"saas_plan_id":str(s.saas_plan_id),"status":s.status} for s in db.query(GymSubscription).order_by(GymSubscription.start_date.desc()).limit(10).all()]}
    @staticmethod
    def _gym_base(db, gym_id):
        today = date.today()
        active_sub = (Subscription.status == "active") & (Subscription.start_date <= today) & (Subscription.end_date >= today)
        active_rows = (db.query(Subscription)
            .options(joinedload(Subscription.payments), joinedload(Subscription.member), joinedload(Subscription.plan))
            .filter(Subscription.member.has(Member.gym_id == gym_id), active_sub).all())

        outstanding_balance = 0.0
        outstanding_members = 0
        overdue_members = 0
        payment_status = {"paid": 0, "partially_paid": 0, "overdue": 0, "unpaid": 0}
        plan_counts = {}
        for sub in active_rows:
            status = sub.payment_status
            payment_status[status] = payment_status.get(status, 0) + 1
            plan_counts[sub.plan_name or "Unknown"] = plan_counts.get(sub.plan_name or "Unknown", 0) + 1
            remaining = sub.remaining_amount
            if remaining > 0.009:
                outstanding_balance += remaining
                outstanding_members += 1
                if status == "overdue":
                    overdue_members += 1

        revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).join(Subscription).filter(
            Payment.subscription.has(Subscription.member.has(Member.gym_id == gym_id)),
            Payment.status == "completed"
        ).scalar()

        # Last 6 calendar months of collected payments.
        monthly_revenue = []
        for offset in range(5, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=offset * 31)).replace(day=1)
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            value = db.query(func.coalesce(func.sum(Payment.amount), 0)).join(Subscription).filter(
                Payment.subscription.has(Subscription.member.has(Member.gym_id == gym_id)),
                Payment.status == "completed",
                Payment.payment_date >= month_start,
                Payment.payment_date < next_month,
            ).scalar()
            monthly_revenue.append({"label": month_start.strftime("%b"), "value": round(float(value or 0), 2)})

        # Last 7 days of check-ins.
        attendance_7d = []
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            count = db.query(func.count(Attendance.id)).filter(
                Attendance.member.has(Member.gym_id == gym_id),
                func.date(Attendance.check_in_time) == day,
            ).scalar()
            attendance_7d.append({"label": day.strftime("%a"), "date": day.isoformat(), "value": int(count or 0)})

        expiring_rows = (db.query(Subscription)
            .options(joinedload(Subscription.member), joinedload(Subscription.plan))
            .filter(Subscription.member.has(Member.gym_id == gym_id), active_sub,
                    Subscription.end_date <= today + timedelta(days=7))
            .order_by(Subscription.end_date.asc()).limit(6).all())
        expiring = [{
            "member": f"{x.member.first_name} {x.member.last_name}".strip(),
            "plan": x.plan_name or "—",
            "end_date": x.end_date.isoformat(),
            "days_left": max(0, (x.end_date - today).days),
        } for x in expiring_rows]

        recent_payments = (db.query(Payment)
            .options(joinedload(Payment.subscription).joinedload(Subscription.member), joinedload(Payment.subscription).joinedload(Subscription.plan))
            .join(Payment.subscription).filter(Subscription.member.has(Member.gym_id == gym_id), Payment.status == "completed")
            .order_by(Payment.payment_date.desc()).limit(8).all())
        recent = [{
            "member": f"{x.subscription.member.first_name} {x.subscription.member.last_name}".strip(),
            "amount": float(x.amount or 0),
            "method": x.payment_method,
            "date": x.payment_date.isoformat() if x.payment_date else None,
            "plan": x.subscription.plan_name or "—",
        } for x in recent_payments]

        return {
            "gym_id": str(gym_id),
            "total_members": db.query(func.count(Member.id)).filter(Member.gym_id == gym_id).scalar(),
            "active_members": db.query(func.count(Member.id)).filter(Member.gym_id == gym_id, Member.status == "active").scalar(),
            "active_subscriptions": len(active_rows),
            "revenue": float(revenue or 0),
            "subscription_value": float(sum(float(s.amount or 0) for s in active_rows)),
            "outstanding_balance": round(outstanding_balance, 2),
            "outstanding_payment_members": outstanding_members,
            "overdue_payment_members": overdue_members,
            "payments": db.query(func.count(Payment.id)).filter(Payment.subscription.has(Subscription.member.has(Member.gym_id == gym_id))).scalar(),
            "attendance": db.query(func.count(Attendance.id)).filter(Attendance.member.has(Member.gym_id == gym_id)).scalar(),
            "expiring_subscriptions": db.query(func.count(Subscription.id)).filter(Subscription.member.has(Member.gym_id == gym_id), Subscription.end_date <= today + timedelta(days=7), Subscription.end_date >= today, Subscription.status == "active", Subscription.start_date <= today).scalar(),
            "payment_status": [{"status": k, "count": v} for k, v in payment_status.items()],
            "plan_distribution": [{"plan": k, "count": v} for k, v in sorted(plan_counts.items(), key=lambda x: (-x[1], x[0]))],
            "monthly_revenue": monthly_revenue,
            "attendance_7d": attendance_7d,
            "expiring_members": expiring,
            "recent_payments": recent,
        }

    @staticmethod
    def gym(db, gym_id):
        return DashboardService._gym_base(db, gym_id)

    @staticmethod
    def staff(db, gym_id):
        data = DashboardService._gym_base(db, gym_id)
        data.update({
            "todays_checkins": db.query(func.count(Attendance.id)).filter(
                Attendance.member.has(Member.gym_id == gym_id),
                func.date(Attendance.check_in_time) == date.today()
            ).scalar(),
            "recent_activity": [{
                "id": str(a.id),
                "member": f"{a.member.first_name} {a.member.last_name}".strip(),
                "check_in_time": a.check_in_time.isoformat() if a.check_in_time else None,
                "check_out_time": a.check_out_time.isoformat() if a.check_out_time else None,
                "guest_count": a.guest_count,
            } for a in db.query(Attendance).options(joinedload(Attendance.member), joinedload(Attendance.guest_invitations))
                .join(Attendance.member).filter(Member.gym_id == gym_id)
                .order_by(Attendance.check_in_time.desc()).limit(10).all()]
        })
        return data
