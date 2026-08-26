from datetime import datetime,timezone
from fastapi import HTTPException
from app.models.member import Member
from app.repositories.member_repository import MemberRepository
class MemberService:
    @staticmethod
    def create(db,gym_id,data):
        now=datetime.now(timezone.utc); obj=Member(gym_id=gym_id,status="active",joined_at=now,created_at=now,updated_at=now,**data); db.add(obj); db.commit(); db.refresh(obj); return obj
    @staticmethod
    def get_all(db,gym_id): return MemberRepository.get_all(db,gym_id)
    @staticmethod
    def get(db,id,gym_id): return MemberRepository.get_by_id(db,id,gym_id)
    @staticmethod
    def update(db,id,gym_id,data):
        obj=MemberRepository.get_by_id(db,id,gym_id)
        if not obj: return None
        for k,v in data.items():
            if v is not None: setattr(obj,k,v)
        obj.updated_at=datetime.now(timezone.utc); db.commit(); db.refresh(obj); return obj
    @staticmethod
    def delete(db,id,gym_id):
        obj=MemberRepository.get_by_id(db,id,gym_id)
        if not obj:return False
        db.delete(obj); db.commit(); return True
