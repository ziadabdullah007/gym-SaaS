from pydantic import BaseModel
from uuid import UUID
from datetime import date
class SubscriptionCreate(BaseModel): member_id:UUID; plan_id:UUID; start_date:date; end_date:date; amount:float; auto_renew:bool=False
class SubscriptionUpdate(BaseModel): status:str|None=None; end_date:date|None=None; amount:float|None=None; auto_renew:bool|None=None
class SubscriptionResponse(BaseModel):
    id:UUID; member_id:UUID; plan_id:UUID; start_date:date; end_date:date; status:str; amount:float; auto_renew:bool
    model_config={"from_attributes":True}
