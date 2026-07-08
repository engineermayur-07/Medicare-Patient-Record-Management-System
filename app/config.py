import os
from dotenv import load_dotenv

load_dotenv()

# Base directory of the project (one level above app/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-fallback-secret-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/medicare_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_APP_PASSWORD = os.getenv('MAIL_APP_PASSWORD')

    # OTP expiry in minutes
    OTP_EXPIRY_MINUTES = 10

    # File uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'medical_records')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024          # 10 MB hard limit
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

    # Admin seed credentials
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@medicare.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin@1234')
