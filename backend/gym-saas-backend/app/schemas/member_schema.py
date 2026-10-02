from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import date, datetime
class MemberCreate(BaseModel):
    first_name:str
    last_name:str
    email:EmailStr|None=None
    phone:str
    password:str|None=None
    date_of_birth:date|None=None
    gender:str|None=None
    height:float|None=None
    weight:float|None=None
class MemberUpdate(BaseModel): first_name:str|None=None; last_name:str|None=None; email:EmailStr|None=None; phone:str|None=None; date_of_birth:date|None=None; gender:str|None=None; height:float|None=None; weight:float|None=None; status:str|None=None; app_access_enabled:bool|None=None
class MemberResponse(BaseModel):
    id:UUID; gym_id:UUID; app_has_password:bool=False; first_name:str; last_name:str; email:str|None; phone:str; date_of_birth:date|None; gender:str|None; height:float|None; weight:float|None; status:str; app_access_enabled:bool=True; joined_at:datetime; last_visit_at:datetime|None; created_at:datetime; updated_at:datetime
    model_config={"from_attributes":True}
