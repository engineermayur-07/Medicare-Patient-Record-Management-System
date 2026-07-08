from datetime import datetime
from app.extensions import db


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(5), nullable=False)   # e.g. "09:00"
    status = db.Column(db.String(20), default='pending', nullable=False)
    # status: pending | confirmed | cancelled | completed
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)    # doctor's notes after visit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUS_COLORS = {
        'pending': 'badge-warning',
        'confirmed': 'badge-success',
        'cancelled': 'badge-danger',
        'completed': 'badge-muted',
    }

    @property
    def status_badge(self):
        return self.STATUS_COLORS.get(self.status, 'badge-muted')

    def __repr__(self):
        return f'<Appointment user={self.user_id} doctor={self.doctor_id} {self.date} {self.time_slot}>'
