from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
class PaymentCreate(BaseModel): subscription_id:UUID; amount:float; payment_method:str
class PaymentResponse(BaseModel):
    id:UUID; subscription_id:UUID; amount:float; payment_method:str; status:str; payment_date:datetime
    model_config={"from_attributes":True}
