from flask import Blueprint, render_template, session, request
from app.extensions import db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.utils.decorators import login_required
from datetime import date

user = Blueprint('user', __name__)

RECORD_TYPES = [
    ('prescription', '💊 Prescription'),
    ('lab_test',     '🧪 Lab Test'),
    ('imaging',      '🩻 Imaging'),
    ('diagnosis',    '📋 Diagnosis'),
    ('other',        '📄 Other'),
]


@user.route('/dashboard')
@login_required
def dashboard():
    u = User.query.get_or_404(session['user_id'])
    today = date.today()

    upcoming = (
        Appointment.query
        .filter(
            Appointment.user_id == u.id,
            Appointment.date >= today,
            Appointment.status.in_(['pending', 'confirmed']),
        )
        .order_by(Appointment.date, Appointment.time_slot)
        .limit(5)
        .all()
    )

    past = (
        Appointment.query
        .filter(
            Appointment.user_id == u.id,
            Appointment.date < today,
        )
        .order_by(Appointment.date.desc())
        .limit(5)
        .all()
    )

    total = Appointment.query.filter_by(user_id=u.id).count()

    record_count = MedicalRecord.query.filter_by(user_id=u.id).count()

    return render_template('user/dashboard.html',
                           user=u, upcoming=upcoming, past=past,
                           total=total, record_count=record_count)


@user.route('/medical-history')
@login_required
def medical_history():
    u = User.query.get_or_404(session['user_id'])
    type_filter = request.args.get('type', 'all')

    q = MedicalRecord.query.filter_by(user_id=u.id)
    if type_filter != 'all':
        q = q.filter_by(record_type=type_filter)

    all_records = q.order_by(MedicalRecord.created_at.desc()).all()
    total = MedicalRecord.query.filter_by(user_id=u.id).count()

    # Stats
    doctors_seen = (
        db.session.query(MedicalRecord.doctor_id)
        .filter_by(user_id=u.id)
        .distinct()
        .count()
    )

    return render_template('user/medical_history.html',
                           user=u, all_records=all_records,
                           type_filter=type_filter, total=total,
                           doctors_seen=doctors_seen,
                           record_types=RECORD_TYPES)
