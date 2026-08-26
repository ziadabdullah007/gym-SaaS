from uuid import UUID
from sqlalchemy.orm import Session
from app.models.staff import Staff
class StaffRepository:
    @staticmethod
    def get_all(db, gym_id=None):
        q=db.query(Staff)
        return q.filter(Staff.gym_id==gym_id).all() if gym_id else q.all()
    @staticmethod
    def get_by_id(db, staff_id: UUID): return db.query(Staff).filter(Staff.id==staff_id).first()
    @staticmethod
    def get_by_user_id(db, user_id: UUID): return db.query(Staff).filter(Staff.user_id==user_id).first()
    @staticmethod
    def create(db, staff): db.add(staff); db.flush(); return staff
    @staticmethod
    def update(db, staff): db.add(staff); db.flush(); return staff
