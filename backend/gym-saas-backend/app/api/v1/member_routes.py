from uuid import UUID
from pydantic import BaseModel, Field
import hashlib, secrets
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role,get_current_gym_id,get_current_member
from app.schemas.member_schema import MemberCreate,MemberUpdate,MemberResponse
from app.schemas.member_app_schema import MemberAppProfileResponse, MemberAppQrResponse
from app.services.member_service import MemberService
router=APIRouter(prefix="/api/v1/members",tags=["Members"])

class MemberLoginInput(BaseModel):
    username: str
    password: str

class MemberPasswordInput(BaseModel):
    password: str = Field(min_length=8, max_length=128)

class MemberUsernameInput(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9._-]+$")

class MemberPasswordResetInput(BaseModel):
    username: str
    reset_code: str
    new_password: str = Field(min_length=8, max_length=128)
@router.post("",response_model=MemberResponse)
def create(data:MemberCreate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return MemberService.create(db,gym_id,data.model_dump())
@router.post("/app-login")
def member_app_login(data:MemberLoginInput,db:Session=Depends(get_db)):
    return MemberService.authenticate_member(db,data.username,data.password)

@router.get("/me", response_model=MemberAppProfileResponse)
def member_app_me(member=Depends(get_current_member), db:Session=Depends(get_db)):
    """Return only the authenticated member's profile, subscriptions, balances and payments."""
    return MemberService.get_member_app_profile(db, member)

@router.get("/me/entry-qr", response_model=MemberAppQrResponse)
def member_app_entry_qr(member=Depends(get_current_member)):
    """Issue the same signed attendance QR credential used by the existing scanner.

    The token is intentionally short-lived (60 seconds); the Flutter app should
    refresh it once per minute rather than continuously.
    """
    now=datetime.now(timezone.utc)
    expires_at=now+timedelta(seconds=60)
    token=jwt.encode({
        "typ":"gymflow_entry_qr",
        "sub":str(member.id),
        "gym_id":str(member.gym_id),
        "iat":now,
        "exp":expires_at,
    },settings.JWT_SECRET_KEY,algorithm=settings.JWT_ALGORITHM)
    return {"qr_token":token,"expires_in":60}

@router.post("/{member_id}/set-username", response_model=MemberResponse)
def set_username(member_id:UUID,data:MemberUsernameInput,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    return MemberService.set_username(db,member_id,gym_id,data.username)

@router.post("/{member_id}/set-password")
def set_initial_password(member_id:UUID,data:MemberPasswordInput,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    MemberService.set_initial_password(db,member_id,gym_id,data.password)
    return {"message":"Initial member app password set successfully"}

@router.post("/{member_id}/password-reset-code")
def generate_password_reset_code(member_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    return MemberService.generate_password_reset_code(db,member_id,gym_id)

@router.post("/password-reset/complete")
def complete_password_reset(data:MemberPasswordResetInput,db:Session=Depends(get_db)):
    return MemberService.reset_password(db,data.username,data.reset_code,data.new_password)

@router.post("/{member_id}/entry-qr")
def issue_entry_qr(member_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    """Issue a short-lived signed QR token. Clients refresh it every 60 seconds."""
    obj=MemberService.get(db,member_id,gym_id)
    if not obj: raise HTTPException(404,"Member not found")
    if not obj.app_access_enabled: raise HTTPException(403,"Member App access is disabled")
    now=datetime.now(timezone.utc)
    token=jwt.encode({"typ":"gymflow_entry_qr","sub":str(obj.id),"gym_id":str(gym_id),
        "iat":now,"exp":now+timedelta(seconds=60)},settings.JWT_SECRET_KEY,algorithm=settings.JWT_ALGORITHM)
    return {"member_id":str(obj.id),"qr_token":token,"expires_at":(now+timedelta(seconds=60)).isoformat(),"expires_in":60}

@router.get("",response_model=list[MemberResponse])
def list_members(db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return MemberService.get_all(db,gym_id)
@router.get("/{member_id}",response_model=MemberResponse)
def get(member_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    obj=MemberService.get(db,member_id,gym_id)
    if not obj:raise HTTPException(404,"Member not found")
    return obj
@router.patch("/{member_id}",response_model=MemberResponse)
def update(member_id:UUID,data:MemberUpdate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    obj=MemberService.update(db,member_id,gym_id,data.model_dump())
    if not obj:raise HTTPException(404,"Member not found")
    return obj
@router.delete("/{member_id}")
def delete(member_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):
    if not MemberService.delete(db,member_id,gym_id):raise HTTPException(404,"Member not found")
    return {"message":"Member deleted successfully"}
