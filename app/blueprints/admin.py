import os

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   send_file, url_for)
from app.extensions import db
from app.models.doctor import Doctor
from app.models.user import User
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.payment import Payment
from app.models.medical_record import MedicalRecord
from app.utils.decorators import admin_required
from app.utils.email import send_fee_reminder_email
from app.utils.validation import parse_medical_fee, validate_password_strength

admin = Blueprint('admin', __name__)

DEPARTMENTS = [
    'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics',
    'Oncology', 'Dermatology', 'Gynecology', 'Ophthalmology',
    'Psychiatry', 'Radiology', 'Emergency', 'General Medicine',
]


@admin.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_doctors = Doctor.query.filter_by(is_active=True).count()
    total_appts = Appointment.query.count()
    pending_appts = Appointment.query.filter_by(status='pending').count()
    recent_appts = (
        Appointment.query
        .order_by(Appointment.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_doctors=total_doctors,
                           total_appts=total_appts,
                           pending_appts=pending_appts,
                           recent_appts=recent_appts)


@admin.route('/patients')
@admin_required
def patients():
    all_patients = User.query.order_by(User.name).all()
    return render_template('admin/patients.html', patients=all_patients)


@admin.route('/patients/<int:user_id>')
@admin_required
def patient_details(user_id):
    patient = User.query.get_or_404(user_id)
    appointments = (
        Appointment.query.filter_by(user_id=user_id)
        .order_by(Appointment.date.desc(), Appointment.time_slot.desc()).all()
    )
    records = (
        MedicalRecord.query.filter_by(user_id=user_id)
        .order_by(MedicalRecord.created_at.desc()).all()
    )
    payments = (
        Payment.query.filter_by(user_id=user_id)
        .order_by(Payment.created_at.desc()).all()
    )
    return render_template(
        'admin/patient_details.html',
        patient=patient,
        appointments=appointments,
        records=records,
        payments=payments,
    )


@admin.route('/patients/<int:user_id>/photo')
@admin_required
def patient_photo(user_id):
    patient = User.query.get_or_404(user_id)
    if not patient.profile_photo_path or not os.path.exists(patient.profile_photo_path):
        abort(404)
    return send_file(patient.profile_photo_path)


@admin.route('/patients/<int:user_id>/remind-fees', methods=['POST'])
@admin_required
def remind_fees(user_id):
    patient = User.query.get_or_404(user_id)
    unpaid_fees = Payment.query.filter(
        Payment.user_id == user_id,
        Payment.status.in_(['pending', 'failed']),
    ).order_by(Payment.created_at.desc()).all()

    if not unpaid_fees:
        flash('This patient has no unpaid fees.', 'info')
        return redirect(url_for('admin.patient_details', user_id=user_id))

    if send_fee_reminder_email(patient.email, patient.name, unpaid_fees):
        flash(f'Fee reminder sent to {patient.email}.', 'success')
    else:
        flash('The fee reminder could not be sent. Check the email configuration.', 'danger')
    return redirect(url_for('admin.patient_details', user_id=user_id))


@admin.route('/fees/add', methods=['GET', 'POST'])
@admin_required
def add_medical_fee():
    users = User.query.order_by(User.name).all()
    if request.method == 'POST':
        user_id = request.form.get('user_id', type=int)
        description = request.form.get('description', '').strip()
        raw_amount = request.form.get('amount', '').strip()

        amount, amount_error = parse_medical_fee(raw_amount)

        if not user_id or not description:
            flash('Patient and fee description are required.', 'danger')
            return render_template('admin/add_fee.html', users=users)
        if len(description) > 255:
            flash('Fee description must be 255 characters or fewer.', 'danger')
            return render_template('admin/add_fee.html', users=users)
        if amount_error:
            flash(amount_error, 'danger')
            return render_template('admin/add_fee.html', users=users)

        user = User.query.get(user_id)
        if not user:
            flash('Selected patient was not found.', 'danger')
            return render_template('admin/add_fee.html', users=users)

        db.session.add(Payment(
            user_id=user.id,
            fee_type='medical_fee',
            description=description,
            amount=amount,
        ))
        db.session.commit()
        flash(f'Medical fee created for {user.name}.', 'success')
        return redirect(url_for('admin.add_medical_fee'))

    return render_template('admin/add_fee.html', users=users)


# ─────────────────────────── Doctors ─────────────────────────────────

@admin.route('/doctors')
@admin_required
def doctors_list():
    all_doctors = Doctor.query.order_by(Doctor.name).all()
    return render_template('admin/doctors_list.html', doctors=all_doctors,
                           departments=DEPARTMENTS)


@admin.route('/doctors/add', methods=['GET', 'POST'])
@admin_required
def add_doctor():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        specialization = request.form.get('specialization', '').strip()
        department = request.form.get('department', '').strip()
        qualification = request.form.get('qualification', '').strip()
        experience = request.form.get('experience_years', '0')
        bio = request.form.get('bio', '').strip()

        if not all([name, email, password, specialization, department]):
            flash('Name, email, password, specialization and department are required.', 'danger')
            return render_template('admin/add_doctor.html', departments=DEPARTMENTS)

        password_error = validate_password_strength(password)
        if password_error:
            flash(password_error, 'danger')
            return render_template('admin/add_doctor.html', departments=DEPARTMENTS)

        if Doctor.query.filter_by(email=email).first():
            flash('A doctor with this email already exists.', 'danger')
            return render_template('admin/add_doctor.html', departments=DEPARTMENTS)

        try:
            exp = int(experience)
        except ValueError:
            exp = 0

        doc = Doctor(
            name=name, email=email, phone=phone,
            specialization=specialization, department=department,
            qualification=qualification, experience_years=exp,
            bio=bio, is_active=True,
        )
        doc.set_password(password)
        db.session.add(doc)
        db.session.commit()
        flash(f'Dr. {name} has been added successfully.', 'success')
        return redirect(url_for('admin.doctors_list'))

    return render_template('admin/add_doctor.html', departments=DEPARTMENTS)


@admin.route('/doctors/<int:doctor_id>/toggle', methods=['POST'])
@admin_required
def toggle_doctor(doctor_id):
    doc = Doctor.query.get_or_404(doctor_id)
    doc.is_active = not doc.is_active
    db.session.commit()
    state = 'activated' if doc.is_active else 'deactivated'
    flash(f'Dr. {doc.name} has been {state}.', 'info')
    return redirect(url_for('admin.doctors_list'))


@admin.route('/doctors/<int:doctor_id>/delete', methods=['POST'])
@admin_required
def delete_doctor(doctor_id):
    doc = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doc)
    db.session.commit()
    flash(f'Dr. {doc.name} has been removed.', 'info')
    return redirect(url_for('admin.doctors_list'))


# ─────────────────────────── Services ────────────────────────────────

@admin.route('/services')
@admin_required
def services():
    all_services = Service.query.order_by(Service.name).all()
    return render_template('admin/services.html', services=all_services)


@admin.route('/services/add', methods=['POST'])
@admin_required
def add_service():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    department = request.form.get('department', '').strip()
    icon = request.form.get('icon', '🏥').strip() or '🏥'

    if not name:
        flash('Service name is required.', 'danger')
        return redirect(url_for('admin.services'))

    svc = Service(name=name, description=description, department=department, icon=icon)
    db.session.add(svc)
    db.session.commit()
    flash(f'Service "{name}" added.', 'success')
    return redirect(url_for('admin.services'))


@admin.route('/services/<int:service_id>/delete', methods=['POST'])
@admin_required
def delete_service(service_id):
    svc = Service.query.get_or_404(service_id)
    db.session.delete(svc)
    db.session.commit()
    flash(f'Service "{svc.name}" deleted.', 'info')
    return redirect(url_for('admin.services'))


@admin.route('/services/<int:service_id>/toggle', methods=['POST'])
@admin_required
def toggle_service(service_id):
    svc = Service.query.get_or_404(service_id)
    svc.is_active = not svc.is_active
    db.session.commit()
    return redirect(url_for('admin.services'))
