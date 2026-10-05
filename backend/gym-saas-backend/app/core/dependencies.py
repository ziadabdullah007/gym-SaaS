from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User
from app.models.member import Member
from app.repositories.user_repository import UserRepository
from app.repositories.gym_repository import GymRepository
from app.repositories.staff_repository import StaffRepository

security = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = UserRepository.get_by_id(db, user_id)
    if not user or user.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is disabled or unavailable")
    return user


def get_current_gym_id(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UUID:
    if current_user.role == "saas_admin":
        raise HTTPException(status_code=403, detail="SaaS Admin has no gym context")
    if current_user.role == "gym_admin":
        gym = GymRepository.get_by_admin_user_id(db, current_user.id)
        if not gym:
            raise HTTPException(status_code=403, detail="No gym is assigned to this user")
        return gym.id
    staff = StaffRepository.get_by_user_id(db, current_user.id)
    if not staff:
        raise HTTPException(status_code=403, detail="No gym is assigned to this staff user")
    return staff.gym_id


def require_role(allowed_roles: list[str]):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return checker


def require_gym_access(resource_gym_id: UUID, current_gym_id: UUID) -> None:
    if resource_gym_id != current_gym_id:
        raise HTTPException(status_code=404, detail="Resource not found")


def get_current_member(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Member:
    """Authenticate a Member App token and return only that member."""
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
        role = payload.get("role")
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired member token")

    if role != "member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Member access required")

    member = db.query(Member).filter(Member.id == user_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Member account not found")
    if not member.app_access_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Member App access is disabled")
    if not member.gym_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Member has no valid gym association")
    return member
