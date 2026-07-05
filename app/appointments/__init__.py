"""Appointments Blueprint — tutoring session request, acceptance, feedback."""

from flask import Blueprint

appointments_bp = Blueprint('appointments', __name__)

from app.appointments import routes  # noqa: F401, E402 — register routes
