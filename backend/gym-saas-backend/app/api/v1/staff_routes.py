from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role,get_current_gym_id
from app.schemas.staff_schema import StaffCreate,StaffUpdate,StaffResponse,StaffProvisionResponse
from app.services.staff_service import StaffService
from app.repositories.staff_repository import StaffRepository
from app.repositories.user_repository import UserRepository
from app.services.dashboard_service import DashboardService
router=APIRouter(prefix="/api/v1/staff",tags=["Staff"])
@router.post("",response_model=StaffProvisionResponse)
def create(data:StaffCreate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),u=Depends(require_role(["gym_admin"]))):
    obj,activation_code=StaffService.create(db,gym_id,data.model_dump(),u.id); user=UserRepository.get_by_id(db,obj.user_id); return {"staff":obj,"username":user.username,"activation_code":activation_code}
@router.get("",response_model=list[StaffResponse])
def list_staff(db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):return StaffRepository.get_all(db,gym_id)
@router.get("/dashboard")
def staff_dashboard(db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["staff"]))):return DashboardService.staff(db,gym_id)
@router.get("/{staff_id}",response_model=StaffResponse)
def get_staff(staff_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):
    obj=StaffRepository.get_by_id(db,staff_id)
    if not obj or obj.gym_id!=gym_id:raise HTTPException(404,"Staff not found")
    return obj
@router.patch("/{staff_id}",response_model=StaffResponse)
def update(staff_id:UUID,data:StaffUpdate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):
    obj=StaffRepository.get_by_id(db,staff_id)
    if not obj or obj.gym_id!=gym_id:raise HTTPException(404,"Staff not found")
    vals=data.model_dump(); user=UserRepository.get_by_id(db,obj.user_id)
    for k in ("position","status"):
        if vals.get(k) is not None:setattr(obj,k,vals[k])
    if vals.get("first_name") is not None:user.first_name=vals["first_name"]
    if vals.get("last_name") is not None:user.last_name=vals["last_name"]
    if obj.status=="disabled":user.status="disabled"
    db.commit();db.refresh(obj);return obj
@router.delete("/{staff_id}")
def delete(staff_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):
    obj=StaffRepository.get_by_id(db,staff_id)
    if not obj or obj.gym_id!=gym_id:raise HTTPException(404,"Staff not found")
    obj.status="disabled";user=UserRepository.get_by_id(db,obj.user_id);user.status="disabled";db.commit();return {"message":"Staff disabled"}
