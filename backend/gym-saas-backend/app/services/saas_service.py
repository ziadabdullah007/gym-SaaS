import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.models.gym import Gym
from app.models.user import User
from app.models.saas_plan import SaaSPlan
from app.models.gym_subscription import GymSubscription
from app.core.security import generate_activation_code
from app.repositories.gym_repository import GymRepository
from app.repositories.user_repository import UserRepository
from app.repositories.saas_repository import SaaSRepository

class SaaSService:
    @staticmethod
    def create_gym(db, data, creator_id):
        now=datetime.now(timezone.utc)
        if UserRepository.get_by_username(db,data["gym_admin"]["username"]): raise HTTPException(409,"Username already exists")
        activation_code, token_hash=generate_activation_code()
        admin=User(id=uuid.uuid4(),username=data["gym_admin"]["username"],password_hash=None,role="gym_admin",status="pending_password",first_name=data["gym_admin"]["first_name"],last_name=data["gym_admin"].get("last_name"),setup_token_hash=token_hash,setup_expires_at=now+timedelta(hours=24),created_by_user_id=creator_id,created_at=now,updated_at=now)
        db.add(admin); db.flush()
        gdata=data["gym"]
        gym=Gym(id=uuid.uuid4(),gym_admin_user_id=admin.id,name=gdata["name"],owner_name=gdata["owner_name"],email=gdata["email"],phone=gdata.get("phone"),address=gdata.get("address"),status="active",created_at=now,updated_at=now)
        db.add(gym); db.commit(); db.refresh(gym)
        return gym,admin,activation_code

    @staticmethod
    def create_saas_plan(db,data):
        now=datetime.now(timezone.utc); obj=SaaSPlan(id=uuid.uuid4(),created_at=now,updated_at=now,**data); db.add(obj); db.commit(); db.refresh(obj); return obj

    @staticmethod
    def update_saas_plan(db,obj,data):
        for k,v in data.items():
            if v is not None: setattr(obj,k,v)
        obj.updated_at=datetime.now(timezone.utc); db.commit(); db.refresh(obj); return obj

    @staticmethod
    def create_gym_subscription(db,data):
        if not GymRepository.get_by_id(db,data["gym_id"]): raise HTTPException(404,"Gym not found")
        if not SaaSRepository.plan(db,data["saas_plan_id"]): raise HTTPException(404,"SaaS plan not found")
        obj=GymSubscription(id=uuid.uuid4(),status="active",**data); db.add(obj); db.commit(); db.refresh(obj); return obj
