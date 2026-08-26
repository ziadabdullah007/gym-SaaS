from pydantic import BaseModel
from uuid import UUID
class PlanCreate(BaseModel): name:str; description:str|None=None; price:float; duration_months:int
class PlanUpdate(BaseModel): name:str|None=None; description:str|None=None; price:float|None=None; duration_months:int|None=None; status:str|None=None
class PlanResponse(BaseModel):
    id:UUID; gym_id:UUID; name:str; description:str|None; price:float; duration_months:int; status:str
    model_config={"from_attributes":True}
