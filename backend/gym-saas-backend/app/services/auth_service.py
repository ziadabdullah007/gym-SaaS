from datetime import datetime, timedelta, timezone
from app.core.security import hash_password, verify_password, create_access_token, generate_setup_token
from app.repositories.user_repository import UserRepository
from app.repositories.gym_repository import GymRepository
from app.repositories.staff_repository import StaffRepository
from fastapi import HTTPException

class AuthService:
    @staticmethod
    def login(db, username, password):
        user=UserRepository.get_by_username(db, username)
        if not user or user.status != "active" or not user.password_hash or not verify_password(password,user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        gym_id=None
        if user.role == "gym_admin":
            gym=GymRepository.get_by_admin_user_id(db,user.id); gym_id=gym.id if gym else None
        elif user.role == "staff":
            staff=StaffRepository.get_by_user_id(db,user.id); gym_id=staff.gym_id if staff else None
        if user.role != "saas_admin" and gym_id is None: raise HTTPException(status_code=403, detail="User has no gym context")
        user.last_login_at=datetime.now(timezone.utc); db.commit(); db.refresh(user)
        return create_access_token(user.id,user.role,gym_id),user,gym_id

    @staticmethod
    def verify_activation(db, username, activation_code):
        user=UserRepository.get_by_username(db, username)
        if (not user or user.status != "pending_password" or not user.setup_token_hash
                or not user.setup_expires_at or user.setup_expires_at < datetime.now(timezone.utc)
                or not verify_password(activation_code, user.setup_token_hash)):
            raise HTTPException(status_code=400, detail="Invalid or expired activation code")
        return user

    @staticmethod
    def setup_password(db, username, activation_code, password):
        user=AuthService.verify_activation(db, username, activation_code)
        user.password_hash=hash_password(password)
        user.status="active"
        user.setup_token_hash=None
        user.setup_expires_at=None
        user.updated_at=datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        return user
