from datetime import date, timedelta
from sqlalchemy import func
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
    def gym(db,gym_id):
        active_sub=Subscription.status=="active"
        revenue=db.query(func.coalesce(func.sum(Payment.amount),0)).join(Subscription).filter(Payment.subscription.has(Subscription.member.has(Member.gym_id==gym_id))).scalar()
        return {"gym_id":str(gym_id),"total_members":db.query(func.count(Member.id)).filter(Member.gym_id==gym_id).scalar(),"active_members":db.query(func.count(Member.id)).filter(Member.gym_id==gym_id,Member.status=="active").scalar(),"active_subscriptions":db.query(func.count(Subscription.id)).filter(Subscription.member.has(Member.gym_id==gym_id),active_sub).scalar(),"revenue":float(revenue or 0),"subscription_value":float(db.query(func.coalesce(func.sum(Subscription.amount),0)).filter(Subscription.member.has(Member.gym_id==gym_id),Subscription.status=="active").scalar() or 0),"payments":db.query(func.count(Payment.id)).filter(Payment.subscription.has(Subscription.member.has(Member.gym_id==gym_id))).scalar(),"attendance":db.query(func.count(Attendance.id)).filter(Attendance.member.has(Member.gym_id==gym_id)).scalar(),"expiring_subscriptions":db.query(func.count(Subscription.id)).filter(Subscription.member.has(Member.gym_id==gym_id),Subscription.end_date<=date.today()+timedelta(days=7),Subscription.end_date>=date.today(),Subscription.status=="active").scalar()}
    @staticmethod
    def staff(db,gym_id):
        return {"gym_id":str(gym_id),"todays_checkins":db.query(func.count(Attendance.id)).filter(Attendance.member.has(Member.gym_id==gym_id),func.date(Attendance.check_in_time)==date.today()).scalar(),"active_members":db.query(func.count(Member.id)).filter(Member.gym_id==gym_id,Member.status=="active").scalar(),"expiring_subscriptions":db.query(func.count(Subscription.id)).filter(Subscription.member.has(Member.gym_id==gym_id),Subscription.end_date<=date.today()+timedelta(days=7),Subscription.end_date>=date.today(),Subscription.status=="active").scalar(),"recent_activity":[{"id":str(a.id),"member_id":str(a.member_id),"check_in_time":a.check_in_time,"check_out_time":a.check_out_time} for a in db.query(Attendance).join(Attendance.member).filter(Member.gym_id==gym_id).order_by(Attendance.check_in_time.desc()).limit(10).all()]}
