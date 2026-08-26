from fastapi import HTTPException
from app.models.plan import Plan
from app.repositories.plan_repository import PlanRepository
class PlanService:
    @staticmethod
    def create(db,gym_id,data):
        obj=Plan(gym_id=gym_id,status="active",**data); db.add(obj); db.commit(); db.refresh(obj); return obj
    @staticmethod
    def list(db,gym_id): return PlanRepository.get_all(db,gym_id)
    @staticmethod
    def get(db,id,gym_id): return PlanRepository.get_by_id(db,id,gym_id)
    @staticmethod
    def update(db,id,gym_id,data):
        obj=PlanRepository.get_by_id(db,id,gym_id)
        if not obj:return None
        for k,v in data.items():
            if v is not None:setattr(obj,k,v)
        db.commit();db.refresh(obj);return obj
    @staticmethod
    def delete(db,id,gym_id):
        obj=PlanRepository.get_by_id(db,id,gym_id)
        if not obj:return False
        db.delete(obj);db.commit();return True
