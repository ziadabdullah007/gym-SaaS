from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role,get_current_gym_id
from app.schemas.gym_schema import GymResponse,GymUpdate
from app.repositories.gym_repository import GymRepository
from app.services.gym_service import GymService
from app.services.dashboard_service import DashboardService
router=APIRouter(prefix="/api/v1/gym",tags=["Gym"])
@router.get("",response_model=GymResponse)
def get_gym(db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):return GymRepository.get_by_id(db,gym_id)
@router.patch("",response_model=GymResponse)
def update_gym(data:GymUpdate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):return GymService.update(db,gym_id,data.model_dump())
@router.get("/dashboard")
def dashboard(db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin"]))):return DashboardService.gym(db,gym_id)
