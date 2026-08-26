from datetime import datetime, timezone
from fastapi import HTTPException
from app.repositories.gym_repository import GymRepository
class GymService:
    @staticmethod
    def update(db,gym_id,data):
        gym=GymRepository.get_by_id(db,gym_id)
        if not gym: raise HTTPException(404,"Gym not found")
        for k,v in data.items():
            if v is not None: setattr(gym,k,v)
        gym.updated_at=datetime.now(timezone.utc); db.commit(); db.refresh(gym); return gym
