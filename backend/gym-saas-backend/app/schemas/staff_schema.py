from pydantic import BaseModel
from uuid import UUID
class StaffCreate(BaseModel): username: str; first_name: str; last_name: str|None=None; position: str
class StaffUpdate(BaseModel): position: str|None=None; status: str|None=None; first_name: str|None=None; last_name: str|None=None
class StaffResponse(BaseModel):
    id: UUID; gym_id: UUID; user_id: UUID; position: str; status: str
    model_config={"from_attributes":True}

class StaffProvisionResponse(BaseModel):
    staff: StaffResponse
    username: str
    activation_code: str
