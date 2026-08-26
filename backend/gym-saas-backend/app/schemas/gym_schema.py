from pydantic import BaseModel, EmailStr
from uuid import UUID
class GymProvisionCreate(BaseModel):
    name: str; owner_name: str; email: EmailStr; phone: str | None=None; address: str | None=None
class GymAdminCreate(BaseModel): username: str; first_name: str; last_name: str | None=None
class GymProvisionRequest(BaseModel): gym: GymProvisionCreate; gym_admin: GymAdminCreate
class GymUpdate(BaseModel): name: str|None=None; owner_name: str|None=None; email: EmailStr|None=None; phone: str|None=None; address: str|None=None
class GymResponse(BaseModel):
    id: UUID; name: str; owner_name: str; email: str; phone: str|None; address: str|None; status: str
    model_config={"from_attributes":True}
class SetupTokenResponse(BaseModel): gym: GymResponse; username: str; activation_code: str
