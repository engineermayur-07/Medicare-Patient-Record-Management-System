<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=26&duration=3000&pause=800&color=1D4ED8&center=true&vCenter=true&width=700&lines=MediCare+Hospital+Management;Book.+Confirm.+Treat.+Record.;Flask+%7C+PostgreSQL+%7C+Jinja2" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge)
![Jinja2](https://img.shields.io/badge/Jinja2-Templates-B41717?style=for-the-badge&logo=jinja&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-AJAX-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Gemini](https://img.shields.io/badge/Google%20Gemini-AI%20Assistant-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

### 🏥 A role-based, server-rendered hospital management web application

[🌐 **Live Demo**](https://medicare-kl5d.onrender.com/) &nbsp;•&nbsp; [📖 **Code Walkthrough**](explanation.md) &nbsp;•&nbsp; [🐛 **Report a Bug**](https://github.com/engineermayur-07/Medicare-Patient-Record-Management-System/issues)

</div>

---

## 📌 About

**MediCare** connects patients, doctors and hospital administrators on one platform. Patients register with email OTP verification and book appointments; doctors confirm, complete or cancel them and upload medical records; admins manage doctors and hospital services.

It was built by a team of four as a **Community Engagement Project** at Sanjivani College of Engineering, Shirdi.

It is a **server-rendered full-stack app**: Flask renders Jinja2 templates, with a little vanilla JavaScript (AJAX) for live slot loading. There is no React or separate frontend API.

> ⏳ The demo is hosted on Render, so the first load may take a little while if the app has been idle.

---

## 📸 Screenshots

| Home Page | Patient Dashboard |
|:---:|:---:|
| ![Home](home.png) | ![Patient](patient-dashboard.png) |

| Doctor Dashboard | Admin Dashboard |
|:---:|:---:|
| ![Doctor](doctor-dashboard.png) | ![Admin](admin-dashboard.png) |

---

## ✨ Features

### 🧑‍⚕️ Patient
- Register with **email OTP verification** (10-minute expiry)
- Secure login with hashed passwords
- Browse doctors and services, book appointments with **live slot availability**
- View and cancel own appointments
- Access personal **medical history** and download or view records
- Profile page, payments / medical fees
- **AI Health Assistant** powered by Google Gemini

### 👨‍⚕️ Doctor
- Dashboard with today's patients, pending confirmations and total appointments
- **Confirm → Complete** or **Cancel** appointments
- Upload medical records (PDF, PNG, JPG) against an appointment

### 🛡️ Admin
- Dashboard statistics (patients, active doctors, appointments, pending)
- Add, activate/deactivate and delete **doctors**
- Add, activate/deactivate and delete **services**
- View patients, recent appointments and medical fees

### 🔐 Security
- Password hashing (`werkzeug.security`)
- Role-based access with decorators (`login_required`, `doctor_required`, `admin_required`, `guest_only`)
- **CSRF protection** on all POST forms (Flask-WTF)
- Ownership checks (`403`) so users only touch their own data
- Server-side re-validation of appointment slots (prevents double booking)
- File-extension whitelist, `secure_filename` and UUID-based stored names

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python + Flask | Routing and business rules |
| ORM | Flask-SQLAlchemy | Python classes ↔ database rows |
| Database | PostgreSQL | Users, doctors, appointments, records, services |
| Templates | Jinja2 | Dynamic server-side HTML |
| Frontend | HTML, CSS, JavaScript | Layout, responsive UI, AJAX slots, file previews |
| Migrations | Flask-Migrate + Alembic | Versioned schema changes |
| Email | Resend API (via `requests`) | OTP and fee reminder emails |
| AI | Google Gemini (`gemini-2.5-flash`) | Health Assistant |
| Server | Gunicorn | Production WSGI server |

---

## 🏗️ Architecture

```text
┌──────────────┐   HTTP    ┌────────────────────────────────────────┐
│   Browser    │ ────────► │               Flask App                │
│ HTML/CSS/JS  │           │                                        │
└──────▲───────┘           │  Blueprints (Controllers)              │
       │                   │  main · auth · user · appointments     │
       │  Rendered HTML    │  doctor · admin · records              │
       │  / JSON (AJAX)    │            │                           │
       │                   │            ▼                           │
       │                   │  Models (SQLAlchemy)                   │
       └────────────────── │  User · Doctor · Admin · Appointment   │
                           │  MedicalRecord · OTP · Service         │
         Jinja2 Templates  │            │                           │
         (Views)           └────────────┼───────────────┬───────────┘
                                        ▼               ▼
                      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                      │  PostgreSQL  │  │  Resend API  │  │  Gemini API  │
                      └──────────────┘  └──────────────┘  └──────────────┘
                                ┌──────────────────────────────┐
                                │ uploads/medical_records/     │
                                │ (record files stored on disk)│
                                └──────────────────────────────┘
```

**Appointment lifecycle**

```text
pending ──► confirmed ──► completed
   │            │
   └────────────┴──────► cancelled
```

---

## 📁 Project Structure

```text
hospital_app/
├── run.py                  # Entry point
├── seed.py                 # Admin, sample doctors and services
├── requirements.txt
├── pyproject.toml
├── vercel.json
├── explanation.md
├── .env.example
├── app/
│   ├── __init__.py         # create_app() factory
│   ├── config.py
│   ├── extensions.py       # db, migrate, csrf
│   ├── models/             # user, doctor, admin, appointment, medical_record, otp, service
│   ├── blueprints/         # main, auth, user, appointments, doctor, admin, records
│   ├── utils/              # decorators, helpers, email
│   ├── templates/
│   └── static/             # css/style.css, js/main.js
└── migrations/
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- PostgreSQL
- A [Resend](https://resend.com) API key (for OTP emails)
- A [Google Gemini](https://aistudio.google.com/) API key (for the Health Assistant)

### Installation

```bash
# 1. Clone
git clone https://github.com/engineermayur-07/Medicare-Patient-Record-Management-System.git
cd Medicare-Patient-Record-Management-System

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

# 3. Dependencies
pip install -r requirements.txt

# 4. Environment variables
cp .env.example .env            # then edit the values

# 5. Create the database tables
flask db upgrade

# 6. Seed sample data (admin, doctors, services)
python seed.py

# 7. Run
python run.py
```

Open **http://localhost:5000**

### Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Signs session cookies |
| `DATABASE_URL` | PostgreSQL connection string (`postgresql+psycopg://user:password@host:5432/dbname`) |
| `RESEND_API_KEY` | Resend API key for emails |
| `RESEND_FROM_EMAIL` | Sender address for OTP and reminder emails |
| `ADMIN_USERNAME` | Admin name created by `seed.py` |
| `ADMIN_EMAIL` | Admin login email |
| `ADMIN_PASSWORD` | Admin login password |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GEMINI_MODEL` | Gemini model name (e.g. `gemini-2.5-flash`) |

> ⚠️ Never commit real keys, passwords or database URLs. Keep real values only in your local `.env`, and use placeholders in `.env.example`.

### Demo Accounts

The admin account is created from the `ADMIN_*` values in your `.env` when you run `seed.py`, along with sample doctors and services (see `seed.py`). Register a new patient through the OTP flow to try the patient side.

---

## 📖 Learn How It Works

A line-by-line explanation of the control flow, models, sessions, decorators, Jinja, JavaScript `fetch`, file uploads and migrations is in **[explanation.md](explanation.md)**. It is written so you can learn Flask by reading a real project.

---

## 🗺️ Roadmap

- [ ] Automated tests
- [ ] Move uploaded records to cloud storage for production
- [ ] Rate limiting on login and OTP endpoints
- [ ] Email reminders for upcoming appointments

---

## 👥 Team

Built by students of **Sanjivani College of Engineering, Kopargaon** (SY B.Tech) as part of a Community Engagement Project:

- **Mayur Gund**
- **Rohit Khokale**
- **Danish Shaikh**
- **Abhijit Fatangare**

---

## 📬 Contact

<div align="center">

**Mayur Gund** — Backend Developer

[![Email](https://img.shields.io/badge/Email-mgund1920%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:mgund1920@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-engineermayur--07-181717?style=for-the-badge&logo=github)](https://github.com/engineermayur-07)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-mgund1920-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/mgund1920)
[![Blog](https://img.shields.io/badge/Blog-engineermayur.blogspot.com-FF5722?style=for-the-badge&logo=blogger&logoColor=white)](https://engineermayur.blogspot.com)

⭐ If you found this project useful, consider giving it a star!

</div>
