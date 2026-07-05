"""Audit Blueprint — admin audit log viewer."""

from flask import Blueprint

audit_bp = Blueprint('audit', __name__)

from app.audit import routes  # noqa: F401, E402 — register routes
