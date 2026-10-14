import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# Base directory of the project (one level above app/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-fallback-secret-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/medicare_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Resend email API
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    RESEND_FROM_EMAIL = os.getenv(
        'RESEND_FROM_EMAIL',
        'MediCare Hospital <onboarding@resend.dev>',
    )

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

    # Razorpay test mode
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
    APPOINTMENT_FEE = Decimal(os.getenv('APPOINTMENT_FEE', '500.00'))

    # Gemini health-summary assistant
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
