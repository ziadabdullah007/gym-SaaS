from uuid import UUID
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role,get_current_gym_id
from app.schemas.body_measurement_schema import BodyMeasurementCreate,BodyMeasurementUpdate,BodyMeasurementResponse
from app.services.body_measurement_service import BodyMeasurementService
router=APIRouter(prefix="/api/v1/members",tags=["Measurements"])
@router.post("/{member_id}/measurements",response_model=BodyMeasurementResponse)
def create(member_id:UUID,data:BodyMeasurementCreate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return BodyMeasurementService.create(db,gym_id,member_id,data.model_dump())
@router.get("/{member_id}/measurements",response_model=list[BodyMeasurementResponse])
def list_measurements(member_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return BodyMeasurementService.list(db,gym_id,member_id)

@router.patch("/{member_id}/measurements/{measurement_id}",response_model=BodyMeasurementResponse)
def update(member_id:UUID,measurement_id:UUID,data:BodyMeasurementUpdate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    return BodyMeasurementService.update(db,gym_id,member_id,measurement_id,data.model_dump(exclude_unset=True))
