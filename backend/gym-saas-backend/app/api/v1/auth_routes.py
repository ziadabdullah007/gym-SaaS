from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth_schema import (
    LoginRequest, ActivationVerifyRequest, ActivationVerifyResponse,
    SetupPasswordRequest, LoginResponse, SetupPasswordResponse, UserResponse
)
from app.services.auth_service import AuthService
router=APIRouter(prefix="/api/v1/auth",tags=["Auth"])
@router.post("/login",response_model=LoginResponse)
def login(data:LoginRequest,db:Session=Depends(get_db)):
    token,user,gym_id=AuthService.login(db,data.username,data.password)
    return {"access_token":token,"user":{"id":user.id,"username":user.username,"role":user.role,"status":user.status,"first_name":user.first_name,"last_name":user.last_name,"gym_id":gym_id}}
@router.post("/verify-activation",response_model=ActivationVerifyResponse)
def verify_activation(data:ActivationVerifyRequest,db:Session=Depends(get_db)):
    user=AuthService.verify_activation(db,data.username,data.activation_code)
    return {"valid":True,"username":user.username}

@router.post("/setup-password",response_model=SetupPasswordResponse)
def setup(data:SetupPasswordRequest,db:Session=Depends(get_db)):
    AuthService.setup_password(db,data.username,data.activation_code,data.password)
    return {"message":"Account activated successfully"}
@router.get("/me",response_model=UserResponse)
def me(current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    gym_id=None
    if current_user.role=="gym_admin":
        from app.repositories.gym_repository import GymRepository; g=GymRepository.get_by_admin_user_id(db,current_user.id);gym_id=g.id if g else None
    elif current_user.role=="staff":
        from app.repositories.staff_repository import StaffRepository;s=StaffRepository.get_by_user_id(db,current_user.id);gym_id=s.gym_id if s else None
    return {"id":current_user.id,"username":current_user.username,"role":current_user.role,"status":current_user.status,"first_name":current_user.first_name,"last_name":current_user.last_name,"gym_id":gym_id}
@router.post("/logout")
def logout(current_user=Depends(get_current_user)): return {"message":"Logout successful. Discard the JWT on the client."}
