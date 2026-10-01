from uuid import UUID
import hashlib, secrets, base64, hmac, struct
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role,get_current_gym_id
from app.schemas.member_schema import MemberCreate,MemberUpdate,MemberResponse
from app.services.member_service import MemberService
router=APIRouter(prefix="/api/v1/members",tags=["Members"])
@router.post("",response_model=MemberResponse)
def create(data:MemberCreate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return MemberService.create(db,gym_id,data.model_dump())
@router.post("/{member_id}/entry-qr")
def issue_entry_qr(member_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    """Issue a short-lived signed QR token. Clients refresh it every 60 seconds."""
    obj=MemberService.get(db,member_id,gym_id)
    if not obj: raise HTTPException(404,"Member not found")
    if not obj.app_access_enabled: raise HTTPException(403,"Member App access is disabled")
    now=datetime.now(timezone.utc)
    expires_at=now+timedelta(seconds=60)
    # Compact, signed token keeps the QR visually less dense than a full JWT.
    payload=obj.id.bytes + UUID(str(gym_id)).bytes + struct.pack("!I", int(expires_at.timestamp()))
    signature=hmac.new(settings.JWT_SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).digest()[:16]
    token="GF1."+base64.urlsafe_b64encode(payload+signature).decode("ascii").rstrip("=")
    return {"member_id":str(obj.id),"qr_token":token,"expires_at":expires_at.isoformat(),"expires_in":60}

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
