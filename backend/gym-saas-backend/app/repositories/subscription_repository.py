from uuid import UUID
from app.models.subscription import Subscription
class SubscriptionRepository:
    @staticmethod
    def get_all(db, gym_id): return db.query(Subscription).join(Subscription.member).filter(Subscription.member.has(gym_id=gym_id)).all()
    @staticmethod
    def get_by_id(db, sub_id: UUID, gym_id): return db.query(Subscription).join(Subscription.member).filter(Subscription.id==sub_id, Subscription.member.has(gym_id=gym_id)).first()
    @staticmethod
    def create(db,obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def update(db,obj): db.add(obj); db.flush(); return obj
