import os
import uuid
from datetime import date, datetime

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   send_file, session, request, url_for)
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.utils.decorators import login_required
from datetime import date

user = Blueprint('user', __name__)

PROFILE_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MIN_DATE_OF_BIRTH = date(1960, 1, 1)
MAX_DATE_OF_BIRTH = date(2015, 12, 31)

RECORD_TYPES = [
    ('prescription', '💊 Prescription'),
    ('lab_test',     '🧪 Lab Test'),
    ('imaging',      '🩻 Imaging'),
    ('diagnosis',    '📋 Diagnosis'),
    ('other',        '📄 Other'),
]


def _save_profile_photo(uploaded_file, user_id):
    filename = secure_filename(uploaded_file.filename or '')
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if extension not in PROFILE_PHOTO_EXTENSIONS:
        raise ValueError('Profile photo must be a PNG, JPG, or JPEG image.')

    profile_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
    os.makedirs(profile_dir, exist_ok=True)
    saved_name = f'user_{user_id}_{uuid.uuid4().hex}.{extension}'
    path = os.path.join(profile_dir, saved_name)
    uploaded_file.save(path)
    return path


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


@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    patient = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        raw_dob = request.form.get('dob', '').strip()
        medical_conditions = request.form.get('medical_conditions', '').strip()

        parsed_dob = None
        if raw_dob:
            try:
                parsed_dob = datetime.strptime(raw_dob, '%Y-%m-%d').date()
            except ValueError:
                flash('Please enter a valid date of birth.', 'danger')
                return render_template('user/profile.html', user=patient)
            if not MIN_DATE_OF_BIRTH <= parsed_dob <= MAX_DATE_OF_BIRTH:
                flash('Date of birth must be between 1960 and 2015.', 'danger')
                return render_template('user/profile.html', user=patient)

        uploaded_photo = request.files.get('profile_photo')
        new_photo_path = None
        if uploaded_photo and uploaded_photo.filename:
            try:
                new_photo_path = _save_profile_photo(uploaded_photo, patient.id)
            except ValueError as exc:
                flash(str(exc), 'danger')
                return render_template('user/profile.html', user=patient)

        old_photo_path = patient.profile_photo_path
        patient.dob = parsed_dob
        patient.medical_conditions = medical_conditions or None
        if new_photo_path:
            patient.profile_photo_path = new_photo_path
        db.session.commit()

        if new_photo_path and old_photo_path and os.path.exists(old_photo_path):
            try:
                os.remove(old_photo_path)
            except OSError:
                current_app.logger.warning(
                    'Could not remove old profile photo for user %s.', patient.id
                )

        flash('Your profile has been updated.', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html', user=patient)


@user.route('/profile/photo')
@login_required
def profile_photo():
    return _serve_profile_photo(session['user_id'])


@user.route('/profile/photo/<int:user_id>')
def patient_profile_photo(user_id):
    if session.get('user_role') not in ('user', 'doctor', 'admin'):
        return redirect(url_for('auth.login'))
    if session.get('user_role') == 'user' and session.get('user_id') != user_id:
        return redirect(url_for('user.profile'))
    return _serve_profile_photo(user_id)


def _serve_profile_photo(user_id):
    patient = User.query.get_or_404(user_id)
    if not patient.profile_photo_path or not os.path.exists(patient.profile_photo_path):
        return redirect(url_for('user.profile'))
    return send_file(patient.profile_photo_path)


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
