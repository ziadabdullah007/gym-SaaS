from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
class AttendanceCheckIn(BaseModel): member_id:UUID
class AttendanceResponse(BaseModel):
    id:UUID; member_id:UUID; check_in_time:datetime; check_out_time:datetime|None; created_at:datetime
    model_config={"from_attributes":True}
