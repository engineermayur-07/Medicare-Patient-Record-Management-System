from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.extensions import db
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.utils.decorators import doctor_required

doctor = Blueprint('doctor', __name__)


@doctor.route('/dashboard')
@doctor_required
def dashboard():
    doc = Doctor.query.get_or_404(session['user_id'])
    today = date.today()

    upcoming = (
        Appointment.query
        .filter(
            Appointment.doctor_id == doc.id,
            Appointment.date >= today,
            Appointment.status.in_(['pending', 'confirmed']),
        )
        .order_by(Appointment.date, Appointment.time_slot)
        .limit(10)
        .all()
    )

    today_count = Appointment.query.filter(
        Appointment.doctor_id == doc.id,
        Appointment.date == today,
        Appointment.status.in_(['pending', 'confirmed']),
    ).count()

    total = Appointment.query.filter_by(doctor_id=doc.id).count()
    pending_count = Appointment.query.filter_by(doctor_id=doc.id, status='pending').count()

    return render_template('doctor/dashboard.html',
                           doctor=doc, upcoming=upcoming,
                           today_count=today_count, total=total,
                           pending_count=pending_count)


@doctor.route('/appointments')
@doctor_required
def appointments():
    doc = Doctor.query.get_or_404(session['user_id'])
    status_filter = request.args.get('status', 'all')
    query = Appointment.query.filter_by(doctor_id=doc.id)
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    all_appts = query.order_by(Appointment.date.desc(), Appointment.time_slot.desc()).all()
    return render_template('doctor/appointments.html',
                           doctor=doc, appointments=all_appts,
                           status_filter=status_filter)


@doctor.route('/appointments/<int:appt_id>/confirm', methods=['POST'])
@doctor_required
def confirm_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != session['user_id']:
        abort(403)
    if appt.status != 'pending':
        flash('Only pending appointments can be confirmed.', 'warning')
    else:
        appt.status = 'confirmed'
        db.session.commit()
        flash('Appointment confirmed.', 'success')
    return redirect(url_for('doctor.appointments'))


@doctor.route('/appointments/<int:appt_id>/complete', methods=['POST'])
@doctor_required
def complete_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != session['user_id']:
        abort(403)
    notes = request.form.get('notes', '').strip()
    if appt.status in ('pending', 'confirmed'):
        appt.status = 'completed'
        appt.notes = notes
        db.session.commit()
        flash('Appointment marked as completed.', 'success')
    else:
        flash('Cannot complete this appointment.', 'warning')
    return redirect(url_for('doctor.appointments'))


@doctor.route('/appointments/<int:appt_id>/cancel', methods=['POST'])
@doctor_required
def cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != session['user_id']:
        abort(403)
    if appt.status in ('pending', 'confirmed'):
        appt.status = 'cancelled'
        db.session.commit()
        flash('Appointment cancelled.', 'info')
    else:
        flash('Cannot cancel this appointment.', 'warning')
    return redirect(url_for('doctor.appointments'))
