from datetime import datetime
from uuid import uuid4

from flask import (Blueprint, abort, current_app, flash, jsonify, redirect,
                   render_template, request, session, url_for, send_file)

from app.extensions import db
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.utils.decorators import login_required
from app.utils.receipts import create_receipt
from app.utils.validation import parse_medical_fee, validate_payment_details


payments = Blueprint('payments', __name__)


def _get_user_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if payment.user_id != session['user_id']:
        abort(403)
    return payment


def _create_simulated_order(payment):
    if payment.razorpay_order_id:
        return payment.razorpay_order_id

    payment.razorpay_order_id = (
        f'sim_order_{payment.id}_{uuid4().hex[:12]}'
    )
    db.session.commit()
    return payment.razorpay_order_id


def _mark_payment_paid(payment, simulated_payment_id):
    payment.razorpay_payment_id = simulated_payment_id
    payment.razorpay_signature = 'simulated_backend_verification'
    payment.status = 'paid'
    payment.paid_at = datetime.utcnow()
    payment.receipt_path = create_receipt(payment)
    db.session.commit()


def _payment_payload(payment):
    return {
        'payment_id': payment.id,
        'order_id': payment.razorpay_order_id,
        'amount': payment.amount_paise,
        'currency': payment.currency,
        'description': payment.description,
    }


@payments.route('')
@login_required
def index():
    all_payments = (
        Payment.query.filter_by(user_id=session['user_id'])
        .order_by(Payment.created_at.desc()).all()
    )
    return render_template('payments/index.html', payments=all_payments)


@payments.route('/appointment/<int:appointment_id>/pay')
@login_required
def pay_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.user_id != session['user_id']:
        abort(403)
    if appointment.status == 'cancelled':
        flash('Cancelled appointments cannot be paid for.', 'warning')
        return redirect(url_for('appointments.my_appointments'))

    payment = Payment.query.filter_by(
        user_id=session['user_id'],
        appointment_id=appointment.id,
        fee_type='appointment',
    ).first()
    if not payment:
        amount, amount_error = parse_medical_fee(
            str(current_app.config['APPOINTMENT_FEE'])
        )
        if amount_error:
            current_app.logger.error(
                'Invalid APPOINTMENT_FEE configuration: %s', amount_error
            )
            flash('This appointment fee is not configured correctly.', 'danger')
            return redirect(url_for('appointments.my_appointments'))

        payment = Payment(
            user_id=session['user_id'],
            appointment_id=appointment.id,
            fee_type='appointment',
            description=f'Appointment with Dr. {appointment.doctor.name}',
            amount=amount,
        )
        db.session.add(payment)
        db.session.commit()
    if payment.status == 'paid':
        flash('This appointment has already been paid.', 'info')
        return redirect(url_for('payments.index'))

    return render_template('payments/checkout.html', payment=payment)


@payments.route('/fee/<int:payment_id>/pay')
@login_required
def pay_fee(payment_id):
    payment = _get_user_payment(payment_id)
    if payment.fee_type != 'medical_fee' or payment.status == 'paid':
        return redirect(url_for('payments.index'))
    return render_template('payments/checkout.html', payment=payment)


@payments.route('/api/create-order', methods=['POST'])
@login_required
def api_create_order():
    data = request.get_json(silent=True) or {}
    payment_id = data.get('payment_id')
    if not isinstance(payment_id, int):
        return jsonify({'error': 'A valid payment_id is required.'}), 400

    payment = _get_user_payment(payment_id)
    if payment.status == 'paid':
        return jsonify({'error': 'This payment is already completed.'}), 409
    if payment.fee_type not in ('appointment', 'medical_fee'):
        return jsonify({'error': 'This payment type is not supported.'}), 400

    if payment.status == 'failed':
        payment.status = 'pending'
        payment.razorpay_order_id = None
        payment.razorpay_payment_id = None
        payment.razorpay_signature = None
        db.session.commit()

    if not payment.razorpay_order_id:
        _create_simulated_order(payment)
    return jsonify(_payment_payload(payment))


@payments.route('/api/confirm', methods=['POST'])
@login_required
def api_confirm():
    data = request.get_json(silent=True) or {}
    payment_id = data.get('payment_id')
    order_id = str(data.get('order_id', ''))
    outcome = data.get('outcome', 'success')
    method = data.get('method')
    details = data.get('details', {})
    valid_methods = ('card', 'upi', 'qr', 'netbanking')
    if (
        not isinstance(payment_id, int)
        or outcome not in ('success', 'failure')
        or method not in valid_methods
    ):
        return jsonify({'error': 'Invalid payment confirmation data.'}), 400

    payment = _get_user_payment(payment_id)
    if payment.status == 'paid':
        return jsonify({'error': 'This payment is already completed.'}), 409
    if not payment.razorpay_order_id or order_id != payment.razorpay_order_id:
        return jsonify({'error': 'Invalid simulated order.'}), 400
    if outcome == 'success':
        details_error = validate_payment_details(method, details)
        if details_error:
            return jsonify({'error': details_error}), 400

    if outcome == 'failure':
        payment.status = 'failed'
        db.session.commit()
        return jsonify({
            'status': 'failed',
            'message': 'Payment failed. You can try again.',
        })

    simulated_payment_id = f'pay_{uuid4().hex[:16]}'
    _mark_payment_paid(payment, simulated_payment_id)
    return jsonify({
        'status': 'paid',
        'message': 'Payment successful.',
        'method': method,
        'receipt_url': url_for('payments.receipt', payment_id=payment.id),
    })


@payments.route('/receipt/<int:payment_id>')
@login_required
def receipt(payment_id):
    payment = _get_user_payment(payment_id)
    if payment.status != 'paid' or not payment.receipt_path:
        abort(404)
    return send_file(payment.receipt_path, as_attachment=True,
                     download_name=f'MediCare-receipt-{payment.id}.html')
