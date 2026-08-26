from uuid import UUID
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.member import Member
class PaymentRepository:
    @staticmethod
    def get_all(db, gym_id):
        return db.query(Payment).filter(Payment.subscription.has(Subscription.member.has(Member.gym_id == gym_id))).all()
    @staticmethod
    def get_by_id(db, payment_id: UUID, gym_id):
        return db.query(Payment).filter(Payment.id == payment_id, Payment.subscription.has(Subscription.member.has(Member.gym_id == gym_id))).first()
    @staticmethod
    def create(db,obj): db.add(obj); db.flush(); return obj
