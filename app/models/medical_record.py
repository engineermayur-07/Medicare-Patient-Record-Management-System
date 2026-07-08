from datetime import datetime
from app.extensions import db


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)

    # Record meta
    record_type = db.Column(db.String(30), nullable=False)
    # record_type: prescription | lab_test | imaging | diagnosis | other

    title = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text)          # clinical notes / instructions / dosage

    # File attachment (optional)
    file_path = db.Column(db.String(500))   # absolute path on disk
    file_name = db.Column(db.String(255))   # original filename shown to user
    file_size = db.Column(db.Integer)       # bytes
    file_mime = db.Column(db.String(100))   # MIME type

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── ORM relationships ──────────────────────────────────────────
    patient = db.relationship(
        'User', foreign_keys=[user_id],
        backref=db.backref('medical_records', lazy='dynamic', cascade='all, delete-orphan'),
    )
    uploader = db.relationship(
        'Doctor', foreign_keys=[doctor_id],
        backref=db.backref('uploaded_records', lazy='dynamic'),
    )
    linked_appointment = db.relationship(
        'Appointment', foreign_keys=[appointment_id],
        backref=db.backref('records', lazy='dynamic'),
    )

    # ── Helpers ───────────────────────────────────────────────────
    RECORD_TYPE_LABELS = {
        'prescription': ('Prescription',    '💊', 'badge-blue'),
        'lab_test':     ('Lab Test',        '🧪', 'badge-teal'),
        'imaging':      ('Imaging',         '🩻', 'badge-purple'),
        'diagnosis':    ('Diagnosis',       '📋', 'badge-orange'),
        'other':        ('Other',           '📄', 'badge-muted'),
    }

    @property
    def type_label(self):
        return self.RECORD_TYPE_LABELS.get(self.record_type, ('Record', '📄', 'badge-muted'))[0]

    @property
    def type_icon(self):
        return self.RECORD_TYPE_LABELS.get(self.record_type, ('Record', '📄', 'badge-muted'))[1]

    @property
    def type_badge(self):
        return self.RECORD_TYPE_LABELS.get(self.record_type, ('Record', '📄', 'badge-muted'))[2]

    @property
    def has_file(self):
        return bool(self.file_path)

    @property
    def file_size_human(self):
        if not self.file_size:
            return ''
        if self.file_size < 1024:
            return f'{self.file_size} B'
        if self.file_size < 1024 ** 2:
            return f'{self.file_size / 1024:.1f} KB'
        return f'{self.file_size / (1024 ** 2):.1f} MB'

    def __repr__(self):
        return f'<MedicalRecord {self.record_type} user={self.user_id}>'
