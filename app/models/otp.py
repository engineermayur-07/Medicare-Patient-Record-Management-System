from datetime import datetime
from app.extensions import db


class OTP(db.Model):
    __tablename__ = 'otps'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20), default='registration')  # registration | reset
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at

    def __repr__(self):
        return f'<OTP {self.email} {self.code}>'
