from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.doctor import Doctor
from app.models.user import User
from app.models.appointment import Appointment
from app.models.service import Service
from app.utils.decorators import admin_required

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
