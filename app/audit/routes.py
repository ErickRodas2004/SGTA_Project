"""Audit routes — admin audit log viewer with filtering."""

from flask import render_template, request
from flask_login import login_required

from app.models import AuditLog
from app.decorators import roles_required
from app.audit import audit_bp


@audit_bp.route('/auditoria')
@login_required
@roles_required('administrador')
def view_audit_log():
    """Paginated audit log, ordered by created_at DESC, optionally filtered by action."""
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action', '', type=str).strip()

    query = AuditLog.query.order_by(AuditLog.created_at.desc())

    if action_filter:
        query = query.filter(AuditLog.action == action_filter)

    pagination = query.paginate(page=page, per_page=20, error_out=False)
    entries = pagination.items

    # Collect distinct action types for the filter dropdown
    distinct_actions = [
        row[0] for row in
        AuditLog.query.with_entities(AuditLog.action).distinct().order_by(AuditLog.action).all()
    ]

    return render_template(
        'audit/log.html',
        entries=entries,
        pagination=pagination,
        action_filter=action_filter,
        distinct_actions=distinct_actions,
    )
