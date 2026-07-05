# SGTA Core Inicial — Propuesta

**Change:** `sgta-core-inicial`
**Date:** 2026-07-03
**Status:** Draft Proposal

---

## 1. Intent

Build the initial core of SGTA (Sistema de Gestión de Tutorías Académicas), a secure web platform for managing academic tutoring sessions between students and teachers, with strict role-based access control and full audit logging.

## 2. Business Problem

Academic institutions lack a centralized, secure system to:
- Allow students to request tutoring appointments
- Allow teachers to manage their availability and provide session feedback
- Give administrators oversight of users, roles, and all system activity

Manual coordination via email or paper leads to lost requests, scheduling conflicts, and no audit trail.

## 3. Target Users

| Role | Description | Key Actions |
|------|-------------|-------------|
| **Estudiante** | Student seeking academic tutoring | View available slots, request tutoring, view own appointments, cancel own appointments |
| **Docente** | Teacher/professor offering tutoring | CRUD availability, view assigned students, record session feedback |
| **Administrador** | System admin | Full user management (CRUD), role assignment, view audit log |

## 4. Business Rules

1. **Authentication required**: All users must authenticate via email/username + password (Bcrypt-hashed).
2. **RBAC enforcement**: Every endpoint enforces role-based access via decorators. No role can perform actions outside its permission set.
3. **Self-service cancellation**: Only the student who created a tutoring request can cancel it, and only if it's still in "pending" or "accepted" state.
4. **Audit trail**: Every CRUD operation on sensitive tables (usuarios, citas) is logged to `AuditLog` with user_id, action, affected table, timestamp, and IP.
5. **Data ownership**: Students see only their own tutoring records. Teachers see only their assigned students. Admins see all.
6. **Session security**: All communications enforce HTTPS, CSP headers, XSS protection, and clickjacking prevention via Flask-Talisman.

## 5. Scope

### In Scope (MVP)

- User authentication (register, login, logout) with Flask-Login + Flask-Bcrypt
- RBAC system with three roles: estudiante, docente, administrador
- CRUD for users (Admin only — create, read, update, deactivate accounts)
- Tutoring request system (Estudiante creates, Docente accepts/provides feedback)
- Availability management (Docente CRUD)
- Audit logging for all sensitive operations
- Flask-Talisman security headers
- Frontend with Bootstrap/Tailwind — responsive UI for all three roles
- Form validation (WTForms) — frontend + backend

### Out of Scope (Future)

- Email/SMS notifications
- Real-time chat
- File uploads (attachments to tutoring sessions)
- Payment or billing integration
- SSO / OAuth providers
- Mobile app

## 6. Technical Approach

### Stack
| Component | Technology |
|-----------|-----------|
| Backend | Python 3.14 + Flask |
| Database | SQLite via Flask-SQLAlchemy |
| Auth | Flask-Login + Flask-Bcrypt |
| Security Headers | Flask-Talisman |
| Forms/Validation | WTForms |
| Frontend | Bootstrap 5 (or Tailwind CSS) |
| Frontend rendering | Flask Jinja2 templates |

### Architecture Pattern
- **Blueprint-based MVC** with separate modules per domain:
  - `auth/` — authentication routes and forms
  - `users/` — admin user management
  - `appointments/` — tutoring CRUD
  - `availability/` — docente schedule management
  - `audit/` — audit log views
- Shared `decorators.py` for RBAC enforcement
- Shared `audit.py` helper for audit logging
- All database models in `models.py`

### Security Architecture
1. **Password hashing**: Flask-Bcrypt `generate_password_hash` / `check_password_hash`
2. **Session management**: Flask-Login with `@login_required` + custom `@roles_required` decorator
3. **Security headers**: Flask-Talisman forcing HTTPS, strict CSP, X-Frame-Options DENY, X-Content-Type-Options nosniff
4. **CSRF**: WTForms CSRF protection on all forms
5. **Input validation**: WTForms validators on all inputs + server-side sanitization
6. **Audit logging**: Custom `log_audit(user_id, action, table, ip)` helper writing to `AuditLog` table

## 7. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| SQLite concurrency limits | Low (single-user dev) | Accept for MVP; migrate to PostgreSQL later |
| No test coverage yet | Medium | Install pytest + flask-testing before apply phase |
| XSS via Jinja2 templates | High | Use autoescaping + WTForms sanitization; never use `|safe` without review |
| CSRF on API endpoints | High | WTForms CSRF on all form submissions |
| Session hijacking | Medium | Flask-Talisman HTTPS enforcement + secure session cookies |
| Sub-agent routing unavailable | Low | Orchestrator handles phases inline |

## 8. Non-Goals

- Full test suite in this change (tests will be added after core is functional)
- Docker containerization (future concern)
- Deployment pipeline (CI/CD)

---

**Next phase**: Spec — detail each requirement with acceptance scenarios.
