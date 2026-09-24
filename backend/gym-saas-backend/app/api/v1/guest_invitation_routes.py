from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role,get_current_gym_id
from app.schemas.guest_invitation_schema import GuestInvitationResponse
from app.services.guest_invitation_service import GuestInvitationService
router=APIRouter(prefix="/api/v1/guest-invitations",tags=["Guest Invitations"])
@router.get("",response_model=list[GuestInvitationResponse])
def list_guests(db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    return GuestInvitationService.list(db,gym_id)
