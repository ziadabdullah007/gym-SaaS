from datetime import datetime,timezone
from fastapi import HTTPException
from app.models.body_measurement import BodyMeasurement
from app.models.member import Member
from app.repositories.body_measurement_repository import BodyMeasurementRepository
class BodyMeasurementService:
    @staticmethod
    def create(db,gym_id,member_id,data):
        if not db.query(Member).filter(Member.id==member_id,Member.gym_id==gym_id).first():raise HTTPException(404,"Member not found")
        obj=BodyMeasurement(member_id=member_id,measured_at=datetime.now(timezone.utc),**data);db.add(obj);db.commit();db.refresh(obj);return obj
    @staticmethod
    def list(db,gym_id,member_id):return BodyMeasurementRepository.get_all(db,member_id,gym_id)
    @staticmethod
    def update(db,gym_id,member_id,measurement_id,data):
        obj=BodyMeasurementRepository.get_by_id(db,measurement_id,member_id,gym_id)
        if not obj: raise HTTPException(404,"Measurement not found")
        for k,v in data.items(): setattr(obj,k,v)
        db.commit(); db.refresh(obj); return obj
