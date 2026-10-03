from datetime import datetime,timezone
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.member import Member
from app.repositories.member_repository import MemberRepository
from app.core.security import hash_password, verify_password, create_access_token
import secrets
import re
from datetime import timedelta
class MemberService:
    @staticmethod
    def create(db,gym_id,data):
        now=datetime.now(timezone.utc)
        password=data.pop("password", None)
        username=str(data.pop("username", "")).strip().lower()
        if not username:
            raise HTTPException(400, "Username is required.")
        if db.query(Member).filter(func.lower(Member.username) == username).first() or db.query(User).filter(func.lower(User.username) == username).first():
            raise HTTPException(409, "Username already exists. Please choose another username.")
        if len(password or "") < 8:
            raise HTTPException(400, "Password must be at least 8 characters.")
        obj=Member(gym_id=gym_id,status="active",app_access_enabled=True,joined_at=now,created_at=now,updated_at=now,
                   username=username,password_hash=hash_password(password), **data)
        db.add(obj)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "Username already exists. Please choose another username.")
        db.refresh(obj)
        return obj
    @staticmethod
    def get_all(db,gym_id): return MemberRepository.get_all(db,gym_id)
    @staticmethod
    def get(db,id,gym_id): return MemberRepository.get_by_id(db,id,gym_id)
    @staticmethod
    def update(db,id,gym_id,data):
        obj=MemberRepository.get_by_id(db,id,gym_id)
        if not obj: return None
        for k,v in data.items():
            if v is not None: setattr(obj,k,v)
        if data.get("app_access_enabled") is False:
            obj.entry_qr_token_hash = None
        obj.updated_at=datetime.now(timezone.utc); db.commit(); db.refresh(obj); return obj
    @staticmethod
    def authenticate_member(db, username, password):
        username=str(username).strip().lower()
        obj=db.query(Member).filter(func.lower(Member.username)==username).first()
        if not obj or not obj.app_access_enabled or not obj.password_hash or not verify_password(password,obj.password_hash):
            raise HTTPException(401,"Invalid username or password.")
        token=create_access_token(obj.id,"member",obj.gym_id)
        return {"access_token":token,"token_type":"bearer","member":{"id":str(obj.id),"username":obj.username,"first_name":obj.first_name,"last_name":obj.last_name,"phone":obj.phone}}

    @staticmethod
    def set_username(db, member_id, gym_id, username):
        obj=MemberRepository.get_by_id(db,member_id,gym_id)
        if not obj: raise HTTPException(404,"Member not found")
        username=str(username).strip().lower()
        if not username: raise HTTPException(400,"Username is required.")
        if not re.match(r"^[A-Za-z0-9._-]{3,50}$", username):
            raise HTTPException(400,"Username must be 3-50 characters using letters, numbers, dot, underscore or hyphen.")
        existing_member=db.query(Member).filter(func.lower(Member.username)==username, Member.id!=member_id).first()
        existing_user=db.query(User).filter(func.lower(User.username)==username).first()
        if existing_member or existing_user:
            raise HTTPException(409,"Username already exists. Please choose another username.")
        obj.username=username
        obj.updated_at=datetime.now(timezone.utc)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409,"Username already exists. Please choose another username.")
        db.refresh(obj)
        return obj

    def set_initial_password(db, member_id, gym_id, password):
        obj=MemberRepository.get_by_id(db,member_id,gym_id)
        if not obj: raise HTTPException(404,"Member not found")
        if obj.password_hash: raise HTTPException(409,"Member already has an app password. Use password reset if it was forgotten.")
        if len(password) < 8: raise HTTPException(400,"Password must be at least 8 characters.")
        obj.password_hash=hash_password(password)
        obj.updated_at=datetime.now(timezone.utc)
        db.commit(); db.refresh(obj); return obj

    @staticmethod
    def generate_password_reset_code(db, member_id, gym_id):
        obj=MemberRepository.get_by_id(db,member_id,gym_id)
        if not obj: raise HTTPException(404,"Member not found")
        if not obj.password_hash: raise HTTPException(409,"Member has no password yet. Set the initial password instead.")
        code=secrets.token_urlsafe(9)
        obj.password_reset_code_hash=hash_password(code)
        obj.password_reset_expires_at=datetime.now(timezone.utc)+timedelta(minutes=10)
        obj.updated_at=datetime.now(timezone.utc)
        db.commit()
        return {"reset_code":code,"expires_in_minutes":10}

    @staticmethod
    def reset_password(db, username, code, new_password):
        if len(new_password) < 8: raise HTTPException(400,"Password must be at least 8 characters.")
        candidates=db.query(Member).filter(func.lower(Member.username)==str(username).strip().lower(), Member.password_reset_code_hash.isnot(None)).all()
        now=datetime.now(timezone.utc)
        for obj in candidates:
            expires=obj.password_reset_expires_at
            if expires and expires.tzinfo is None: expires=expires.replace(tzinfo=timezone.utc)
            if expires and expires > now and verify_password(code,obj.password_reset_code_hash):
                obj.password_hash=hash_password(new_password)
                obj.password_reset_code_hash=None
                obj.password_reset_expires_at=None
                obj.updated_at=now
                db.commit()
                return {"message":"Password reset successfully. You can now sign in."}
        raise HTTPException(400,"Invalid or expired reset code.")

    @staticmethod
    def delete(db,id,gym_id):
        obj=MemberRepository.get_by_id(db,id,gym_id)
        if not obj:return False
        db.delete(obj); db.commit(); return True
