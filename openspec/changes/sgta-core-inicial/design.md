# SGTA Core Inicial — Diseño de Arquitectura

**Change:** `sgta-core-inicial`
**Date:** 2026-07-03
**Status:** Draft Design

---

## 1. Estructura del Proyecto

```
sgta-seguridad/
├── app/
│   ├── __init__.py              # Flask app factory (create_app)
│   ├── models.py                # All SQLAlchemy models
│   ├── decorators.py            # @roles_required, @login_required wrappers
│   ├── audit.py                 # log_audit() helper function
│   ├── forms.py                 # All WTForms definitions
│   ├── extensions.py            # Flask extensions init (db, bcrypt, login_manager, talisman)
│   │
│   ├── auth/
│   │   ├── __init__.py          # Blueprint: auth_bp
│   │   ├── routes.py            # /login, /register, /logout
│   │   └── forms.py             # LoginForm, RegisterForm
│   │
│   ├── users/
│   │   ├── __init__.py          # Blueprint: users_bp
│   │   ├── routes.py            # /admin/usuarios/* CRUD
│   │   └── forms.py             # UserForm, EditUserForm
│   │
│   ├── appointments/
│   │   ├── __init__.py          # Blueprint: appointments_bp
│   │   ├── routes.py            # /tutorias/* CRUD
│   │   └── forms.py             # AppointmentForm, FeedbackForm
│   │
│   ├── availability/
│   │   ├── __init__.py          # Blueprint: availability_bp
│   │   ├── routes.py            # /disponibilidad/* CRUD
│   │   └── forms.py             # AvailabilityForm
│   │
│   ├── audit/
│   │   ├── __init__.py          # Blueprint: audit_bp
│   │   └── routes.py            # /admin/auditoria (GET only)
│   │
│   └── templates/
│       ├── base.html            # Base layout (nav, flash messages, footer)
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── dashboard/
│       │   ├── estudiante.html
│       │   ├── docente.html
│       │   └── admin.html
│       ├── users/
│       │   ├── list.html
│       │   ├── create.html
│       │   └── edit.html
│       ├── appointments/
│       │   ├── request.html
│       │   ├── my_list.html
│       │   └── feedback.html
│       ├── availability/
│       │   └── manage.html
│       └── audit/
│           └── log.html
│
├── openspec/                     # SDD artifacts
│   ├── config.yaml
│   └── changes/
│       └── sgta-core-inicial/
│           ├── proposal.md
│           ├── spec.md
│           ├── design.md
│           └── tasks.md
│
├── .atl/
│   ├── skill-registry.md
│   └── .skill-registry.cache.json
│
├── run.py                       # Entry point: `python run.py`
├── config.py                    # Flask configuration classes
└── requirements.txt             # Dependencies
```

---

## 2. Patrón Arquitectónico: Blueprint MVC

Cada módulo de dominio es un **Flask Blueprint** independiente con sus propias rutas, formularios y templates. La app factory en `__init__.py` registra todos los blueprints con prefijos de URL.

```
create_app()
├── init_extensions()           # db, bcrypt, login_manager, talisman
├── register_blueprints()
│   ├── auth_bp        → /auth/*
│   ├── users_bp       → /admin/*
│   ├── appointments_bp → /tutorias/*
│   ├── availability_bp → /disponibilidad/*
│   └── audit_bp       → /admin/auditoria
├── init_error_handlers()       # 403, 404, 500
└── init_context_processors()   # Inject current user, role into all templates
```

---

## 3. Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │   Auth   │ │  Users   │ │Appointm. │ │Availab.  │       │
│  │ Blueprint│ │ Blueprint│ │Blueprint │ │Blueprint │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
│       │            │            │            │              │
│  ┌────┴────────────┴────────────┴────────────┴─────┐       │
│  │              Shared Layer                        │       │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │       │
│  │  │Models (db)│ │decorators│ │ audit.log_audit()│ │       │
│  │  └──────────┘ └──────────┘ └──────────────────┘ │       │
│  │  ┌──────────┐ ┌──────────┐                      │       │
│  │  │  Forms   │ │Extens.   │                      │       │
│  │  └──────────┘ └──────────┘                      │       │
│  └─────────────────────────────────────────────────┘       │
│                                                            │
│  ┌───────────────────────────────────────────────────┐     │
│  │              Jinja2 Templates (UI)                 │     │
│  │  base.html → role-specific dashboards → CRUD views │     │
│  └───────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  Flask-Talisman (CSP, HSTS, X-Frame-Options)                │
│  Flask-Login (session management)                           │
│  WTForms CSRF (form protection)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                  SQLite (dev) / PostgreSQL (prod)
```

---

## 4. Esquema de Base de Datos (ER)

```
┌─────────────────┐       ┌──────────────────────┐
│      User       │       │    Appointment        │
├─────────────────┤       ├──────────────────────┤
│ id (PK)         │◄──────│ student_id (FK)       │
│ username        │       │ teacher_id (FK)       │
│ email           │◄──────│ id (PK)               │
│ password_hash   │       │ subject               │
│ role            │       │ description           │
│ is_active       │       │ status                │
│ created_at      │       │ scheduled_date        │
│ updated_at      │       │ scheduled_time        │
└─────────────────┘       │ feedback              │
        │                 │ created_at            │
        │                 │ updated_at            │
        │                 └──────────────────────┘
        │
        │                 ┌──────────────────────┐
        │                 │    Availability       │
        │                 ├──────────────────────┤
        └────────────────►│ teacher_id (FK)       │
                          │ id (PK)               │
                          │ day_of_week (0-6)     │
                          │ start_time            │
                          │ end_time              │
                          │ is_available          │
                          │ created_at            │
                          └──────────────────────┘

    ┌──────────────────────┐
    │      AuditLog        │
    ├──────────────────────┤
    │ id (PK)              │
    │ user_id (nullable FK)│───► User (optional)
    │ username             │
    │ action               │
    │ table_affected       │
    │ record_id            │
    │ details (JSON text)  │
    │ ip_address           │
    │ created_at           │
    └──────────────────────┘
```

**Relaciones:**
- `User` 1→N `Appointment` (as student)
- `User` 1→N `Appointment` (as teacher)
- `User` 1→N `Availability`
- `User` 1→N `AuditLog` (optional FK)

---

## 5. Diseño de Rutas (Endpoint Design)

### Auth Blueprint (`/auth`)
| Método | Ruta | Función | Roles |
|--------|------|---------|-------|
| GET | `/auth/register` | `register()` | None |
| POST | `/auth/register` | `register()` | None |
| GET | `/auth/login` | `login()` | None |
| POST | `/auth/login` | `login()` | None |
| GET | `/auth/logout` | `logout()` | All auth |

### Users Blueprint (`/admin`)
| Método | Ruta | Función | Roles |
|--------|------|---------|-------|
| GET | `/admin/usuarios` | `list_users()` | admin |
| GET | `/admin/usuarios/crear` | `create_user()` | admin |
| POST | `/admin/usuarios/crear` | `create_user()` | admin |
| GET | `/admin/usuarios/<id>/editar` | `edit_user()` | admin |
| POST | `/admin/usuarios/<id>/editar` | `edit_user()` | admin |
| POST | `/admin/usuarios/<id>/baja` | `deactivate_user()` | admin |

### Appointments Blueprint (`/tutorias`)
| Método | Ruta | Función | Roles |
|--------|------|---------|-------|
| GET | `/tutorias/solicitar` | `request_tutoria()` | estudiante |
| POST | `/tutorias/solicitar` | `request_tutoria()` | estudiante |
| GET | `/tutorias/mis-tutorias` | `my_tutorias()` | estudiante |
| POST | `/tutorias/<id>/cancelar` | `cancel_tutoria()` | estudiante |
| GET | `/tutorias/<id>/feedback` | `feedback_form()` | docente |
| POST | `/tutorias/<id>/feedback` | `feedback_form()` | docente |
| POST | `/tutorias/<id>/aceptar` | `accept_tutoria()` | docente |
| GET | `/docente/agendados` | `assigned_students()` | docente |

### Availability Blueprint (`/disponibilidad`)
| Método | Ruta | Función | Roles |
|--------|------|---------|-------|
| GET | `/disponibilidad/` | `manage_availability()` | docente |
| POST | `/disponibilidad/crear` | `create_slot()` | docente |
| POST | `/disponibilidad/<id>/eliminar` | `delete_slot()` | docente |

### Audit Blueprint (`/admin`)
| Método | Ruta | Función | Roles |
|--------|------|---------|-------|
| GET | `/admin/auditoria` | `view_audit_log()` | admin |

### Root
| Método | Ruta | Función | Roles |
|--------|------|---------|-------|
| GET | `/` | Home / landing | None |
| GET | `/dashboard` | `dashboard()` | All auth → redirects by role |

---

## 6. Arquitectura de Seguridad

```
┌──────────────────────────────────────────┐
│            Request Flow                   │
│                                          │
│ 1. Flask-Talisman headers applied        │
│    (CSP, HSTS, XFO, XSS protection)      │
│                                          │
│ 2. WTForms CSRF token validated          │
│    (on all POST/PUT/DELETE)              │
│                                          │
│ 3. Flask-Login @login_required           │
│    (session cookie checked)              │
│                                          │
│ 4. @roles_required('admin') decorator    │
│    (role check against User.role)        │
│                                          │
│ 5. Route handler executes                │
│    - Input validated by WTForms          │
│    - DB via SQLAlchemy (param queries)   │
│    - Audit logged via log_audit()        │
│                                          │
│ 6. Jinja2 autoescaping renders output    │
└──────────────────────────────────────────┘
```

### RBAC Decorator Implementation Pattern

```python
def roles_required(*roles):
    def decorator(f):
        @functools.wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### Audit Helper Pattern

```python
def log_audit(action, table_affected, record_id=None, details=None):
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        username=current_user.username if current_user.is_authenticated else 'anonymous',
        action=action,
        table_affected=table_affected,
        record_id=record_id,
        details=json.dumps(details) if details else None,
        ip_address=request.remote_addr or '0.0.0.0'
    )
    db.session.add(log)
    db.session.commit()
```

---

## 7. Diseño de Frontend

### Base Template (`base.html`)
```
┌──────────────────────────────────────┐
│  Navbar (role-based menu)            │
│  ├── Logo / Home                     │
│  ├── Estudiante: Solicitar | Mis T.  │
│  ├── Docente: Disponibilidad | Agr.  │
│  ├── Admin: Usuarios | Auditoría     │
│  └── Cerrar sesión                   │
├──────────────────────────────────────┤
│  Flash messages (dismissible)        │
│  ┌────────────────────────────────┐  │
│  │ ✓ Success / ✗ Error / ⚠ Info  │  │
│  └────────────────────────────────┘  │
├──────────────────────────────────────┤
│  {% block content %}                │
│  (Page-specific content)            │
│  └────────────────────────────────┘ │
├──────────────────────────────────────┤
│  Footer                             │
│  SGTA v1.0 — © 2026                │
└──────────────────────────────────────┘
```

### CSS Framework Decision: Bootstrap 5
- **Razón:** Componentes listos (tables, forms, alerts, navbar, modals), grid responsive, consistente con WTForms rendering
- CDN: Bootstrap 5.3 via jsDelivr + Bootstrap Icons

### Color Palette (Security-Themed)
- Primary: `#0d6efd` (Bootstrap blue — trust)
- Success: `#198754` (green — confirmations)
- Danger: `#dc3545` (red — errors, cancellations)
- Warning: `#ffc107` (amber — pending states)

---

## 8. Configuración de Flask

```python
# config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-change-in-prod'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sgta.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_ROUNDS = 12
    TALISMAN_FORCE_HTTPS = False  # True in production
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'style-src': ["'self'", 'https://cdn.jsdelivr.net'],
        'script-src': ["'self'", 'https://cdn.jsdelivr.net'],
    }
```

---

## 9. Decisiones Técnicas y Tradeoffs

| Decisión | Alternativa | Por qué |
|----------|-------------|---------|
| **SQLite** vs PostgreSQL | PostgreSQL para prod | SQLite simplifica setup inicial; migrar después |
| **Bootstrap** vs Tailwind | Tailwind para proyectos diseño-heavy | Bootstrap tiene componentes listos para CRUD rápido |
| **Unico models.py** vs models por blueprint | Separar en módulos | Un archivo es suficiente para MVP; refactorizar después |
| **Jinja2** vs SPA (React/Vue) | SPA para mejor UX | Jinja2 + Bootstrap es más rápido de implementar y seguro por defecto (autoescaping) |
| **Decorador custom** vs Flask-Principal | Flask-Principal para RBAC complejo | Decorador simple y explícito; Flask-Principal agrega complejidad innecesaria para 3 roles |

---

**Next phase**: Tasks — breakdown into implementation tasks with dependencies.
