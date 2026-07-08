import random
import string
from datetime import datetime, timedelta

from app.extensions import db
from app.models.otp import OTP


def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def create_otp(email: str, purpose: str = 'registration', expiry_minutes: int = 10) -> str:
    """Invalidate old OTPs for this email+purpose, create a fresh one, return the code."""
    OTP.query.filter_by(email=email, purpose=purpose, is_used=False).update({'is_used': True})
    db.session.flush()

    code = generate_otp()
    otp = OTP(
        email=email,
        code=code,
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes),
    )
    db.session.add(otp)
    db.session.commit()
    return code


def verify_otp(email: str, code: str, purpose: str = 'registration') -> bool:
    """Return True if a valid unused unexpired OTP matches, and marks it used."""
    otp = OTP.query.filter_by(
        email=email, code=code, purpose=purpose, is_used=False
    ).order_by(OTP.created_at.desc()).first()

    if otp and otp.is_valid:
        otp.is_used = True
        db.session.commit()
        return True
    return False


def generate_time_slots(start_hour: int = 9, end_hour: int = 17,
                         interval_minutes: int = 30) -> list[str]:
    """Return list of HH:MM strings from start_hour to end_hour (inclusive) at interval."""
    slots = []
    current = datetime(2000, 1, 1, start_hour, 0)
    end = datetime(2000, 1, 1, end_hour, 0)
    delta = timedelta(minutes=interval_minutes)
    while current <= end:
        slots.append(current.strftime('%H:%M'))
        current += delta
    return slots


def get_available_slots(doctor_id: int, date) -> list[str]:
    """Return time slots not yet booked for doctor on date (excludes cancelled)."""
    from app.models.appointment import Appointment
    booked = {
        a.time_slot
        for a in Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date,
            Appointment.status.in_(['pending', 'confirmed']),
        ).all()
    }
    return [s for s in generate_time_slots() if s not in booked]
