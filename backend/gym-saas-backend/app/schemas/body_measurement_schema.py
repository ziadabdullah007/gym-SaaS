from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
class BodyMeasurementCreate(BaseModel): weight:float|None=None; body_fat_percentage:float|None=None; bmi:float|None=None; notes:str|None=None
class BodyMeasurementUpdate(BaseModel): weight:float|None=None; body_fat_percentage:float|None=None; bmi:float|None=None; notes:str|None=None
class BodyMeasurementResponse(BaseModel):
    id:UUID; member_id:UUID; measured_at:datetime; weight:float|None; body_fat_percentage:float|None; bmi:float|None; notes:str|None
    model_config={"from_attributes":True}
