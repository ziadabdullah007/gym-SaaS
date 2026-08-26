from uuid import UUID
from app.models.saas_plan import SaaSPlan
from app.models.gym_subscription import GymSubscription
class SaaSRepository:
    @staticmethod
    def plans(db): return db.query(SaaSPlan).all()
    @staticmethod
    def plan(db, plan_id: UUID): return db.query(SaaSPlan).filter(SaaSPlan.id==plan_id).first()
    @staticmethod
    def create_plan(db,obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def update_plan(db,obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def subscriptions(db): return db.query(GymSubscription).all()
    @staticmethod
    def subscription(db, sub_id: UUID): return db.query(GymSubscription).filter(GymSubscription.id==sub_id).first()
    @staticmethod
    def create_subscription(db,obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def update_subscription(db,obj): db.add(obj); db.flush(); return obj
