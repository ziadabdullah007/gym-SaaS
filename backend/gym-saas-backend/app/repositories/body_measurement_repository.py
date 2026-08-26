from uuid import UUID
from app.models.body_measurement import BodyMeasurement
class BodyMeasurementRepository:
    @staticmethod
    def get_all(db, member_id: UUID, gym_id): return db.query(BodyMeasurement).filter(BodyMeasurement.member_id==member_id, BodyMeasurement.member.has(gym_id=gym_id)).all()
    @staticmethod
    def get_by_id(db, measurement_id: UUID, member_id: UUID, gym_id): return db.query(BodyMeasurement).filter(BodyMeasurement.id==measurement_id, BodyMeasurement.member_id==member_id, BodyMeasurement.member.has(gym_id=gym_id)).first()
    @staticmethod
    def create(db,obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def update(db,obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def delete(db,obj): db.delete(obj); db.flush()
