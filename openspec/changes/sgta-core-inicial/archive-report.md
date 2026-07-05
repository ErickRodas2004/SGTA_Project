# SGTA Core Inicial — Archive Report

**Change:** `sgta-core-inicial`
**Status:** ✅ COMPLETED
**Date:** 2026-07-03

---

## Deliverables

### Batch 1: Core (T01-T04, T13)
- Project scaffold with Flask app factory pattern
- SQLAlchemy models: User, Appointment, Availability, AuditLog
- RBAC decorator (`@roles_required`)
- Audit logger (`log_audit()` helper)
- Flask-Talisman security hardening

### Batch 2: Auth + Base UI (T05-T07, T14)
- Auth blueprint: register, login, logout with Bcrypt
- Role-based dashboard routing (estudiante/docente/administrador)
- Base template with Bootstrap 5.3 CDN, role-based navbar, flash messages
- Error handlers: 403, 404, 500 with styled templates

### Batch 3: Admin + CRUD (T08, T12)
- User management blueprint: list, create, edit, deactivate
- Admin user forms with uniqueness validation
- Audit log viewer with pagination and action filter

### Batch 4: Tutorías + Disponibilidad (T09-T11)
- Student appointment flow: request (future-date validation), list (filterable), cancel (own-only guard)
- Docente appointment flow: view assigned (grouped by status), accept (pending→accepted), feedback (accepted→completed)
- Docente availability CRUD: create (start<end validation), list, delete (ownership guard)

## Audit Trail
9 audited actions: LOGIN, REGISTER_USER, CREATE_USER, UPDATE_USER, DEACTIVATE_USER, REQUEST_TUTORIA, CANCEL_TUTORIA, ACCEPT_TUTORIA, COMPLETE_TUTORIA

## Files Created
~30 files across app/ and templates/ directory

## Known Limitations
- SQLite (dev) — migrate to PostgreSQL for production
- Flask-Talisman `force_https=False` — set to True in production
- No test suite installed (pytest available but not configured)
- No email notifications for appointment status changes
- No overlapping appointment detection (spec mentions as optional warning)

## Next Steps Recommendation
- Install pytest and add test coverage
- Configure production deployment (PostgreSQL, HTTPS, proper secret key)
- Add email/SMS notifications for appointment state changes
- Consider pagination for /tutorias/mis-tutorias if data grows
