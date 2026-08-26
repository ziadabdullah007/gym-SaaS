from pydantic import BaseModel, Field
from uuid import UUID
class LoginRequest(BaseModel): username: str; password: str
class ActivationVerifyRequest(BaseModel):
    username: str
    activation_code: str = Field(min_length=6, max_length=6)

class ActivationVerifyResponse(BaseModel):
    valid: bool
    username: str

class SetupPasswordRequest(BaseModel):
    username: str
    activation_code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=8)
class UserResponse(BaseModel):
    id: UUID; username: str; role: str; status: str; first_name: str; last_name: str | None; gym_id: UUID | None = None
    model_config = {"from_attributes": True}
class LoginResponse(BaseModel): access_token: str; token_type: str = "bearer"; user: UserResponse
class SetupPasswordResponse(BaseModel): message: str
