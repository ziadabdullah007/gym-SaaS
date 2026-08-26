from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role,get_current_gym_id
from app.schemas.attendance_schema import AttendanceCheckIn,AttendanceResponse
from app.services.attendance_service import AttendanceService
router=APIRouter(prefix="/api/v1/attendance",tags=["Attendance"])
@router.post("/check-in",response_model=AttendanceResponse)
def check_in(data:AttendanceCheckIn,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return AttendanceService.check_in(db,gym_id,data.member_id)
@router.post("/{attendance_id}/check-out",response_model=AttendanceResponse)
def check_out(attendance_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return AttendanceService.check_out(db,gym_id,attendance_id)
@router.get("",response_model=list[AttendanceResponse])
def list_att(db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return AttendanceService.list(db,gym_id)
