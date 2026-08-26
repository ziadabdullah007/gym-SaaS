from uuid import UUID
from app.models.attendance import Attendance
class AttendanceRepository:
    @staticmethod
    def get_all(db, gym_id): return db.query(Attendance).join(Attendance.member).filter(Attendance.member.has(gym_id=gym_id)).all()
    @staticmethod
    def get_by_id(db, attendance_id: UUID, gym_id): return db.query(Attendance).join(Attendance.member).filter(Attendance.id==attendance_id, Attendance.member.has(gym_id=gym_id)).first()
    @staticmethod
    def create(db,obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def update(db,obj): db.add(obj); db.flush(); return obj
