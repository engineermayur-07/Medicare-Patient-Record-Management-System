import os
import uuid
from datetime import datetime

from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, session, abort, send_file, current_app)
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.medical_record import MedicalRecord
from app.models.appointment import Appointment
from app.models.user import User
from app.models.doctor import Doctor
from app.utils.decorators import login_required, doctor_required, admin_required

records = Blueprint('records', __name__)

RECORD_TYPES = [
    ('prescription', '💊 Prescription'),
    ('lab_test',     '🧪 Lab Test'),
    ('imaging',      '🩻 Imaging (X-Ray / MRI / CT)'),
    ('diagnosis',    '📋 Diagnosis & Notes'),
    ('other',        '📄 Other'),
]


# ─── helpers ──────────────────────────────────────────────────────────────────

def _allowed_file(filename: str) -> bool:
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def _save_file(file, user_id: int) -> tuple[str, str, int, str]:
    """Save uploaded file. Returns (file_path, file_name, file_size, mime_type)."""
    original_name = secure_filename(file.filename)
    ext = original_name.rsplit('.', 1)[-1].lower()
    unique_name = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

    user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], f'user_{user_id}')
    os.makedirs(user_dir, exist_ok=True)

    full_path = os.path.join(user_dir, unique_name)
    file.save(full_path)
    size = os.path.getsize(full_path)

    mime_map = {'pdf': 'application/pdf', 'png': 'image/png',
                'jpg': 'image/jpeg', 'jpeg': 'image/jpeg'}
    mime = mime_map.get(ext, 'application/octet-stream')

    return full_path, original_name, size, mime


def _can_access_record(record: MedicalRecord) -> bool:
    """Return True if the current session user is allowed to view this record."""
    role = session.get('user_role')
    uid  = session.get('user_id')
    if role == 'admin':
        return True
    if role == 'user' and record.user_id == uid:
        return True
    if role == 'doctor' and record.doctor_id == uid:
        return True
    return False


# ─── upload ───────────────────────────────────────────────────────────────────

@records.route('/upload/<int:appointment_id>', methods=['GET', 'POST'])
@doctor_required
def upload(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)

    # Doctor can only upload to their own appointments
    if appt.doctor_id != session['user_id']:
        abort(403)

    doctor = Doctor.query.get(session['user_id'])
    patient = User.query.get(appt.user_id)

    if request.method == 'POST':
        record_type = request.form.get('record_type', '').strip()
        title       = request.form.get('title', '').strip()
        notes       = request.form.get('notes', '').strip()
        uploaded_file = request.files.get('file')

        if not record_type or not title:
            flash('Record type and title are required.', 'danger')
            return render_template('records/upload.html', appointment=appt,
                                   patient=patient, doctor=doctor,
                                   record_types=RECORD_TYPES)

        file_path = file_name = file_mime = None
        file_size = None

        if uploaded_file and uploaded_file.filename:
            if not _allowed_file(uploaded_file.filename):
                flash('Only PDF, PNG, JPG, JPEG files are allowed.', 'danger')
                return render_template('records/upload.html', appointment=appt,
                                       patient=patient, doctor=doctor,
                                       record_types=RECORD_TYPES)
            try:
                file_path, file_name, file_size, file_mime = _save_file(
                    uploaded_file, appt.user_id)
            except Exception as e:
                current_app.logger.error(f'File save error: {e}')
                flash('File upload failed. Please try again.', 'danger')
                return render_template('records/upload.html', appointment=appt,
                                       patient=patient, doctor=doctor,
                                       record_types=RECORD_TYPES)

        rec = MedicalRecord(
            user_id=appt.user_id,
            doctor_id=session['user_id'],
            appointment_id=appointment_id,
            record_type=record_type,
            title=title,
            notes=notes,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            file_mime=file_mime,
        )
        db.session.add(rec)
        db.session.commit()

        flash(f'Medical record "{title}" uploaded for {patient.name}.', 'success')
        return redirect(url_for('doctor.appointments'))

    return render_template('records/upload.html', appointment=appt,
                           patient=patient, doctor=doctor,
                           record_types=RECORD_TYPES)


# ─── download / view ──────────────────────────────────────────────────────────

@records.route('/download/<int:record_id>')
def download(record_id):
    rec = MedicalRecord.query.get_or_404(record_id)
    if not _can_access_record(rec):
        abort(403)
    if not rec.has_file or not os.path.exists(rec.file_path):
        flash('File not found on server.', 'danger')
        return redirect(request.referrer or url_for('main.index'))
    return send_file(rec.file_path, as_attachment=True,
                     download_name=rec.file_name, mimetype=rec.file_mime)


@records.route('/view/<int:record_id>')
def view_inline(record_id):
    """Serve PDF/image inline in the browser (no download prompt)."""
    rec = MedicalRecord.query.get_or_404(record_id)
    if not _can_access_record(rec):
        abort(403)
    if not rec.has_file or not os.path.exists(rec.file_path):
        abort(404)
    return send_file(rec.file_path, mimetype=rec.file_mime)


# ─── delete ───────────────────────────────────────────────────────────────────

@records.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id):
    rec = MedicalRecord.query.get_or_404(record_id)
    role = session.get('user_role')
    uid  = session.get('user_id')

    if role not in ('doctor', 'admin'):
        abort(403)
    if role == 'doctor' and rec.doctor_id != uid:
        abort(403)

    # Remove file from disk
    if rec.file_path and os.path.exists(rec.file_path):
        try:
            os.remove(rec.file_path)
        except OSError as e:
            current_app.logger.warning(f'Could not delete file {rec.file_path}: {e}')

    db.session.delete(rec)
    db.session.commit()
    flash('Medical record deleted.', 'info')
    return redirect(request.referrer or url_for('doctor.appointments'))


# ─── patient history (doctor view) ────────────────────────────────────────────

@records.route('/patient/<int:user_id>')
@doctor_required
def patient_history(user_id):
    """Doctor views a specific patient's full medical history."""
    patient = User.query.get_or_404(user_id)
    type_filter = request.args.get('type', 'all')

    q = MedicalRecord.query.filter_by(user_id=user_id)
    if type_filter != 'all':
        q = q.filter_by(record_type=type_filter)

    all_records = q.order_by(MedicalRecord.created_at.desc()).all()
    total = MedicalRecord.query.filter_by(user_id=user_id).count()

    return render_template('records/patient_history.html',
                           patient=patient, all_records=all_records,
                           type_filter=type_filter, total=total,
                           record_types=RECORD_TYPES)
