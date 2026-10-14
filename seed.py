"""
seed.py — Run once to create the admin account and seed sample data.

Usage:
    python seed.py
"""
from datetime import date

from app import create_app
from app.extensions import db
from app.models.admin import Admin
from app.models.doctor import Doctor
from app.models.service import Service
from app.models.user import User
from app.config import Config

app = create_app()


def seed():
    with app.app_context():
        db.create_all()

        # ─── Admin ───
        if not Admin.query.filter_by(email=Config.ADMIN_EMAIL).first():
            admin = Admin(
                username=Config.ADMIN_USERNAME,
                email=Config.ADMIN_EMAIL,
            )
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            print(f'[+] Admin created: {Config.ADMIN_EMAIL} / {Config.ADMIN_PASSWORD}')
        else:
            print('[=] Admin already exists.')

        # ─── Sample Doctors ───
        sample_doctors = [
            {
                'name': 'Priya Sharma', 'email': 'priya@medicare.com',
                'password': 'Doctor@1234',
                'specialization': 'Interventional Cardiologist',
                'department': 'Cardiology',
                'qualification': 'MBBS, MD, DM (Cardiology)',
                'experience_years': 14,
                'bio': 'Expert in cardiac catheterization and complex coronary interventions.',
            },
            {
                'name': 'Rajesh Kumar', 'email': 'rajesh@medicare.com',
                'password': 'Doctor@1234',
                'specialization': 'Pediatric Neurologist',
                'department': 'Neurology',
                'qualification': 'MBBS, MD, DM (Neurology)',
                'experience_years': 10,
                'bio': 'Dedicated to diagnosing and treating neurological disorders in children.',
            },
            {
                'name': 'Aisha Patel', 'email': 'aisha@medicare.com',
                'password': 'Doctor@1234',
                'specialization': 'Orthopedic Surgeon',
                'department': 'Orthopedics',
                'qualification': 'MBBS, MS (Ortho), Fellowship (Sports Medicine)',
                'experience_years': 12,
                'bio': 'Specialist in joint replacement and sports injury management.',
            },
            {
                'name': 'Suresh Menon', 'email': 'suresh@medicare.com',
                'password': 'Doctor@1234',
                'specialization': 'Consultant Dermatologist',
                'department': 'Dermatology',
                'qualification': 'MBBS, MD (Dermatology)',
                'experience_years': 8,
                'bio': 'Treating skin, hair, and nail disorders with modern dermatological techniques.',
            },
        ]

        for d in sample_doctors:
            if not Doctor.query.filter_by(email=d['email']).first():
                doc = Doctor(
                    name=d['name'], email=d['email'],
                    specialization=d['specialization'],
                    department=d['department'],
                    qualification=d['qualification'],
                    experience_years=d['experience_years'],
                    bio=d['bio'],
                    is_active=True,
                )
                doc.set_password(d['password'])
                db.session.add(doc)
                print(f'[+] Doctor: {d["name"]} ({d["email"]})')
            else:
                print(f'[=] Doctor exists: {d["name"]}')

        # ─── Sample Users ───
        sample_users = [
            {
                'name': 'Aarav Mehta', 'email': 'aarav.mehta@example.com',
                'password': 'Patient@1234', 'phone': '9876501001',
                'dob': '1992-04-15', 'medical_conditions': 'None',
            },
            {
                'name': 'Diya Nair', 'email': 'diya.nair@example.com',
                'password': 'Patient@1234', 'phone': '9876501002',
                'dob': '1988-09-22', 'medical_conditions': 'Seasonal allergies',
            },
            {
                'name': 'Rohan Singh', 'email': 'rohan.singh@example.com',
                'password': 'Patient@1234', 'phone': '9876501003',
                'dob': '1979-01-08', 'medical_conditions': 'Hypertension',
            },
            {
                'name': 'Ananya Iyer', 'email': 'ananya.iyer@example.com',
                'password': 'Patient@1234', 'phone': '9876501004',
                'dob': '1995-11-30', 'medical_conditions': 'None',
            },
            {
                'name': 'Vikram Joshi', 'email': 'vikram.joshi@example.com',
                'password': 'Patient@1234', 'phone': '9876501005',
                'dob': '1968-06-17', 'medical_conditions': 'Type 2 diabetes',
            },
            {
                'name': 'Meera Kapoor', 'email': 'meera.kapoor@example.com',
                'password': 'Patient@1234', 'phone': '9876501006',
                'dob': '1985-02-03', 'medical_conditions': 'Asthma',
            },
            {
                'name': 'Arjun Desai', 'email': 'arjun.desai@example.com',
                'password': 'Patient@1234', 'phone': '9876501007',
                'dob': '1990-08-19', 'medical_conditions': 'None',
            },
            {
                'name': 'Kavya Rao', 'email': 'kavya.rao@example.com',
                'password': 'Patient@1234', 'phone': '9876501008',
                'dob': '2001-12-11', 'medical_conditions': 'Iron deficiency anemia',
            },
            {
                'name': 'Sameer Khan', 'email': 'sameer.khan@example.com',
                'password': 'Patient@1234', 'phone': '9876501009',
                'dob': '1975-03-27', 'medical_conditions': 'High cholesterol',
            },
            {
                'name': 'Ishita Verma', 'email': 'ishita.verma@example.com',
                'password': 'Patient@1234', 'phone': '9876501010',
                'dob': '1998-07-06', 'medical_conditions': 'None',
            },
        ]

        for data in sample_users:
            if not User.query.filter_by(email=data['email']).first():
                user = User(
                    name=data['name'],
                    email=data['email'],
                    phone=data['phone'],
                    dob=date.fromisoformat(data['dob']),
                    medical_conditions=data['medical_conditions'],
                    is_verified=True,
                )
                user.set_password(data['password'])
                db.session.add(user)
                print(f'[+] User: {data["name"]} ({data["email"]})')
            else:
                print(f'[=] User exists: {data["name"]}')

        # ─── Sample Services ───
        sample_services = [
            ('Cardiology', 'Cardiology', '❤️',
             'Complete cardiac care including ECG, echocardiography, and interventional procedures.'),
            ('Neurology', 'Neurology', '🧠',
             'Diagnosis and treatment of brain, spinal cord, and nervous system disorders.'),
            ('Orthopaedics', 'Orthopedics', '🦴',
             'Bone and joint care, fracture management, and joint replacement surgery.'),
            ('Paediatrics', 'Pediatrics', '👶',
             'Comprehensive healthcare for infants, children, and adolescents.'),
            ('Dermatology', 'Dermatology', '🌿',
             'Expert skin, hair, and nail care with advanced cosmetic and medical treatments.'),
            ('Oncology', 'Oncology', '🎗️',
             'Cancer diagnosis, chemotherapy, radiation therapy, and survivorship care.'),
            ('Ophthalmology', 'Ophthalmology', '👁️',
             'Complete eye care, cataract surgery, glaucoma treatment, and vision correction.'),
            ('Emergency Care', 'Emergency', '🚑',
             '24/7 emergency services with state-of-the-art trauma and critical care.'),
        ]

        for name, dept, icon, desc in sample_services:
            if not Service.query.filter_by(name=name).first():
                svc = Service(name=name, department=dept, icon=icon, description=desc)
                db.session.add(svc)
                print(f'[+] Service: {name}')

        db.session.commit()
        print('\n✅ Seeding complete!')
        print(f'\nAdmin login: {Config.ADMIN_EMAIL}  /  {Config.ADMIN_PASSWORD}')
        print('Doctor login (all): Doctor@1234')
        print('User login (all): Patient@1234')


if __name__ == '__main__':
    seed()
