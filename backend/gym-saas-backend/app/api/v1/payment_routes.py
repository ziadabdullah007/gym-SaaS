from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_role,get_current_gym_id
from app.schemas.payment_schema import PaymentCreate,PaymentResponse
from app.services.payment_service import PaymentService
router=APIRouter(prefix="/api/v1/payments",tags=["Payments"])
@router.post("",response_model=PaymentResponse)
def create(data:PaymentCreate,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return PaymentService.create(db,gym_id,data.model_dump())
@router.get("",response_model=list[PaymentResponse])
def list_pay(db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):return PaymentService.list(db,gym_id)
@router.get("/{payment_id}",response_model=PaymentResponse)
def get(payment_id:UUID,db:Session=Depends(get_db),gym_id=Depends(get_current_gym_id),_=Depends(require_role(["gym_admin","staff"]))):
    obj=PaymentService.get(db,payment_id,gym_id)
    if not obj:raise HTTPException(404,"Payment not found")
    return obj
