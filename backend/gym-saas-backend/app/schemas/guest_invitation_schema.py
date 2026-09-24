from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
class GuestInvitationResponse(BaseModel):
    id:UUID; subscription_id:UUID; member_id:UUID; attendance_id:UUID; guest_name:str; guest_phone:str; guest_age:int|None; guest_weight:float|None; visit_date:datetime; created_at:datetime
    model_config={"from_attributes":True}
