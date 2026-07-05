"""RBAC decorators — role-based access control for Flask routes."""

from functools import wraps

from flask import abort, redirect, url_for, flash
from flask_login import current_user


def roles_required(*roles):
    """Decorator — restrict route access to one or more roles.

    Usage::

        @app.route('/admin/usuarios')
        @roles_required('administrador')
        def list_users():
            ...

    Chains with ``@login_required`` internally. Unauthenticated requests
    are redirected to the login page. Authenticated-but-unauthorized
    requests receive a 403 Forbidden.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(
                    'Por favor inicia sesión para acceder a esta página.',
                    'warning',
                )
                return redirect(url_for('auth.login'))

            if not current_user.is_active:
                flash('Tu cuenta está desactivada.', 'danger')
                return redirect(url_for('auth.login'))

            if current_user.role not in roles:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
