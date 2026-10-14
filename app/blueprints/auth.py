from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.extensions import db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.admin import Admin
from app.utils.helpers import create_otp
from app.utils.helpers import verify_otp as check_otp
from app.utils.email import send_otp_email
from app.utils.decorators import guest_only
from app.utils.validation import validate_password_strength

auth = Blueprint('auth', __name__)


# ─────────────────────────── Registration ────────────────────────────

@auth.route('/register', methods=['GET', 'POST'])
@guest_only
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Basic validation
        if not all([name, email, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        password_error = validate_password_strength(password)
        if password_error:
            flash(password_error, 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'danger')
            return render_template('auth/register.html')

        # Create unverified user
        user = User(name=name, email=email, phone=phone, is_verified=False)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Generate & send OTP
        code = create_otp(email, purpose='registration',
                          expiry_minutes=current_app.config['OTP_EXPIRY_MINUTES'])
        sent = send_otp_email(email, code, name)

        if not sent:
            flash('Could not send verification email. Please try again.', 'danger')
            db.session.delete(user)
            db.session.commit()
            return render_template('auth/register.html')

        # Temporarily store email in session for the OTP step
        session['pending_verify_email'] = email
        flash(f'A 6-digit OTP was sent to {email}. It expires in 10 minutes.', 'info')
        return redirect(url_for('auth.verify_otp'))

    return render_template('auth/register.html')


# ─────────────────────────── OTP Verification ────────────────────────

@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('pending_verify_email')
    if not email:
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        code = request.form.get('otp', '').strip()

        if not code or len(code) != 6:
            flash('Please enter the 6-digit OTP.', 'danger')
            return render_template('auth/verify_otp.html', email=email)

        if check_otp(email, code, purpose='registration'):
            user = User.query.filter_by(email=email).first()
            if user:
                user.is_verified = True
                db.session.commit()
                session.pop('pending_verify_email', None)
                flash('Email verified! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired OTP. Please try again.', 'danger')

    return render_template('auth/verify_otp.html', email=email)


# ─────────────────────────── Resend OTP ──────────────────────────────

@auth.route('/resend-otp', methods=['POST'])
def resend_otp():
    email = session.get('pending_verify_email')
    if not email:
        return redirect(url_for('auth.register'))

    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect(url_for('auth.register'))

    code = create_otp(email, purpose='registration',
                      expiry_minutes=current_app.config['OTP_EXPIRY_MINUTES'])
    send_otp_email(email, code, user.name)
    flash('A new OTP has been sent to your email.', 'info')
    return redirect(url_for('auth.verify_otp'))


# ─────────────────────────── Login ───────────────────────────────────

@auth.route('/login', methods=['GET', 'POST'])
@guest_only
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('auth/login.html')

        # Check admin first (by email)
        admin = Admin.query.filter_by(email=email).first()
        if admin and admin.check_password(password):
            session.clear()
            session['user_id'] = admin.id
            session['user_role'] = 'admin'
            session['user_name'] = admin.username
            flash(f'Welcome back, {admin.username}!', 'success')
            return redirect(url_for('admin.dashboard'))

        # Check doctor
        doctor = Doctor.query.filter_by(email=email).first()
        if doctor and doctor.check_password(password):
            if not doctor.is_active:
                flash('Your doctor account has been deactivated. Contact admin.', 'danger')
                return render_template('auth/login.html')
            session.clear()
            session['user_id'] = doctor.id
            session['user_role'] = 'doctor'
            session['user_name'] = doctor.name
            flash(f'Welcome, Dr. {doctor.name}!', 'success')
            return redirect(url_for('doctor.dashboard'))

        # Check user
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_verified:
                session['pending_verify_email'] = email
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('auth.verify_otp'))
            session.clear()
            session['user_id'] = user.id
            session['user_role'] = 'user'
            session['user_name'] = user.name
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('user.dashboard'))

        flash('Incorrect email or password.', 'danger')
    return render_template('auth/login.html')


# ─────────────────────────── Logout ──────────────────────────────────

@auth.route('/logout')
def logout():
    name = session.get('user_name', '')
    session.clear()
    flash(f'You have been logged out, {name}.', 'info')
    return redirect(url_for('main.index'))
