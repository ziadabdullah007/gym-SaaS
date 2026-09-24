from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
class SubscriptionCreate(BaseModel):
    member_id:UUID; plan_id:UUID; start_date:date; end_date:date; amount:float; auto_renew:bool=False
class SubscriptionUpdate(BaseModel):
    status:str|None=None; end_date:date|None=None; amount:float|None=None; auto_renew:bool|None=None
class SubscriptionResponse(BaseModel):
    id:UUID; member_id:UUID; plan_id:UUID; start_date:date; end_date:date; status:str; amount:float; auto_renew:bool
    invitation_limit:int; invitations_used:int; invitations_remaining:int
    freeze_limit_days:int; freeze_used_days:int; freeze_remaining_days:int
    model_config={"from_attributes":True}
class FreezeCreate(BaseModel):
    days:int=Field(gt=0)
    reason:str|None=None
