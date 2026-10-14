from datetime import datetime
from decimal import Decimal

from app.extensions import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'),
                               nullable=True)
    fee_type = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='INR', nullable=False)
    razorpay_order_id = db.Column(db.String(80), unique=True, nullable=True)
    razorpay_payment_id = db.Column(db.String(80), unique=True, nullable=True)
    razorpay_signature = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)
    receipt_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('payments', lazy='dynamic'))
    appointment = db.relationship(
        'Appointment',
        backref=db.backref('payments', lazy='dynamic'),
    )

    @property
    def amount_paise(self):
        return int(Decimal(str(self.amount)) * 100)

    def __repr__(self):
        return f'<Payment {self.id} {self.status} {self.amount} {self.currency}>'
