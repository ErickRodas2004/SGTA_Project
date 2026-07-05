# SGTA Core Inicial — Especificación Técnica

**Change:** `sgta-core-inicial`
**Date:** 2026-07-03
**Status:** Draft Spec

---

## Models

### User
| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer PK | Auto-increment |
| username | String(80) | Unique, not null |
| email | String(120) | Unique, not null |
| password_hash | String(256) | Not null (Bcrypt) |
| role | String(20) | Not null: `estudiante`, `docente`, `administrador` |
| is_active | Boolean | Default true |
| created_at | DateTime | Auto |
| updated_at | DateTime | Auto |

### Appointment (Tutoría)
| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer PK | Auto-increment |
| student_id | Integer FK | References User.id, not null |
| teacher_id | Integer FK | References User.id, not null |
| subject | String(200) | Not null |
| description | Text | Optional |
| status | String(20) | `pending`, `accepted`, `completed`, `cancelled` |
| scheduled_date | Date | Not null |
| scheduled_time | Time | Not null |
| feedback | Text | Nullable, docente fills after session |
| created_at | DateTime | Auto |
| updated_at | DateTime | Auto |

### Availability (Disponibilidad)
| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer PK | Auto-increment |
| teacher_id | Integer FK | References User.id, not null |
| day_of_week | Integer | 0-6 (Monday=0) |
| start_time | Time | Not null |
| end_time | Time | Not null |
| is_available | Boolean | Default true |
| created_at | DateTime | Auto |

### AuditLog
| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer PK | Auto-increment |
| user_id | Integer | Nullable (for unauthenticated actions) |
| username | String(80) | For display, even if user deleted |
| action | String(100) | e.g. `CREATE_USER`, `CANCEL_APPOINTMENT` |
| table_affected | String(50) | e.g. `users`, `appointments` |
| record_id | Integer | Nullable, ID of affected record |
| details | Text | Nullable, JSON with extra context |
| ip_address | String(45) | IPv4 or IPv6 |
| created_at | DateTime | Auto |

---

## Requirement: REQ-AUTH — Authentication

### REQ-AUTH-01: User Registration
**Description:** Any new user can register with username, email, and password. Role is assigned at registration (estudiante by default; admin can promote later).

**Acceptance:**
- GIVEN a visitor on the register page WHEN they submit valid data THEN a User is created with role `estudiante`, password is Bcrypt-hashed, and they are redirected to login
- GIVEN a visitor submits a duplicate email WHEN the form validates THEN an error "Email already registered" is shown
- GIVEN a visitor submits a weak password (< 8 chars) WHEN the form validates THEN an error is shown

### REQ-AUTH-02: Login / Logout
**Description:** Registered users can log in with username/email + password. Sessions use Flask-Login.

**Acceptance:**
- GIVEN a registered user WHEN they submit correct credentials THEN they are logged in and redirected to their role-specific dashboard
- GIVEN a registered user WHEN they submit incorrect password THEN "Invalid credentials" error is shown
- GIVEN an authenticated user WHEN they click logout THEN their session is destroyed and they are redirected to login
- GIVEN an inactive user (`is_active=false`) WHEN they attempt to login THEN access is denied with "Account deactivated"

### REQ-AUTH-03: Password Security
**Description:** Passwords are never stored in plain text.

**Acceptance:**
- GIVEN any user record WHEN inspected in the database THEN `password_hash` contains a Bcrypt hash, never the plain password
- GIVEN a login attempt WHEN the password is checked THEN `check_password_hash` is used for constant-time comparison

---

## Requirement: REQ-RBAC — Role-Based Access Control

### REQ-RBAC-01: Role Decorator
**Description:** A `@roles_required('role1', 'role2')` decorator guards every protected route.

**Acceptance:**
- GIVEN an unauthenticated request to any protected route WHEN no session exists THEN redirect to login with 302
- GIVEN a student accessing a docente-only route WHEN they are authenticated as estudiante THEN return 403 Forbidden
- GIVEN a docente accessing their own route WHEN they have the docente role THEN the route handler executes normally

### REQ-RBAC-02: Route Matrix
| Route | Method | Role | Description |
|-------|--------|------|-------------|
| `/dashboard` | GET | any auth | Redirects to role-specific dashboard |
| `/admin/usuarios` | GET | admin | User list |
| `/admin/usuarios/crear` | GET/POST | admin | Create user |
| `/admin/usuarios/<id>/editar` | GET/POST | admin | Edit user |
| `/admin/usuarios/<id>/baja` | POST | admin | Deactivate user |
| `/admin/auditoria` | GET | admin | View audit log |
| `/tutorias/solicitar` | GET/POST | estudiante | Request tutoring |
| `/tutorias/mis-tutorias` | GET | estudiante | View own appointments |
| `/tutorias/<id>/cancelar` | POST | estudiante | Cancel own appointment |
| `/disponibilidad/` | GET/POST | docente | CRUD availability slots |
| `/docente/agendados` | GET | docente | View assigned students |
| `/tutorias/<id>/feedback` | GET/POST | docente | Record session feedback |

---

## Requirement: REQ-USERS — User Management (Admin)

### REQ-USERS-01: Create User
**Description:** Admin can create accounts for estudiantes and docentes with any role.

**Acceptance:**
- GIVEN an admin on the create user form WHEN they submit valid data for a docente THEN the user is created with role `docente`
- GIVEN an admin WHEN they submit the form with missing fields THEN validation errors are shown
- GIVEN an admin WHEN they leave the password field blank THEN an auto-generated temporary password is created (or form requires it)

### REQ-USERS-02: Edit User
**Description:** Admin can update user profile details and role.

**Acceptance:**
- GIVEN an admin editing a user WHEN they change the role from `estudiante` to `docente` THEN the role updates
- GIVEN an admin WHEN they try to demote another admin THEN the system prevents removing the last admin

### REQ-USERS-03: Deactivate User (Baja)
**Description:** Admin can deactivate (soft-delete) a user account. The user cannot log in but their data is preserved.

**Acceptance:**
- GIVEN an admin deactivates a user WHEN they confirm THEN `is_active` is set to false, the action is logged in AuditLog
- GIVEN a deactivated user WHEN they try to log in THEN "Account deactivated" error is shown

---

## Requirement: REQ-APPOINTMENTS — Tutoring Sessions

### REQ-APP-01: Request Tutoring (Estudiante)
**Description:** A student can request a tutoring session by selecting a docente, subject, date, and time.

**Acceptance:**
- GIVEN an authenticated estudiante on the request form WHEN they select a docente and submit valid data THEN a new Appointment is created with status `pending`
- GIVEN a student WHEN they submit a request for a past date THEN the form rejects with "Scheduled date must be in the future"
- GIVEN a student WHEN the selected time slot conflicts with an existing pending/accepted appointment for that teacher THEN the system warns about potential overlap

### REQ-APP-02: View My Appointments (Estudiante)
**Description:** A student can view all their tutoring requests and their status.

**Acceptance:**
- GIVEN an authenticated estudiante on "Mis Tutorías" page WHEN they view it THEN they see all their appointments with status, docente name, date, time
- GIVEN a student with no appointments WHEN they view the page THEN they see "No tienes tutorías registradas"

### REQ-APP-03: Cancel Appointment (Estudiante)
**Description:** A student can cancel their own appointment if it's pending or accepted.

**Acceptance:**
- GIVEN a student viewing their appointment in `pending` status WHEN they click cancel THEN status changes to `cancelled`, audit log entry created
- GIVEN a student WHEN they try to cancel a `completed` appointment THEN the action is rejected with "Cannot cancel a completed tutoring session"
- GIVEN a student WHEN they try to cancel another student's appointment THEN 403 Forbidden

### REQ-APP-04: View Assigned Students (Docente)
**Description:** A docente can see students who have requested tutoring with them.

**Acceptance:**
- GIVEN an authenticated docente on their "Estudiantes Agendados" page WHEN they view it THEN they see all appointments assigned to them
- GIVEN a docente WHEN an appointment is in `pending` status THEN they see an option to accept it

### REQ-APP-05: Accept Appointment (Docente)
**Description:** A docente can accept a pending tutoring request.

**Acceptance:**
- GIVEN a docente viewing a pending appointment WHEN they click accept THEN status changes to `accepted`
- GIVEN a docente WHEN they accept THEN the student can see the updated status

### REQ-APP-06: Record Feedback (Docente)
**Description:** After a tutoring session, the docente can record feedback.

**Acceptance:**
- GIVEN a docente on the feedback form for a `completed` appointment WHEN they submit feedback THEN the `feedback` field is updated
- GIVEN a docente WHEN they try to add feedback to a `pending` appointment THEN the form rejects with "Cannot add feedback until tutoring is completed"

---

## Requirement: REQ-AVAILABILITY — Docente Schedule

### REQ-AVAIL-01: Create Availability Slot
**Description:** Docente can add available time slots for tutoring.

**Acceptance:**
- GIVEN an authenticated docente on their availability page WHEN they add a time slot (day, start, end) THEN it is saved
- GIVEN a docente WHEN they add a slot with start_time >= end_time THEN validation error is shown

### REQ-AVAIL-02: List Availability
**Description:** Docente can see their current availability calendar.

**Acceptance:**
- GIVEN a docente viewing their availability WHEN they have slots THEN all slots are shown grouped by day
- GIVEN a docente with no slots WHEN they view the page THEN they see "No has registrado disponibilidad"

### REQ-AVAIL-03: Delete Availability Slot
**Description:** Docente can remove an availability slot.

**Acceptance:**
- GIVEN a docente viewing their availability WHEN they delete a slot THEN it is removed

---

## Requirement: REQ-AUDIT — Audit Logging

### REQ-AUDIT-01: Automatic Audit Logging
**Description:** All sensitive operations automatically create an AuditLog entry.

**Triggered actions:**
| Action | Table | Trigger |
|--------|-------|---------|
| `CREATE_USER` | users | Admin creates a user |
| `UPDATE_USER` | users | Admin edits a user |
| `DEACTIVATE_USER` | users | Admin deactivates a user |
| `REQUEST_TUTORIA` | appointments | Student creates appointment |
| `CANCEL_TUTORIA` | appointments | Student cancels |
| `ACCEPT_TUTORIA` | appointments | Docente accepts |
| `COMPLETE_TUTORIA` | appointments | Docente marks complete |
| `FEEDBACK_TUTORIA` | appointments | Docente adds feedback |

**Acceptance:**
- GIVEN any triggered action WHEN it executes THEN an AuditLog row is created with user_id, action, table_affected, record_id, ip_address, and timestamp
- GIVEN a user performs an action without being logged in (if possible) WHEN it triggers audit THEN user_id is null but username captures context

### REQ-AUDIT-02: View Audit Log (Admin)
**Description:** Admin can view all audit log entries with filtering.

**Acceptance:**
- GIVEN an admin on the audit page WHEN they view it THEN they see all entries ordered by timestamp DESC with username, action, table, IP, date
- GIVEN an admin WHEN they filter by action type THEN only matching entries are shown

---

## Requirement: REQ-SECURITY — Security Headers & Protection

### REQ-SEC-01: Flask-Talisman
**Description:** All responses include security headers via Flask-Talisman.

**Acceptance:**
- GIVEN any HTTP response WHEN inspected THEN it includes `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, and `Content-Security-Policy` headers
- GIVEN a form submission without CSRF token WHEN POSTed THEN the request is rejected with 400

### REQ-SEC-02: Input Sanitization
**Description:** All user input is validated and sanitized.

**Acceptance:**
- GIVEN any form field WHEN submitted with HTML/JS content THEN WTForms validates and rejects/escapes dangerous content
- GIVEN a SQL injection attempt via any string field WHEN processed THEN SQLAlchemy parameterized queries prevent injection

---

## Requirement: REQ-FRONTEND — User Interface

### REQ-FRONT-01: Responsive Layout
**Description:** The UI uses Bootstrap (or Tailwind) with a responsive layout.

**Acceptance:**
- GIVEN a user on any page WHEN viewed on a mobile screen (<768px) THEN the layout adapts
- GIVEN any form WHEN displayed THEN it is styled with the chosen CSS framework

### REQ-FRONT-02: System Messages (Flash Alerts)
**Description:** Success, error, and info messages are shown as dismissible alerts.

**Acceptance:**
- GIVEN a successful operation (create, update, delete) WHEN completed THEN a green success flash is shown
- GIVEN a failed operation or validation error WHEN rejected THEN a red/amber error flash is shown
- GIVEN a 403 Forbidden WHEN triggered THEN a "Access denied" flash is shown

### REQ-FRONT-03: Navigation by Role
**Description:** Each role sees a navigation menu relevant to their permissions.

**Acceptance:**
- GIVEN an estudiante WHEN logged in THEN nav shows: Solicitar Tutoría, Mis Tutorías
- GIVEN a docente WHEN logged in THEN nav shows: Mi Disponibilidad, Estudiantes Agendados
- GIVEN an admin WHEN logged in THEN nav shows: Usuarios, Auditoría

---

## Data Flow Diagrams

### Tutoring Request Flow
```
Estudiante → POST /tutorias/solicitar → Validate (WTForms)
    → Create Appointment (status=pending) → AuditLog CREATE
    → Flash success → Redirect to Mis Tutorías
```

### Tutoring Acceptance Flow
```
Docente → GET /docente/agendados → View pendings
    → POST /tutorias/<id>/aceptar → Update status=accepted
    → AuditLog ACCEPT → Flash success → Redirect back
```

### Feedback Flow
```
Docente → GET /tutorias/<id>/feedback → Load form
    → POST /tutorias/<id>/feedback → Validate → Update feedback field
    → Update status=completed → AuditLog FEEDBACK → Flash success
```

---

**Next phase**: Design — architecture diagrams, component structure, route design, database schema.
