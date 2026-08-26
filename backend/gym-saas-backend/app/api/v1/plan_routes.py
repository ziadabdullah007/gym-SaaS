from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role,get_current_gym_id
from app.schemas.plan_schema import PlanCreate,PlanUpdate,PlanResponse
from app.services.plan_service import PlanService
router=APIRouter(prefix="/api/v1/plans",tags=["Plans"])
@router.post("",response_model=PlanResponse)
def create(data:PlanCreate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):return PlanService.create(db,gym_id,data.model_dump())
@router.get("",response_model=list[PlanResponse])
def list_plans(db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return PlanService.list(db,gym_id)
@router.get("/{plan_id}",response_model=PlanResponse)
def get(plan_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    obj=PlanService.get(db,plan_id,gym_id)
    if not obj:raise HTTPException(404,"Plan not found")
    return obj
@router.patch("/{plan_id}",response_model=PlanResponse)
def update(plan_id:UUID,data:PlanUpdate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):
    obj=PlanService.update(db,plan_id,gym_id,data.model_dump())
    if not obj:raise HTTPException(404,"Plan not found")
    return obj
@router.delete("/{plan_id}")
def delete(plan_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):
    if not PlanService.delete(db,plan_id,gym_id):raise HTTPException(404,"Plan not found")
    return {"message":"Plan deleted successfully"}
