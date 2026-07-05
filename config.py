import os


class Config:
    """Flask application configuration."""

    # Flask core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-change-in-prod'

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sgta.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Bcrypt
    BCRYPT_LOG_ROUNDS = 12

    # Flask-Talisman — security headers
    TALISMAN_FORCE_HTTPS = False  # True in production
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'style-src': ["'self'", 'https://cdn.jsdelivr.net'],
        'script-src': ["'self'", 'https://cdn.jsdelivr.net'],
        'font-src': ["'self'", 'https://cdn.jsdelivr.net'],
        'img-src': ["'self'", 'data:'],
    }
    TALISMAN_X_FRAME_OPTIONS = 'DENY'
    TALISMAN_X_CONTENT_TYPE_OPTIONS = 'nosniff'
    TALISMAN_SESSION_COOKIE_SECURE = False  # True in production (requires HTTPS)
    TALISMAN_SESSION_COOKIE_HTTPONLY = True
    TALISMAN_SESSION_COOKIE_SAMESITE = 'Lax'

    # WTForms CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
