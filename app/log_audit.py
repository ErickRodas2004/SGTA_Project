"""Audit logging helpers — log sensitive operations to the AuditLog table."""

import json
from functools import wraps

from flask import request, has_request_context
from flask_login import current_user

from app.extensions import db
from app.models import AuditLog


def log_audit(action, table_affected, record_id=None, details=None):
    """Persist an audit log entry.

    Parameters
    ----------
    action : str
        Canonical action name, e.g. ``'CREATE_USER'``, ``'CANCEL_TUTORIA'``.
    table_affected : str
        Database table name, e.g. ``'users'``, ``'appointments'``.
    record_id : int or None
        Primary key of the affected row (if applicable).
    details : dict or None
        Optional extra context; serialised to JSON.
    """
    # current_user may be None outside request context (CLI commands)
    user = current_user if hasattr(current_user, 'is_authenticated') else None
    is_auth = user is not None and user.is_authenticated

    entry = AuditLog(
        user_id=user.id if is_auth else None,
        username=user.username if is_auth else 'anonymous',
        action=action,
        table_affected=table_affected,
        record_id=record_id,
        details=json.dumps(details, ensure_ascii=False) if details else None,
        ip_address=request.remote_addr if has_request_context() else '0.0.0.0',
    )
    db.session.add(entry)
    db.session.commit()


def audit_log(action, table_affected):
    """Decorator — automatically log an audit entry after the wrapped
    function executes.

    The decorated function **must** return an object with a ``.id``
    attribute (or ``None``) that will be stored as ``record_id``.

    Usage::

        @audit_log('CREATE_USER', 'users')
        def create_user_handler():
            user = User(...)
            db.session.add(user)
            db.session.commit()
            return user  # user.id becomes record_id
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            record_id = result.id if hasattr(result, 'id') else None
            log_audit(action, table_affected, record_id=record_id)
            return result

        return decorated_function

    return decorator
