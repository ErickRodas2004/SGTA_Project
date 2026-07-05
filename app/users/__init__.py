"""Users Blueprint — admin user management CRUD."""

from flask import Blueprint

users_bp = Blueprint('users', __name__)

from app.users import routes  # noqa: F401, E402 — register routes
