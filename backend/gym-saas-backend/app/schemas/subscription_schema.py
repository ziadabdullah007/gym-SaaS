from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date

class SubscriptionCreate(BaseModel):
    member_id:UUID
    plan_id:UUID
    start_date:date
    end_date:date
    amount:float = Field(gt=0)
    initial_payment_amount:float = Field(gt=0)
    initial_payment_method:str = "cash"
    payment_due_date:date|None=None
    auto_renew:bool=False

class SubscriptionUpdate(BaseModel):
    end_date:date|None=None
    auto_renew:bool|None=None

class SubscriptionResponse(BaseModel):
    id:UUID; member_id:UUID; plan_id:UUID; plan_name:str|None; start_date:date; end_date:date; status:str; amount:float; auto_renew:bool
    payment_due_date:date|None
    paid_amount:float; remaining_amount:float; payment_status:str; check_in_allowed:bool
    invitation_limit:int; invitations_used:int; invitations_remaining:int
    freeze_limit_days:int; freeze_used_days:int; freeze_remaining_days:int
    model_config={"from_attributes":True}

class SubscriptionRenew(BaseModel):
    plan_id:UUID
    initial_payment_amount:float = Field(gt=0)
    initial_payment_method:str = "cash"
    payment_due_date:date|None=None

class FreezeCreate(BaseModel):
    days:int=Field(gt=0)
    reason:str|None=None
