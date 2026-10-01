from uuid import UUID
import hashlib, secrets
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
    """Rotate the member's entry QR credential. Return the raw token only once."""
    obj=MemberService.get(db,member_id,gym_id)
    if not obj: raise HTTPException(404,"Member not found")
    if not obj.app_access_enabled: raise HTTPException(403,"Member App access is disabled")
    token=secrets.token_urlsafe(32)
    obj.entry_qr_token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest()
    db.commit()
    return {"member_id":str(obj.id),"qr_token":token,"message":"Store this token in the member app and encode it as the entry QR. It will not be shown again; issuing a new token revokes the previous one."}

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
