from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: UUID): return db.query(User).filter(User.id == user_id).first()
    @staticmethod
    def get_by_username(db: Session, username: str): return db.query(User).filter(User.username == username).first()
    @staticmethod
    def create(db: Session, user: User): db.add(user); db.flush(); return user
    @staticmethod
    def update(db: Session, user: User): db.add(user); db.flush(); return user


def commit_refresh(db, obj):
    db.commit(); db.refresh(obj); return obj
