from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from app.extensions import db
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.utils.decorators import login_required
from app.utils.helpers import get_available_slots

appointments = Blueprint('appointments', __name__)


@appointments.route('/book')
@login_required
def select_doctor():
    """Step 1: pick a doctor."""
    doctors = Doctor.query.filter_by(is_active=True).order_by(Doctor.name).all()
    return render_template('appointments/select_doctor.html', doctors=doctors)


@appointments.route('/book/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book(doctor_id):
    """Step 2: pick date & time for the chosen doctor."""
    doctor = Doctor.query.filter_by(id=doctor_id, is_active=True).first_or_404()

    if request.method == 'POST':
        raw_date = request.form.get('date', '').strip()
        time_slot = request.form.get('time_slot', '').strip()
        reason = request.form.get('reason', '').strip()

        if not raw_date or not time_slot:
            flash('Please select both a date and a time slot.', 'danger')
            return render_template('appointments/book.html', doctor=doctor)

        try:
            appt_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('appointments/book.html', doctor=doctor)

        if appt_date <= date.today():
            flash('Please choose a future date.', 'danger')
            return render_template('appointments/book.html', doctor=doctor)

        # Check slot still available
        available = get_available_slots(doctor_id, appt_date)
        if time_slot not in available:
            flash('That time slot is no longer available. Please choose another.', 'warning')
            return render_template('appointments/book.html', doctor=doctor)

        user_id = session['user_id']
        active_statuses = ['pending', 'confirmed']

        same_doctor_same_day = Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.doctor_id == doctor_id,
            Appointment.date == appt_date,
            Appointment.status.in_(active_statuses),
        ).first()
        if same_doctor_same_day:
            flash('You already have an appointment with this doctor on that day.', 'warning')
            return render_template('appointments/book.html', doctor=doctor)

        another_doctor_same_time = Appointment.query.filter(
            Appointment.user_id == user_id,
            Appointment.date == appt_date,
            Appointment.time_slot == time_slot,
            Appointment.status.in_(active_statuses),
        ).first()
        if another_doctor_same_time:
            flash('You already have another appointment at that date and time.', 'warning')
            return render_template('appointments/book.html', doctor=doctor)

        appt = Appointment(
            user_id=user_id,
            doctor_id=doctor_id,
            date=appt_date,
            time_slot=time_slot,
            reason=reason,
            status='pending',
        )
        db.session.add(appt)
        db.session.commit()

        flash('Appointment booked successfully! The doctor will confirm shortly.', 'success')
        return redirect(url_for('appointments.my_appointments'))

    return render_template('appointments/book.html', doctor=doctor)


@appointments.route('/slots/<int:doctor_id>/<string:date_str>')
@login_required
def available_slots(doctor_id, date_str):
    """AJAX endpoint: return available time slots as JSON."""
    try:
        appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'slots': [], 'error': 'Invalid date'}), 400

    if appt_date <= date.today():
        return jsonify({'slots': []})

    doctor = Doctor.query.get(doctor_id)
    if not doctor or not doctor.is_active:
        abort(404)

    slots = get_available_slots(doctor_id, appt_date)
    return jsonify({'slots': slots})


@appointments.route('/my-appointments')
@login_required
def my_appointments():
    today = date.today()
    all_appts = (
        Appointment.query
        .filter_by(user_id=session['user_id'])
        .order_by(Appointment.date.desc(), Appointment.time_slot.desc())
        .all()
    )
    upcoming = [a for a in all_appts if a.date >= today and a.status != 'cancelled']
    past = [a for a in all_appts if a.date < today or a.status in ('completed', 'cancelled')]
    return render_template('appointments/my_appointments.html',
                           upcoming=upcoming, past=past)


@appointments.route('/cancel/<int:appt_id>', methods=['POST'])
@login_required
def cancel(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.user_id != session['user_id']:
        abort(403)
    if appt.date <= date.today() or appt.status not in ('pending', 'confirmed'):
        flash('Only upcoming pending or confirmed appointments can be cancelled.', 'warning')
        return redirect(url_for('appointments.my_appointments'))
    appt.status = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('appointments.my_appointments'))
