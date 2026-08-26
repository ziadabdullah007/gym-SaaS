from pydantic import BaseModel
from uuid import UUID
from datetime import date
class SaaSPlanCreate(BaseModel): name:str; description:str|None=None; price:float; max_members_per_gym:int|None=None
class SaaSPlanUpdate(BaseModel): name:str|None=None; description:str|None=None; price:float|None=None; max_members_per_gym:int|None=None
class SaaSPlanResponse(BaseModel):
    id:UUID; name:str; description:str|None; price:float; max_members_per_gym:int|None
    model_config={"from_attributes":True}
class GymSubscriptionCreate(BaseModel): gym_id:UUID; saas_plan_id:UUID; start_date:date; end_date:date
class GymSubscriptionUpdate(BaseModel): saas_plan_id:UUID|None=None; start_date:date|None=None; end_date:date|None=None; status:str|None=None
class GymSubscriptionResponse(BaseModel):
    id:UUID; gym_id:UUID; saas_plan_id:UUID; start_date:date; end_date:date; status:str
    model_config={"from_attributes":True}
