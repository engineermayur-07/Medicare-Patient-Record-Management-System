from flask import Blueprint, render_template
from app.models.service import Service
from app.models.doctor import Doctor

main = Blueprint('main', __name__)


@main.route('/')
def index():
    services = Service.query.filter_by(is_active=True).limit(6).all()
    doctors = Doctor.query.filter_by(is_active=True).limit(4).all()
    return render_template('main/index.html', services=services, doctors=doctors)


@main.route('/services')
def services():
    all_services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    return render_template('main/services.html', services=all_services)


@main.route('/doctors')
def doctors():
    all_doctors = Doctor.query.filter_by(is_active=True).order_by(Doctor.name).all()
    return render_template('main/doctors.html', doctors=all_doctors)
