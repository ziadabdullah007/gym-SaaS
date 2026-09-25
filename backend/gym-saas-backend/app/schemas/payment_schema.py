from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
class PaymentCreate(BaseModel):
    subscription_id:UUID
    amount:float=Field(gt=0)
    payment_method:str
    idempotency_key:str|None=None
class PaymentResponse(BaseModel):
    id:UUID; subscription_id:UUID; amount:float; payment_method:str; status:str; payment_date:datetime
    model_config={"from_attributes":True}
