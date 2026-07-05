"""Main Blueprint — root routes and role-based dashboard routing."""

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page — redirect to dashboard if authenticated, else to login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
def dashboard():
    """Render a role-specific dashboard."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    role_templates = {
        'estudiante': 'dashboard/estudiante.html',
        'docente': 'dashboard/docente.html',
        'administrador': 'dashboard/admin.html',
    }
    template = role_templates.get(current_user.role, 'dashboard/estudiante.html')
    return render_template(template)
