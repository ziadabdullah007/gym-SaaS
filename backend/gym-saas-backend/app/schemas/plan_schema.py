from pydantic import BaseModel, Field
from uuid import UUID

class PlanCreate(BaseModel):
    name:str
    description:str|None=None
    price:float
    duration_months:int = Field(ge=1)
    max_invitations:int = Field(default=0, ge=0)
    max_freeze_days:int = Field(default=0, ge=0)

class PlanUpdate(BaseModel):
    name:str|None=None
    description:str|None=None
    price:float|None=None
    duration_months:int|None=Field(default=None, ge=1)
    max_invitations:int|None=Field(default=None, ge=0)
    max_freeze_days:int|None=Field(default=None, ge=0)
    status:str|None=None

class PlanResponse(BaseModel):
    id:UUID; gym_id:UUID; name:str; description:str|None; price:float; duration_months:int; max_invitations:int; max_freeze_days:int; status:str
    model_config={"from_attributes":True}
