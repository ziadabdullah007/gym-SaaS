from datetime import datetime, timedelta, timezone
from uuid import UUID
import secrets
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from app.core.config import settings

password_hasher=PasswordHasher()

def hash_password(password:str)->str:return password_hasher.hash(password)
def verify_password(password:str,password_hash:str)->bool:
    try:return password_hasher.verify(password_hash,password)
    except (VerifyMismatchError,VerificationError):return False

def create_access_token(user_id:UUID,role:str,gym_id:UUID|None=None)->str:
    now=datetime.now(timezone.utc); payload={"sub":str(user_id),"role":role,"iat":now,"exp":now+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
    if gym_id:payload["gym_id"]=str(gym_id)
    return jwt.encode(payload,settings.JWT_SECRET_KEY,algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token:str)->dict:
    return jwt.decode(token,settings.JWT_SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])
def generate_activation_code():
    # Six-digit one-time activation code shown only to the provisioning admin.
    code=f"{secrets.randbelow(1_000_000):06d}"
    return code,hash_password(code)

def generate_setup_token():
    # Backward-compatible alias for existing callers.
    return generate_activation_code()
