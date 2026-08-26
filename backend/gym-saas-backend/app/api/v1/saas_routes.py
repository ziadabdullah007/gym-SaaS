from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role
from app.schemas.gym_schema import GymProvisionRequest,GymResponse,SetupTokenResponse
from app.schemas.saas_plan_schema import *
from app.services.saas_service import SaaSService
from app.services.dashboard_service import DashboardService
from app.repositories.gym_repository import GymRepository
from app.repositories.saas_repository import SaaSRepository
from app.models.gym_subscription import GymSubscription
from datetime import datetime,timezone
router=APIRouter(prefix="/api/v1/saas",tags=["SaaS"])
@router.get("/dashboard")
def dashboard(db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):return DashboardService.saas(db)
@router.post("/gyms",response_model=SetupTokenResponse)
def create_gym(data:GymProvisionRequest,db:Session=Depends(get_db),u=Depends(require_role(["saas_admin"]))):
    gym,admin,activation_code=SaaSService.create_gym(db,data.model_dump(),u.id);return {"gym":gym,"username":admin.username,"activation_code":activation_code}
@router.get("/gyms",response_model=list[GymResponse])
def gyms(db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):return GymRepository.get_all(db)
@router.get("/gyms/{gym_id}",response_model=GymResponse)
def gym(gym_id:UUID,db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):return GymRepository.get_by_id(db,gym_id) or (_ for _ in ()).throw(HTTPException(404,"Gym not found"))
@router.patch("/gyms/{gym_id}",response_model=GymResponse)
def update_gym(gym_id:UUID,data:dict,db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):
    obj=GymRepository.get_by_id(db,gym_id)
    if not obj:raise HTTPException(404,"Gym not found")
    for k,v in data.items():
        if k not in {"id","gym_admin_user_id","created_at","updated_at"} and v is not None:setattr(obj,k,v)
    obj.updated_at=datetime.now(timezone.utc);db.commit();db.refresh(obj);return obj
@router.delete("/gyms/{gym_id}")
def delete_gym(gym_id:UUID,db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):
    obj=GymRepository.get_by_id(db,gym_id)
    if not obj:raise HTTPException(404,"Gym not found")
    obj.status="disabled";db.commit();return {"message":"Gym disabled"}
@router.post("/plans",response_model=SaaSPlanResponse)
def create_plan(data:SaaSPlanCreate,db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):return SaaSService.create_saas_plan(db,data.model_dump())
@router.get("/plans",response_model=list[SaaSPlanResponse])
def plans(db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):return SaaSRepository.plans(db)
@router.patch("/plans/{plan_id}",response_model=SaaSPlanResponse)
def update_plan(plan_id:UUID,data:SaaSPlanUpdate,db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):
    obj=SaaSRepository.plan(db,plan_id)
    if not obj:raise HTTPException(404,"SaaS plan not found")
    return SaaSService.update_saas_plan(db,obj,data.model_dump())
@router.post("/gym-subscriptions",response_model=GymSubscriptionResponse)
def create_gym_sub(data:GymSubscriptionCreate,db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):return SaaSService.create_gym_subscription(db,data.model_dump())
@router.get("/gym-subscriptions",response_model=list[GymSubscriptionResponse])
def gym_subs(db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):return SaaSRepository.subscriptions(db)
@router.patch("/gym-subscriptions/{sub_id}",response_model=GymSubscriptionResponse)
def update_gym_sub(sub_id:UUID,data:GymSubscriptionUpdate,db:Session=Depends(get_db),_=Depends(require_role(["saas_admin"]))):
    obj=SaaSRepository.subscription(db,sub_id)
    if not obj:raise HTTPException(404,"Gym subscription not found")
    for k,v in data.model_dump().items():
        if v is not None:setattr(obj,k,v)
    db.commit();db.refresh(obj);return obj
