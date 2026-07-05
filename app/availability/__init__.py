"""Availability Blueprint — docente schedule management."""

from flask import Blueprint

availability_bp = Blueprint('availability', __name__)

from app.availability import routes  # noqa: F401, E402 — register routes
