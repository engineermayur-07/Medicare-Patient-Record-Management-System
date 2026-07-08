from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """Requires an authenticated user (role: user)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_role') != 'user':
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def doctor_required(f):
    """Requires an authenticated doctor."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_role') != 'doctor':
            flash('Doctor login required.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Requires an authenticated admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def guest_only(f):
    """Redirect already-logged-in users away from login/register pages."""
    @wraps(f)
    def decorated(*args, **kwargs):
        role = session.get('user_role')
        if role == 'user':
            return redirect(url_for('user.dashboard'))
        if role == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated
