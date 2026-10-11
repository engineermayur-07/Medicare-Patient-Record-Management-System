from flask import Flask
from .config import Config
from .extensions import db, migrate, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Import models so Alembic can detect them
    from .models import user, doctor, admin, otp, appointment, service, medical_record  # noqa: F401

    # Register blueprints
    from .blueprints.main import main as main_bp
    from .blueprints.auth import auth as auth_bp
    from .blueprints.user import user as user_bp
    from .blueprints.appointments import appointments as appt_bp
    from .blueprints.doctor import doctor as doctor_bp
    from .blueprints.admin import admin as admin_bp
    from .blueprints.records import records as records_bp
    from .blueprints.chatbot import chatbot as chatbot_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(appt_bp, url_prefix='/appointments')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(records_bp, url_prefix='/records')
    app.register_blueprint(chatbot_bp, url_prefix='/user')

    # Ensure upload folder exists
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inject `now` into every template (used by footer for year)
    from datetime import datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    return app
