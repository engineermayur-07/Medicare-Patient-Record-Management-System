# MediCare Hospital Management System — Project Explanation

## 1. What this project is

This is a hospital management web application called MediCare.

It allows:

- Patients to register and verify their email using an OTP.
- Patients to log in and book appointments.
- Doctors to view, confirm, complete, or cancel appointments.
- Doctors to upload medical records.
- Patients to view their medical history.
- Administrators to manage doctors and hospital services.

The project uses:

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python + Flask | Receives browser requests and applies business rules |
| Database access | Flask-SQLAlchemy | Converts Python objects into database rows |
| Database | PostgreSQL | Stores users, doctors, appointments, records, and services |
| HTML rendering | Jinja2 templates | Generates HTML dynamically from Python data |
| Styling | CSS | Controls appearance and responsive layout |
| Browser behavior | JavaScript | Handles menus, date slots, file previews, and AJAX |
| Database migrations | Flask-Migrate + Alembic | Creates and updates database tables |
| Email | Resend API via Python `requests` | Sends OTP verification and fee reminder emails |

This is a **server-rendered full-stack application**. It does not use React, Vue, or a separate frontend API.

---

## 2. Project structure

```text
hospital_app/
│
├── run.py
├── seed.py
├── requirements.txt
├── .env
├── .env.example
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── admin.py
│   │   ├── appointment.py
│   │   ├── medical_record.py
│   │   ├── otp.py
│   │   └── service.py
│   │
│   ├── blueprints/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── appointments.py
│   │   ├── doctor.py
│   │   ├── admin.py
│   │   └── records.py
│   │
│   ├── utils/
│   │   ├── decorators.py
│   │   ├── helpers.py
│   │   └── email.py
│   │
│   ├── templates/
│   └── static/
│       ├── css/style.css
│       └── js/main.js
│
└── migrations/
    ├── env.py
    └── versions/6470e82d711d_init.py
```

The `venv` directory contains installed Python packages. You normally do not study or modify it.

---

## 3. How the application starts

The starting file is `run.py`:

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

### `from app import create_app`

This imports the `create_app` function from `app/__init__.py`.

### `app = create_app()`

This creates the Flask application.

This style is called the **application factory pattern**. Instead of creating the Flask application globally, the project creates it through a function:

```python
def create_app(config_class=Config):
```

This makes the application easier to configure and test.

### `if __name__ == '__main__'`

Every Python file has a special variable called `__name__`.

When you run:

```text
python run.py
```

Python sets:

```python
__name__ == '__main__'
```

Therefore:

```python
app.run(debug=True)
```

executes.

If another file imports `run.py`, the condition is false, so the server does not start automatically.

---

## 4. Application creation flow

Inside `app/__init__.py`:

```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
```

This:

1. Creates a Flask object.
2. Loads configuration.
3. Connects database extensions.
4. Registers URL routes.

The extensions are defined in `extensions.py`:

```python
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
```

These objects are created without an application first. Later they are connected:

```python
db.init_app(app)
migrate.init_app(app, db)
csrf.init_app(app)
```

This is called the **extension initialization pattern**.

The extensions provide:

- `db` for database operations.
- `migrate` for database migrations.
- `csrf` for protection against Cross-Site Request Forgery.

The models are imported:

```python
from .models import user, doctor, admin, otp, appointment, service, medical_record
```

This is important because SQLAlchemy must know about all model classes before migrations can detect database tables.

Finally, blueprints are registered:

```python
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
```

A blueprint groups related routes.

For example:

```python
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
```

Because the blueprint is registered with:

```python
url_prefix='/auth'
```

the real URL becomes:

```text
/auth/login
```

---

## 5. The request-response control flow

Whenever a user visits a URL:

```text
Browser → Flask route → Database/business logic → Template → HTML response → Browser
```

For example, for:

```text
GET /user/dashboard
```

the flow is:

1. The browser sends a request.
2. Flask finds the matching route.
3. `login_required` checks the session.
4. The route queries the database.
5. Python passes data into a Jinja template.
6. Jinja generates HTML.
7. Flask sends HTML back to the browser.
8. The browser displays it.

A route usually looks like this:

```python
@user.route('/dashboard')
@login_required
def dashboard():
    u = User.query.get_or_404(session['user_id'])
    return render_template('user/dashboard.html', user=u)
```

A route can return:

- HTML using `render_template`.
- A redirect using `redirect`.
- JSON using `jsonify`.
- A file using `send_file`.
- An error using `abort`.

---

## 6. Database models

Models describe database tables using Python classes.

For example:

```python
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
```

This means:

- `User` is a Python class.
- `users` is the database table.
- `id` is an integer primary key.
- `name` is a required string.

### `User`

Represents a patient.

Important fields:

```text
name
email
password_hash
phone
dob
is_verified
created_at
```

Passwords are never stored directly. Instead:

```python
user.set_password(password)
```

uses:

```python
generate_password_hash(password)
```

During login:

```python
user.check_password(password)
```

uses:

```python
check_password_hash(...)
```

### `Doctor`

Represents a doctor.

Important fields:

```text
name
email
password_hash
specialization
department
qualification
experience_years
bio
is_active
```

A doctor can have many appointments:

```python
appointments = db.relationship(
    'Appointment',
    backref='doctor',
    lazy='dynamic',
    cascade='all, delete-orphan'
)
```

This means:

```python
appointment.doctor
```

returns the doctor connected to an appointment.

### `Admin`

Represents an administrator. Admins can manage doctors and services.

### `Appointment`

Connects a patient and a doctor:

```python
user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
```

An appointment includes:

```text
date
time_slot
status
reason
notes
```

Possible statuses:

```text
pending
confirmed
cancelled
completed
```

### `MedicalRecord`

Represents prescriptions, lab tests, imaging, diagnosis, and other records.

It connects:

- A patient.
- A doctor.
- Optionally an appointment.
- An optional file stored on disk.

### `OTP`

Stores one-time password verification codes:

```text
email
code
purpose
expires_at
is_used
```

### `Service`

Represents hospital services such as Cardiology, Neurology, Dermatology, and Emergency Care.

---

## 7. SQLAlchemy syntax

The project uses Python instead of writing SQL manually.

```python
User.query.filter_by(email=email).first()
```

Equivalent SQL idea:

```sql
SELECT * FROM users WHERE email = ... LIMIT 1;
```

Common methods:

```python
User.query.all()
```

Gets all users.

```python
User.query.first()
```

Gets the first user.

```python
User.query.get(id)
```

Gets a user by primary key.

```python
User.query.get_or_404(id)
```

Gets a user, or automatically returns HTTP 404 if not found.

```python
User.query.filter_by(email=email).first()
```

Filters using exact equality.

```python
Appointment.query.filter(
    Appointment.date >= today,
    Appointment.status.in_(['pending', 'confirmed'])
)
```

Uses more advanced conditions.

To save:

```python
db.session.add(user)
db.session.commit()
```

To delete:

```python
db.session.delete(user)
db.session.commit()
```

A database session represents the current group of database changes.

---

## 8. Authentication and sessions

The project supports three roles:

```text
user
doctor
admin
```

After successful login, the role is stored in Flask's session:

```python
session['user_id'] = user.id
session['user_role'] = 'user'
session['user_name'] = user.name
```

The session allows later requests to remember who is logged in.

The session is usually stored in a signed browser cookie. The `SECRET_KEY` prevents users from safely modifying session data.

To read session values:

```python
session.get('user_role')
```

To remove everything:

```python
session.clear()
```

---

## 9. Decorators and access control

The file `app/utils/decorators.py` contains decorators.

Example:

```python
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_role') != 'user':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated
```

A decorator is a function that wraps another function.

This:

```python
@login_required
def dashboard():
```

is conceptually similar to:

```python
dashboard = login_required(dashboard)
```

The wrapper checks access before the original route runs.

The project has:

```python
@login_required
```

for patients,

```python
@doctor_required
```

for doctors, and:

```python
@admin_required
```

for administrators.

The `guest_only` decorator prevents logged-in users from opening login and registration pages.

---

## 10. Patient registration flow

The registration page is:

```text
GET /auth/register
```

The template contains:

```html
<form method="POST" action="{{ url_for('auth.register') }}">
```

The user submits the form.

The route receives data:

```python
name = request.form.get('name', '').strip()
email = request.form.get('email', '').strip().lower()
phone = request.form.get('phone', '').strip()
password = request.form.get('password', '')
```

Important Python concepts:

- `request.form` contains submitted form fields.
- `.get()` safely reads a field.
- `.strip()` removes surrounding whitespace.
- `.lower()` converts text to lowercase.

Validation:

```python
if not all([name, email, password, confirm]):
```

`all()` returns `True` only if every item is truthy.

Password comparison:

```python
if password != confirm:
```

The user is created:

```python
user = User(
    name=name,
    email=email,
    phone=phone,
    is_verified=False
)
```

Then the password is hashed:

```python
user.set_password(password)
```

An OTP is created:

```python
code = create_otp(email, purpose='registration', expiry_minutes=10)
```

The OTP is emailed:

```python
send_otp_email(email, code, name)
```

The email is temporarily stored in the session:

```python
session['pending_verify_email'] = email
```

The user is redirected:

```python
return redirect(url_for('auth.verify_otp'))
```

---

## 11. OTP verification flow

The user submits the OTP to:

```text
POST /auth/verify-otp
```

The code is checked:

```python
if check_otp(email, code, purpose='registration'):
```

The helper searches for:

- Matching email.
- Matching code.
- Correct purpose.
- Unused OTP.

Then it checks expiration:

```python
datetime.utcnow() < self.expires_at
```

If valid:

```python
otp.is_used = True
user.is_verified = True
db.session.commit()
```

The user can now log in.

---

## 12. Login flow

The login route checks three account types.

First, admin:

```python
admin = Admin.query.filter_by(email=email).first()
```

Then doctor:

```python
doctor = Doctor.query.filter_by(email=email).first()
```

Then patient:

```python
user = User.query.filter_by(email=email).first()
```

When credentials are correct, the session is populated:

```python
session.clear()
session['user_id'] = user.id
session['user_role'] = 'user'
session['user_name'] = user.name
```

Then the user is redirected to the correct dashboard:

```text
admin   → /admin/dashboard
doctor  → /doctor/dashboard
patient → /user/dashboard
```

---

## 13. Appointment booking flow

### Step 1: Select a doctor

```text
GET /appointments/book
```

The backend retrieves active doctors:

```python
doctors = Doctor.query.filter_by(is_active=True).order_by(Doctor.name).all()
```

The template loops over them:

```jinja2
{% for doctor in doctors %}
```

### Step 2: Select date and time

```text
GET /appointments/book/<doctor_id>
```

The page contains JavaScript.

When the user changes the date, JavaScript calls:

```javascript
fetch(`/appointments/slots/${doctorId}/${date}`)
```

This is an AJAX request. The page does not reload.

The backend endpoint returns JSON:

```python
return jsonify({'slots': slots})
```

The browser receives the JSON and creates `<option>` elements for the time dropdown.

### Step 3: Submit appointment

The backend validates:

```python
if not raw_date or not time_slot:
```

It converts the date:

```python
appt_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
```

The appointment must be in the future:

```python
if appt_date <= date.today():
```

The backend checks availability again:

```python
available = get_available_slots(doctor_id, appt_date)
```

This second check is important because another user may have booked the same slot after the browser loaded the original list.

The appointment is saved:

```python
appt = Appointment(
    user_id=session['user_id'],
    doctor_id=doctor_id,
    date=appt_date,
    time_slot=time_slot,
    status='pending'
)
```

The doctor must confirm it.

---

## 14. Appointment status flow

The normal lifecycle is:

```text
pending → confirmed → completed
```

Cancellation is possible from:

```text
pending → cancelled
confirmed → cancelled
```

Doctors use:

```text
POST /doctor/appointments/<id>/confirm
POST /doctor/appointments/<id>/complete
POST /doctor/appointments/<id>/cancel
```

The route verifies that the appointment belongs to the logged-in doctor:

```python
if appt.doctor_id != session['user_id']:
    abort(403)
```

`403` means the user is authenticated but not authorized.

Patients can cancel their own appointments:

```python
if appt.user_id != session['user_id']:
    abort(403)
```

This is an ownership check.

---

## 15. Medical record flow

Doctors upload a record at:

```text
GET /records/upload/<appointment_id>
POST /records/upload/<appointment_id>
```

The doctor must own the appointment:

```python
if appt.doctor_id != session['user_id']:
    abort(403)
```

Allowed file extensions are checked:

```python
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
```

The filename is cleaned:

```python
secure_filename(file.filename)
```

A unique filename is generated using:

```python
uuid.uuid4().hex
```

The file is saved to:

```text
uploads/medical_records/user_<id>/
```

The database stores metadata:

```text
file_path
file_name
file_size
file_mime
```

The actual file is stored on disk, not inside PostgreSQL.

Files can be downloaded through:

```text
/download/<record_id>
```

or displayed inside the browser using:

```text
/view/<record_id>
```

Access is checked using `_can_access_record()`:

- Admins can access all records.
- Patients can access their own records.
- Doctors can access records they uploaded.

---

## 16. Admin flow

Administrators can:

- View dashboard statistics.
- Add doctors.
- Activate or deactivate doctors.
- Delete doctors.
- Add services.
- Activate or deactivate services.
- Delete services.

The admin dashboard calculates values such as:

```python
total_users = User.query.count()
total_doctors = Doctor.query.filter_by(is_active=True).count()
pending_appts = Appointment.query.filter_by(status='pending').count()
```

Admin forms submit data using HTTP POST.

For example:

```python
if request.method == 'POST':
```

The same route can display a form for `GET` and process the form for `POST`.

---

## 17. Templates and Jinja syntax

Templates are HTML files with Jinja expressions.

### Output syntax

```jinja2
{{ user.name }}
```

Prints a value.

```jinja2
{{ appt.status|title }}
```

The `|title` part is a Jinja filter. It changes:

```text
pending
```

into:

```text
Pending
```

### Conditions

```jinja2
{% if user.phone %}
    {{ user.phone }}
{% endif %}
```

Equivalent Python idea:

```python
if user.phone:
    print(user.phone)
```

Multiple branches:

```jinja2
{% if role == 'user' %}
{% elif role == 'doctor' %}
{% else %}
{% endif %}
```

### Loops

```jinja2
{% for appt in appointments %}
    {{ appt.date }}
{% endfor %}
```

Equivalent Python idea:

```python
for appt in appointments:
    print(appt.date)
```

### Template inheritance

Most pages start with:

```jinja2
{% extends 'base.html' %}
```

The common layout is in `base.html`.

Child templates fill named blocks:

```jinja2
{% block content %}
    Page-specific HTML
{% endblock %}
```

This avoids repeating the navbar and footer in every page.

### URL generation

```jinja2
{{ url_for('auth.login') }}
```

Flask creates the correct URL from the route name. This is safer than hardcoding:

```html
<a href="/auth/login">
```

---

## 18. HTML syntax used here

HTML describes page structure.

```html
<form method="POST" action="/auth/login">
```

This means that submitting the form sends a POST request.

```html
<input type="email" name="email">
```

Creates an email input. The `name` value is the key Flask reads:

```python
request.form.get('email')
```

```html
<button type="submit">
```

Submits the form.

```html
class="btn btn-primary"
```

Applies CSS classes.

```html
id="hamburger"
```

Allows JavaScript to find the element:

```javascript
document.getElementById('hamburger')
```

The hidden CSRF field:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

protects POST forms from unauthorized websites submitting requests on behalf of users.

---

## 19. JavaScript syntax used here

The main JavaScript file is:

```text
app/static/js/main.js
```

### Variables

```javascript
const hamburger = document.getElementById('hamburger');
```

`const` creates a variable that cannot be reassigned.

```javascript
let value = 10;
```

`let` creates a variable that can be reassigned.

### Conditions

```javascript
if (hamburger) {
    ...
}
```

JavaScript uses braces instead of Python indentation.

Python:

```python
if hamburger:
    do_something()
```

JavaScript:

```javascript
if (hamburger) {
  doSomething();
}
```

### Functions

```javascript
function toggleEye(inputId, btn) {
  ...
}
```

Arrow function:

```javascript
() => {
  ...
}
```

This is commonly used as a callback.

### DOM events

```javascript
hamburger.addEventListener('click', () => {
```

This means: when the button is clicked, execute this function.

### DOM modification

```javascript
navLinks.classList.toggle('open');
```

Adds or removes the CSS class `open`.

```javascript
element.textContent = 'Hello';
```

Changes visible text.

### Loops

```javascript
document.querySelectorAll('.flash').forEach(el => {
```

Finds all elements with class `flash` and runs a function for each one.

### Async and await

```javascript
const res = await fetch(url);
const data = await res.json();
```

`fetch()` performs a network request.

`await` pauses the asynchronous function until the request completes.

The function is marked:

```javascript
async function () {
```

This is JavaScript's way of handling operations that take time, such as HTTP requests.

### Destructuring

```javascript
const [h, m] = slot.split(':');
```

If:

```javascript
slot = '09:30'
```

then:

```javascript
h = '09'
m = '30'
```

### Template literals

```javascript
`/appointments/slots/${doctorId}/${date}`
```

Backticks allow variables inside strings using:

```javascript
${variable}
```

---

## 20. CSS syntax

The CSS file is:

```text
app/static/css/style.css
```

CSS uses selectors and declarations:

```css
.btn-primary {
  background: blue;
  color: white;
}
```

Meaning:

- Select elements with class `btn-primary`.
- Set their background color to blue.
- Set their text color to white.

A class selector starts with:

```css
.
```

An ID selector starts with:

```css
#
```

Example:

```css
#hamburger {
}
```

The JavaScript adds and removes CSS classes to change the interface:

```javascript
navLinks.classList.toggle('open');
```

CSS then controls how `.open` looks on mobile.

---

## 21. Configuration and environment variables

`config.py` loads `.env`:

```python
load_dotenv()
```

Then reads variables:

```python
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
```

This keeps configuration outside source code.

Important configuration values:

```text
SQLALCHEMY_DATABASE_URI
SECRET_KEY
RESEND_API_KEY
RESEND_FROM_EMAIL
UPLOAD_FOLDER
MAX_CONTENT_LENGTH
ALLOWED_EXTENSIONS
```

The `.env` file should not be committed to Git because it can contain passwords and credentials.

---

## 22. Database migrations

The migration file:

```text
migrations/versions/6470e82d711d_init.py
```

contains instructions such as:

```python
op.create_table('users', ...)
```

`upgrade()` creates tables.

`downgrade()` removes them.

This allows the database schema to be version-controlled.

The project also has:

```python
db.create_all()
```

inside `seed.py`.

That directly creates missing tables. In a production application, migrations are normally preferred over relying only on `create_all()`.

---

## 23. Seeding sample data

Run:

```text
python seed.py
```

The seed script:

1. Creates database tables.
2. Creates an admin account.
3. Creates sample doctors.
4. Creates sample hospital services.
5. Avoids duplicates by checking whether records already exist.

The `for` loop:

```python
for d in sample_doctors:
```

processes each dictionary.

The dictionary syntax:

```python
{
    'name': 'Priya Sharma',
    'email': 'priya@medicare.com'
}
```

stores key-value pairs.

Tuple unpacking is used here:

```python
for name, dept, icon, desc in sample_services:
```

Each tuple is split into four variables.

---

## 24. Complete example: patient booking

The complete control flow is:

```text
Patient opens /appointments/book
        ↓
Flask executes select_doctor()
        ↓
Database returns active doctors
        ↓
Jinja renders select_doctor.html
        ↓
Patient chooses a doctor
        ↓
Browser opens /appointments/book/3
        ↓
Flask renders the booking form
        ↓
JavaScript requests /appointments/slots/3/2026-09-10
        ↓
Flask calculates free slots
        ↓
Flask returns JSON
        ↓
JavaScript fills the dropdown
        ↓
Patient submits the form
        ↓
Flask validates the date and slot
        ↓
Appointment row is inserted
        ↓
Patient is redirected to /appointments/my-appointments
```

---

## 25. Most important concepts to learn from this project

To understand this project deeply, learn these topics in this order:

1. Python functions, classes, imports, decorators, exceptions, and list comprehensions.
2. HTTP methods: GET and POST.
3. HTML forms and browser requests.
4. Flask routes and templates.
5. Jinja conditions, loops, filters, and inheritance.
6. SQL and relational database concepts.
7. SQLAlchemy models, relationships, and queries.
8. Sessions and authentication.
9. JavaScript DOM manipulation and `fetch`.
10. CSS layout and responsive design.
11. File uploads and security.
12. Database migrations and deployment.

The project is a practical example of the **MVC-style architecture**:

```text
Models      → database classes
Views       → Jinja HTML templates
Controllers → Flask blueprint route functions
```

In this project, the route functions act as the controller layer, the SQLAlchemy classes are the model layer, and the templates are the view layer.
