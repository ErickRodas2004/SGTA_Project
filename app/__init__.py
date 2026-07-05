"""Flask application factory — create_app() entry point."""

from flask import Flask, flash, redirect, render_template, url_for
from config import Config
from app.extensions import db, bcrypt, login_manager, talisman


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # --
    # Initialize extensions
    # --
    db.init_app(flask_app)
    bcrypt.init_app(flask_app)
    login_manager.init_app(flask_app)
    talisman.init_app(
        flask_app,
        force_https=False,
        content_security_policy=config_class.TALISMAN_CONTENT_SECURITY_POLICY,
    )

    # --
    # Login Manager — user loader callback
    # --
    from app.models import User  # noqa: late import to avoid circular refs

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --
    # Register blueprints
    # --
    from app.auth import auth_bp
    flask_app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes import main_bp
    flask_app.register_blueprint(main_bp)

    from app.users import users_bp
    flask_app.register_blueprint(users_bp, url_prefix='/admin')

    from app.audit import audit_bp
    flask_app.register_blueprint(audit_bp, url_prefix='/admin')

    from app.appointments import appointments_bp
    flask_app.register_blueprint(appointments_bp, url_prefix='/tutorias')

    from app.availability import availability_bp
    flask_app.register_blueprint(availability_bp, url_prefix='/disponibilidad')

    # --
    # Error handlers
    # --
    register_error_handlers(flask_app)

    # --
    # Context processors
    # --
    register_context_processors(flask_app)

    # --
    # Create database tables (dev convenience — use migrations in prod)
    # --
    with flask_app.app_context():
        from app import models  # noqa: F401 — ensure models are registered
        db.create_all()

    # --
    # Register CLI commands
    # --
    from app import cli
    cli.init_app(flask_app)

    return flask_app


def register_error_handlers(app):
    """Register HTTP error handlers — renders templates from templates/errors/."""

    @app.errorhandler(403)
    def forbidden(e):
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500


def register_context_processors(app):
    """Inject current_user into all Jinja templates."""

    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return {'current_user': current_user}
