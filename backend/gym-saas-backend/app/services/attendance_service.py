from datetime import datetime,timezone
from fastapi import HTTPException
from app.models.attendance import Attendance
from app.models.member import Member
from app.repositories.attendance_repository import AttendanceRepository
class AttendanceService:
    @staticmethod
    def check_in(db,gym_id,member_id):
        member=db.query(Member).filter(Member.id==member_id,Member.gym_id==gym_id).first()
        if not member:raise HTTPException(404,"Member not found")
        active=db.query(Attendance).filter(Attendance.member_id==member_id,Attendance.check_out_time.is_(None)).first()
        if active: raise HTTPException(400,"Member is already checked in")
        obj=Attendance(member_id=member_id,check_in_time=datetime.now(timezone.utc),check_out_time=None,created_at=datetime.now(timezone.utc));db.add(obj);member.last_visit_at=obj.check_in_time;db.commit();db.refresh(obj);return obj
    @staticmethod
    def check_out(db,gym_id,attendance_id):
        obj=AttendanceRepository.get_by_id(db,attendance_id,gym_id)
        if not obj:raise HTTPException(404,"Attendance not found")
        if obj.check_out_time:raise HTTPException(400,"Attendance already checked out")
        obj.check_out_time=datetime.now(timezone.utc);db.commit();db.refresh(obj);return obj
    @staticmethod
    def list(db,gym_id):return AttendanceRepository.get_all(db,gym_id)
