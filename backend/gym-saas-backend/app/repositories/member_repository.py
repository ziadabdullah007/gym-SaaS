from uuid import UUID
from app.models.member import Member
class MemberRepository:
    @staticmethod
    def get_all(db, gym_id): return db.query(Member).filter(Member.gym_id==gym_id).all()
    @staticmethod
    def get_by_id(db, member_id: UUID, gym_id): return db.query(Member).filter(Member.id==member_id, Member.gym_id==gym_id).first()
    @staticmethod
    def create(db, obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def update(db, obj): db.add(obj); db.flush(); return obj
    @staticmethod
    def delete(db, obj): db.delete(obj); db.flush()
