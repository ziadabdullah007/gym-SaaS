from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
class GuestInput(BaseModel):
    name:str=Field(min_length=1,max_length=255)
    phone:str=Field(min_length=1,max_length=50)
    age:int|None=Field(default=None,ge=1,le=120)
    weight:float|None=Field(default=None,ge=0,le=500)
class AttendanceCheckIn(BaseModel):
    member_id:UUID
    guests:list[GuestInput]=Field(default_factory=list)
class AttendanceResponse(BaseModel):
    id:UUID; member_id:UUID; check_in_time:datetime; check_out_time:datetime|None; created_at:datetime
    guest_count:int=0
    model_config={"from_attributes":True}
