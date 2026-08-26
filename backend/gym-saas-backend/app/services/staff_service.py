import uuid
from datetime import datetime,timedelta,timezone
from fastapi import HTTPException
from app.models.staff import Staff
from app.models.user import User
from app.core.security import generate_activation_code
from app.repositories.user_repository import UserRepository
from app.repositories.staff_repository import StaffRepository
class StaffService:
    @staticmethod
    def create(db,gym_id,data,creator_id):
        if UserRepository.get_by_username(db,data["username"]): raise HTTPException(409,"Username already exists")
        now=datetime.now(timezone.utc); activation_code,token_hash=generate_activation_code()
        user=User(id=uuid.uuid4(),username=data["username"],role="staff",status="pending_password",first_name=data["first_name"],last_name=data.get("last_name"),setup_token_hash=token_hash,setup_expires_at=now+timedelta(hours=24),created_by_user_id=creator_id,created_at=now,updated_at=now)
        db.add(user); db.flush(); staff=Staff(id=uuid.uuid4(),gym_id=gym_id,user_id=user.id,position=data["position"],status="active",created_at=now); db.add(staff); db.commit(); db.refresh(staff); return staff,activation_code
