from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role,get_current_gym_id
from app.schemas.subscription_schema import SubscriptionCreate,SubscriptionUpdate,SubscriptionResponse
from app.services.subscription_service import SubscriptionService
router=APIRouter(prefix="/api/v1/subscriptions",tags=["Subscriptions"])
@router.post("",response_model=SubscriptionResponse)
def create(data:SubscriptionCreate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return SubscriptionService.create(db,gym_id,data.model_dump())
@router.get("",response_model=list[SubscriptionResponse])
def list_sub(db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return SubscriptionService.list(db,gym_id)
@router.get("/{subscription_id}",response_model=SubscriptionResponse)
def get(subscription_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    obj=SubscriptionService.get(db,subscription_id,gym_id)
    if not obj:raise HTTPException(404,"Subscription not found")
    return obj
@router.patch("/{subscription_id}",response_model=SubscriptionResponse)
def update(subscription_id:UUID,data:SubscriptionUpdate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):
    obj=SubscriptionService.update(db,subscription_id,gym_id,data.model_dump())
    if not obj:raise HTTPException(404,"Subscription not found")
    return obj
