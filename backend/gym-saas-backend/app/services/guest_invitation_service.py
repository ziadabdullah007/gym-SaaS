from app.models.guest_invitation import GuestInvitation
class GuestInvitationService:
    @staticmethod
    def list(db,gym_id):
        return db.query(GuestInvitation).filter(GuestInvitation.gym_id==gym_id).order_by(GuestInvitation.visit_date.desc()).all()
