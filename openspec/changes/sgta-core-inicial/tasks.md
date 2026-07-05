# SGTA Core Inicial — Desglose de Tareas

**Change:** `sgta-core-inicial`
**Date:** 2026-07-03
**Status:** ✅ Completed — 14/14 tasks implemented and verified

---

## Dependencias entre tareas

```
T01 → T02 → T03 → T04 → T05 → T06 → T07 → T08 → T09 → T10
                  │              │              │
                  ├→ T04a         ├→ T06a        ├→ T08a
                                  └→ T06b
```

**Leyenda:** `→` = depende de / bloquea a

---

## ✅ Task T01: Project Scaffold & Dependencies

**Archivos:** `requirements.txt`, `config.py`, `app/__init__.py`, `app/extensions.py`, `run.py`
**Dependencias:** Ninguna
**Estimación:** ~80 líneas

### Qué hacer
1. Crear `requirements.txt` con: Flask, Flask-SQLAlchemy, Flask-Bcrypt, Flask-Login, Flask-Talisman, WTForms
2. Crear `config.py` con clase Config (SECRET_KEY, SQLALCHEMY_DATABASE_URI, Bcrypt rounds, Talisman CSP)
3. Crear `app/extensions.py` — inicializar db, bcrypt, login_manager, talisman
4. Crear `app/__init__.py` — app factory: create_app() que init extensions, register blueprints, error handlers
5. Crear `run.py` — entry point
6. Instalar dependencias

### Criterio de aceptación
- `python run.py` inicia el servidor sin errores
- Flask carga la configuración correctamente

---

## ✅ Task T02: Database Models

**Archivos:** `app/models.py`
**Dependencias:** T01
**Estimación:** ~120 líneas

### Qué hacer
1. Modelo `User`: id, username, email, password_hash, role, is_active, timestamps
   - `set_password(password)` → bcrypt hash
   - `check_password(password)` → verify hash
   - `has_role(role)` → role comparison
   - `is_authenticated`, `is_active` property para Flask-Login
2. Modelo `Appointment`: id, student_id FK, teacher_id FK, subject, description, status, scheduled_date, scheduled_time, feedback, timestamps
3. Modelo `Availability`: id, teacher_id FK, day_of_week, start_time, end_time, is_available, created_at
4. Modelo `AuditLog`: id, user_id (nullable FK), username, action, table_affected, record_id, details, ip_address, created_at

### Criterio de aceptación
- `db.create_all()` crea las 4 tablas correctamente
- Relaciones FK funcionan
- User.set_password produce hash Bcrypt válido

---

## ✅ Task T03: RBAC Decorators & Login Manager Config

**Archivos:** `app/decorators.py`, `app/extensions.py` (update)
**Dependencias:** T01, T02
**Estimación:** ~40 líneas

### Qué hacer
1. Crear `app/decorators.py`:
   - `@roles_required(*roles)`: verifica que `current_user.role` esté en los roles permitidos
   - Si no autenticado → redirect a login
   - Si rol incorrecto → abort(403)
2. Configurar Flask-Login en `extensions.py`:
   - `login_manager.user_loader` callback
   - `login_view = 'auth.login'`
   - `login_message_category = 'warning'`

### Criterio de aceptación
- Decorador protege rutas correctamente
- 403 renderiza template de acceso denegado
- 302 a login si no autenticado

---

## ✅ Task T04: Audit Logger

**Archivos:** `app/audit.py`
**Dependencias:** T02
**Estimación:** ~30 líneas

### Qué hacer
1. Función `log_audit(action, table_affected, record_id=None, details=None)`
   - Crea AuditLog con user_id, username (o 'anonymous'), action, table_affected, record_id, details (JSON), ip_address (request.remote_addr)
   - db.session.add + commit
2. Decorador opcional `@audit_log(action, table)` para logging automático

### Criterio de aceptación
- Llamar `log_audit(...)` persiste un registro en AuditLog
- IP se captura correctamente
- user_id es null si no hay sesión activa

---

## ✅ Task T05: Auth Blueprint (Register, Login, Logout)

**Archivos:** `app/auth/__init__.py`, `app/auth/routes.py`, `app/auth/forms.py`, `app/templates/auth/*.html`
**Dependencias:** T01, T02, T03, T04
**Estimación:** ~250 líneas (150 backend + 100 templates)

### Qué hacer
1. `auth/forms.py`:
   - `RegisterForm`: username, email, password, confirm_password (WTForms validators: Length, Email, EqualTo, DataRequired)
   - `LoginForm`: username, password, remember_me
2. `auth/routes.py`:
   - `GET/POST /auth/register` → valida form, crea User con role='estudiante', redirect a login
   - `GET/POST /auth/login` → valida credenciales, login_user(), redirect a dashboard según role
   - `GET /auth/logout` → logout_user(), redirect a login
3. `auth/__init__.py`: Blueprint `auth_bp`
4. Templates:
   - `login.html`: form centrado con Bootstrap
   - `register.html`: form centrado con Bootstrap
5. Auditoría: login exitoso → log_audit('LOGIN', 'users', user.id)

### Criterio de aceptación
- Registro crea usuario con Bcrypt hash
- Login/Logout funcionan
- Roles determinan redirect post-login
- CSRF protegido

---

## ✅ Task T06: Dashboard & Role Routing

**Archivos:** `app/templates/dashboard/*.html`, `app/routes.py` (main)
**Dependencias:** T03, T05
**Estimación:** ~150 líneas (20 backend + 130 templates)

### Qué hacer
1. Ruta `GET /dashboard`:
   - `current_user.role == 'estudiante'` → render dashboard/estudiante.html
   - `current_user.role == 'docente'` → render dashboard/docente.html
   - `current_user.role == 'administrador'` → render dashboard/admin.html
2. Ruta `GET /` → redirect a /dashboard si autenticado, sino a /auth/login
3. Templates de dashboard: cards con acciones rápidas, stats, enlaces

### Criterio de aceptación
- Cada rol ve su dashboard específico
- Navbar se actualiza según rol

---

## ✅ Task T07: Base Template (Navbar + Layout)

**Archivos:** `app/templates/base.html`
**Dependencias:** T05
**Estimación:** ~120 líneas

### Qué hacer
1. Layout base con:
   - Bootstrap 5.3 CDN + Bootstrap Icons
   - Navbar con menú contextual por rol:
     - **Estudiante:** Solicitar Tutoría, Mis Tutorías
     - **Docente:** Mi Disponibilidad, Estudiantes Agendados
     - **Admin:** Usuarios, Auditoría
   - Flash messages con dismissible alerts (success, danger, warning)
   - `{% block content %}` para contenido de página
   - Footer simple
   - Jinja2 autoescaping activado

### Criterio de aceptación
- Navbar muestra opciones correctas según current_user.role
- Flash messages se renderizan y pueden cerrarse

---

## ✅ Task T08: Admin — User Management (CRUD)

**Archivos:** `app/users/__init__.py`, `app/users/routes.py`, `app/users/forms.py`, `app/templates/users/*.html`
**Dependencias:** T02, T03, T04, T07
**Estimación:** ~320 líneas (180 backend + 140 templates)

### Qué hacer
1. `users/forms.py`:
   - `UserForm`: username, email, password, role (select: estudiante, docente, administrador)
   - `EditUserForm`: same sin password
2. `users/routes.py`:
   - `GET /admin/usuarios` → tabla paginada de usuarios
   - `GET/POST /admin/usuarios/crear` → create + log_audit('CREATE_USER', 'users', new_user.id)
   - `GET/POST /admin/usuarios/<id>/editar` → edit + log_audit('UPDATE_USER', 'users', id)
   - `POST /admin/usuarios/<id>/baja` → is_active=False + log_audit('DEACTIVATE_USER', 'users', id)
3. `users/__init__.py`: Blueprint `users_bp`
4. Templates:
   - `list.html`: tabla con acciones (editar, dar de baja)
   - `create.html`: form
   - `edit.html`: form precargado

### Criterio de aceptación
- Solo admin accede (403 para otros roles)
- Crear usuario funciona con cualquier rol
- Dar de baja desactiva login
- Cada acción queda registrada en AuditLog

---

## ✅ Task T09: Appointment — Student (Request, List, Cancel)

**Archivos:** `app/appointments/__init__.py`, `app/appointments/routes.py`, `app/appointments/forms.py`, `app/templates/appointments/*.html`
**Dependencias:** T02, T03, T04, T07, T08 (para listar docentes)
**Estimación:** ~280 líneas (150 backend + 130 templates)

### Qué hacer
1. `appointments/forms.py`:
   - `AppointmentForm`: teacher (SelectField con docentes), subject, description, scheduled_date, scheduled_time
   - Validación custom: fecha futura, formato correcto
2. `appointments/routes.py`:
   - `GET/POST /tutorias/solicitar` → crea Appointment(status='pending') + log_audit('REQUEST_TUTORIA', 'appointments', id)
   - `GET /tutorias/mis-tutorias` → lista appointments del estudiante, filtrables por status
   - `POST /tutorias/<id>/cancelar` → status='cancelled' + log_audit('CANCEL_TUTORIA', 'appointments', id)
3. `appointments/__init__.py`: Blueprint `appointments_bp`
4. Templates:
   - `request.html`: form con selector de docente
   - `my_list.html`: tabla con status badges, botón cancelar

### Criterio de aceptación
- Estudiante puede solicitar y ver tutorías
- Cancelar solo si own appointment y status != 'completed'
- Fechas pasadas rechazadas

---

## ✅ Task T10: Appointment — Docente (Accept, View Students, Feedback)

**Archivos:** `app/appointments/routes.py` (append), `app/appointments/forms.py` (append), `app/templates/appointments/*.html` (append)
**Dependencias:** T09
**Estimación:** ~220 líneas (120 backend + 100 templates)

### Qué hacer
1. `appointments/forms.py`:
   - `FeedbackForm`: feedback textarea, opcionalmente rating
2. Rutas nuevas en `appointments/routes.py`:
   - `GET /docente/agendados` → lista appointments del docente, agrupados por status
   - `POST /tutorias/<id>/aceptar` → status='accepted' + log_audit('ACCEPT_TUTORIA', 'appointments', id)
   - `GET/POST /tutorias/<id>/feedback` → guarda feedback, status='completed' + log_audit('FEEDBACK_TUTORIA', 'appointments', id)
3. Templates:
   - `assigned_list.html`: tabla con botones de aceptar, feedback
   - `feedback.html`: form de feedback

### Criterio de aceptación
- Docente ve solo sus appointments asignados
- Aceptar cambia status y notifica (flash)
- Feedback solo permitido si status='accepted' (se marca 'completed')

---

## ✅ Task T11: Availability CRUD (Docente)

**Archivos:** `app/availability/__init__.py`, `app/availability/routes.py`, `app/availability/forms.py`, `app/templates/availability/*.html`
**Dependencias:** T02, T03, T07
**Estimación:** ~200 líneas (100 backend + 100 templates)

### Qué hacer
1. `availability/forms.py`:
   - `AvailabilityForm`: day_of_week (SelectField 0-6 con nombres), start_time, end_time
   - Validación custom: start < end
2. `availability/routes.py`:
   - `GET /disponibilidad/` → lista slots del docente
   - `POST /disponibilidad/crear` → crea slot
   - `POST /disponibilidad/<id>/eliminar` → elimina slot
3. `availability/__init__.py`: Blueprint `availability_bp`
4. Templates:
   - `manage.html`: tabla de slots + form inline

### Criterio de aceptación
- Solo docente accede
- CRUD completo: crear, listar, eliminar
- Validación de horarios

---

## ✅ Task T12: Audit Log View (Admin)

**Archivos:** `app/audit/routes.py`, `app/audit/__init__.py`, `app/templates/audit/log.html`
**Dependencias:** T02, T03, T07
**Estimación:** ~100 líneas (40 backend + 60 templates)

### Qué hacer
1. `audit/routes.py`:
   - `GET /admin/auditoria` → tabla paginada de AuditLog, ordenada por created_at DESC
   - Filtro opcional por acción (query param `?action=CREATE_USER`)
2. `audit/__init__.py`: Blueprint `audit_bp`
3. Template:
   - `log.html`: tabla con username, acción, tabla, record_id, IP, timestamp, detail expandible

### Criterio de aceptación
- Solo admin accede
- Paginación funciona
- Filtro por acción funciona

---

## ✅ Task T13: Flask-Talisman & Security Hardening

**Archivos:** `config.py` (update), `app/__init__.py` (update)
**Dependencias:** T01
**Estimación:** ~40 líneas

### Qué hacer
1. Configurar Flask-Talisman en `create_app()`:
   - `force_https=False` (True en prod)
   - `content_security_policy` permitiendo Bootstrap CDN
   - `x_frame_options='DENY'`
   - `x_content_type_options='nosniff'
   - `session_cookie_secure=True` (en prod)
   - `session_cookie_http_only=True`
2. Verificar que WTForms CSRF esté activo en todos los forms

### Criterio de aceptación
- Headers de seguridad presentes en respuesta HTTP
- CSRF token presente en todos los forms

---

## ✅ Task T14: Error Handlers & Polish

**Archivos:** `app/__init__.py` (update), `app/templates/errors/*.html`
**Dependencias:** T07
**Estimación:** ~60 líneas (10 backend + 50 templates)

### Qué hacer
1. Error handlers: 403, 404, 500
2. Templates: `403.html`, `404.html`, `500.html`
3. Mensajes flash para acceso denegado (403)

### Criterio de aceptación
- 403 muestra template amigable con "No tienes permiso"
- 404 muestra "Página no encontrada"
- 500 muestra "Error interno"

---

## Review Workload Forecast

| Métrica | Estimación |
|---------|-----------|
| **Archivos a crear** | ~30 archivos |
| **Líneas totales estimadas** | ~2,000+ líneas |
| **Líneas backend (Python)** | ~1,200 |
| **Líneas frontend (HTML/Jinja2)** | ~800 |
| **PR único recomendado** | ❌ Excede 400 líneas |
| **Chained PRs recomendado** | ✅ Sí |
| **Decision needed before apply** | ✅ Sí — definir estrategia de PRs |

### Propuesta de división en batches

| Batch | Tareas | Líneas est. | Descripción |
|-------|--------|-------------|-------------|
| **Batch 1: Core** ✅ | T01, T02, T03, T04, T13 | ~310 | Scaffold, models, decorators, audit, seguridad |
| **Batch 2: Auth + Base UI** ✅ | T05, T06, T07, T14 | ~580 | Auth, dashboards, base template, errores |
| **Batch 3: Admin + CRUD** ✅ | T08, T12 | ~420 | Gestión de usuarios, vista auditoría |
| **Batch 4: Tutorías + Disp.** ✅ | T09, T10, T11 | ~700 | Flujo completo de tutorías + disponibilidad |

---

**Status**: ✅ COMPLETED — 14/14 tasks implemented and verified.
**Next phase**: Archive — cambio finalizado.
