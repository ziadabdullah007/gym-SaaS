from uuid import UUID
from sqlalchemy.orm import Session
from app.models.gym import Gym
class GymRepository:
    @staticmethod
    def get_all(db): return db.query(Gym).all()
    @staticmethod
    def get_by_id(db, gym_id: UUID): return db.query(Gym).filter(Gym.id == gym_id).first()
    @staticmethod
    def get_by_admin_user_id(db, user_id: UUID): return db.query(Gym).filter(Gym.gym_admin_user_id == user_id).first()
    @staticmethod
    def create(db, gym): db.add(gym); db.flush(); return gym
    @staticmethod
    def update(db, gym): db.add(gym); db.flush(); return gym
    @staticmethod
    def delete(db, gym): db.delete(gym); db.flush()
