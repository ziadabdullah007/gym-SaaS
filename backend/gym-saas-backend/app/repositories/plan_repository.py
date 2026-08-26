from uuid import UUID
from app.models.plan import Plan
class PlanRepository:
    @staticmethod
    def get_all(db, gym_id): return db.query(Plan).filter(Plan.gym_id==gym_id).all()
    @staticmethod
    def get_by_id(db, plan_id: UUID, gym_id): return db.query(Plan).filter(Plan.id==plan_id, Plan.gym_id==gym_id).first()
    @staticmethod
    def create(db,obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def update(db,obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def delete(db,obj): db.delete(obj); db.flush()
