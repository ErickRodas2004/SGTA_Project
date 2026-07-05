# SGTA — Documento de Seguridad de la Información
**Sistema de Gestión de Tutorías Académicas**
**Fecha:** Julio 2026

---

## 1. IDENTIFICACIÓN Y VALORIZACIÓN DE ACTIVOS (para Analista 1)

### 1.1 Inventario de Activos de Información

| Activo | Descripción | Ubicación/Formato | Dueño | Clasificación |
|--------|-------------|-------------------|-------|---------------|
| Datos de usuarios | username, email, password_hash, rol, estado activo/inactivo | BD SQLite (`instance/sgta.db`), tabla `users` | Administrador del sistema | C: Alto, I: Alto, D: Medio |
| Credenciales de acceso | Password en tránsito (formulario HTTPS), hash almacenado (bcrypt) | Tránsito: POST HTTP → BD; Reposo: columna `password_hash` (hash bcrypt $2b$12$) | Usuario / Sistema | C: Alto, I: Alto, D: Bajo |
| Datos de tutorías | Citas (student_id, teacher_id, subject, status, fechas, feedback) | BD SQLite, tabla `appointments` | Estudiantes y Docentes | C: Medio, I: Alto, D: Medio |
| Datos de disponibilidad horaria | Bloques horarios por docente (day_of_week, start/end_time) | BD SQLite, tabla `availability` | Docentes | C: Bajo, I: Medio, D: Bajo |
| Registros de auditoría | AuditLog completo (user_id, acción, tabla, IP, timestamp, detalles) | BD SQLite, tabla `audit_logs` | Administrador del sistema | C: Alto, I: Alto, D: Medio |
| Cookies de sesión | Cookie firmada por Flask-Login con SECRET_KEY | Navegador del usuario (httpOnly, SameSite=Lax) | Usuario / Sistema | C: Alto, I: Alto, D: Bajo |
| Configuración de la aplicación | SECRET_KEY, BCRYPT_LOG_ROUNDS, CSP, CSRF config | `config.py`, variable de entorno `SECRET_KEY` | Administrador del sistema | C: Alto, I: Alto, D: Bajo |
| Base de datos completa | `sgta.db` — todas las tablas del sistema | `instance/sgta.db` (archivo SQLite) | Administrador del sistema | C: Alto, I: Alto, D: Alto |
| Código fuente de la aplicación | Python/Flask, templates, formularios, rutas | Directorio `app/`, `config.py`, `run.py` | Equipo de desarrollo | C: Medio, I: Alto, D: Bajo |
| Variables de entorno / secretos | SECRET_KEY, configuración de producción | Shell/variable de entorno | Administrador del sistema | C: Alto, I: Alto, D: Bajo |

### 1.2 Valorización por el modelo CIA (Confidencialidad, Integridad, Disponibilidad)

| Activo | Confidencialidad | Integridad | Disponibilidad |
|--------|-----------------|------------|----------------|
| Datos de usuarios | **Alto** — Contienen información personal (email) y hashes de contraseña. Su exposición permitiría ataques de suplantación. | **Alto** — La modificación no autorizada de roles o credenciales compromete todo el sistema. | **Medio** — El sistema funciona sin consultar usuarios constantemente, pero el login los requiere. |
| Credenciales de acceso | **Alto** — La exposición del hash permite ataques offline de fuerza bruta. | **Alto** — Un hash manipulado permitiría autenticación sin conocer la contraseña. | **Bajo** — La pérdida temporal no afecta porque el hash está en BD y se regenera al cambiar password. |
| Datos de tutorías | **Medio** — Contienen información académica (materias, fechas) no crítica pero privada. | **Alto** — La alteración de estados (pending→accepted/completed) o feedback falso afecta el registro académico. | **Medio** — Los estudiantes y docentes necesitan consultar sus tutorías regularmente. |
| Datos de disponibilidad horaria | **Bajo** — La disponibilidad de un docente no es información sensible. | **Medio** — La manipulación podría causar conflictos de agenda. | **Bajo** — Solo se usa al crear disponibilidad y al solicitar tutoría. |
| Registros de auditoría | **Alto** — Contienen trazabilidad completa de acciones, IPs, y cambios. Clave para forense. | **Alto** — La alteración destruiría la pista de auditoría y el no-repudio. | **Medio** — No es crítico en tiempo real, pero debe estar disponible para investigación. |
| Cookies de sesión | **Alto** — Permiten suplantación completa si son robadas (sesión hijacking). | **Alto** — Una cookie manipulada puede suplantar a cualquier usuario. | **Bajo** — Se regeneran en cada login. La pérdida solo obliga a re-autenticar. |
| Configuración de la aplicación | **Alto** — SECRET_KEY firma cookies y CSRF tokens. Su exposición permite forjar sesiones. | **Alto** — Modificar CSP, BCrypt rounds, o CSRF timeout debilita la seguridad. | **Bajo** — Solo se lee al iniciar la app. Se restaura desde el repositorio o backup. |
| Base de datos completa | **Alto** — Contiene TODOS los datos del sistema. | **Alto** — Pérdida total de integridad = sistema inservible. | **Alto** — Sin BD el sistema no funciona. |
| Código fuente de la aplicación | **Medio** — Código abierto/visible al equipo, pero lógica de negocio y configuración pueden ser sensibles. | **Alto** — La modificación maliciosa puede introducir backdoors o vulnerabilidades. | **Bajo** — El código desplegado no cambia frecuentemente. |
| Variables de entorno / secretos | **Alto** — La SECRET_KEY en producción es crítica para la seguridad de sesiones y tokens. | **Alto** — Valores incorrectos pueden romper la autenticación o la seguridad de headers. | **Bajo** — Se configuran una vez y se mantienen estables. |

### 1.3 Impacto Potencial

| Activo | Impacto de pérdida de Confidencialidad | Impacto de pérdida de Integridad | Impacto de pérdida de Disponibilidad |
|--------|---------------------------------------|----------------------------------|--------------------------------------|
| Datos de usuarios | Filtración de datos personales (email, nombres de usuario). Posible violación de RGPD/LOPD. Ataques de phishing dirigidos. | Cuentas modificadas permiten acceso no autorizado a datos académicos. Asignación fraudulenta de roles. | Imposibilidad de registrar nuevos usuarios o autenticar existentes. |
| Credenciales de acceso | Ataque offline de fuerza bruta sobre hashes bcrypt. Si el password es débil, se compromete la cuenta. | Login sin autenticación real. Suplantación total del sistema. | Sin impacto: el hash no es necesario en tiempo real para el funcionamiento. |
| Datos de tutorías | Exposición de historial académico de estudiantes (qué estudian, con quién, cuándo). | Tutorías marcadas como completadas sin realizarse. Feedback fraudulento. Notas académicas falsas. | Estudiantes no pueden ver su agenda. Docentes no ven sus pendientes. |
| Registros de auditoría | Exposición de IPs, patrones de uso, quién hizo qué. Información para ataques dirigidos. | Imposibilidad de detectar accesos no autorizados o modificaciones ilegítimas. Pérdida de pista forense. | No se puede investigar incidentes de seguridad. Pérdida de compliance. |
| Cookies de sesión | Suplantación completa de usuarios. Acceso a funcionalidades según el rol de la víctima. | Modificación de la cookie permite escalar privilegios o suplantar identidad. | Usuarios deben re-autenticarse constantemente. |
| Configuración de la aplicación | Exposición de SECRET_KEY → forjar cualquier cookie de sesión o CSRF token. | Modificar CSP permite XSS. Bajar BCrypt rounds acelera ataques de fuerza bruta. Deshabilitar CSRF permite ataques CSRF. | Sin configuración válida la app no inicia o funciona incorrectamente. |
| Base de datos completa | **Máximo impacto**: todos los datos del sistema expuestos. | **Máximo impacto**: pérdida total de confianza en los datos. | **Máximo impacto**: sistema completamente caído. |
| Código fuente | Exposición de lógica de negocio, configuración (posibles secretos hardcodeados), patrones de seguridad. | Introducción de vulnerabilidades (backdoors, SQLi, XSS) por código malicioso. | Sin código la aplicación no puede ejecutarse. |

---

## 2. MATRIZ DE RIESGOS Y PLAN DE MITIGACIÓN (para Analista 1)

### 2.1 Identificación de Amenazas

| # | Amenaza | Activo Afectado | Origen | Probabilidad | Impacto | Nivel de Riesgo |
|---|---------|-----------------|--------|-------------|---------|-----------------|
| 1 | **Robo de credenciales** (fuerza bruta, sniffing, sesión hijacking) | Credenciales, Cookies de sesión | Externo / Red | Media | Alto | **Alto** |
| 2 | **Inyección de código** (SQLi, XSS) | BD, Templates, Usuarios | Externo / Web | Baja | Alto | **Medio** |
| 3 | **Alteración de registros** (modificación no autorizada de tutorías o usuarios) | Datos de tutorías, Datos de usuarios | Interno / Externo | Media | Alto | **Alto** |
| 4 | **Acceso no autorizado** (escalada de privilegios, bypass de roles) | Datos de usuarios, Tutorías, Auditoría | Interno / Externo | Media | Alto | **Alto** |
| 5 | **Suplantación de identidad** (session fixation, cookie theft) | Cookies de sesión, Datos de usuarios | Externo / Red | Media | Alto | **Alto** |
| 6 | **Pérdida de datos** (falta de backups, corrupción de BD) | BD completa | Interno / Accidental | Media | Alto | **Alto** |
| 7 | **Ataque CSRF** (ejecución de acciones sin consentimiento) | Sesión del usuario | Externo / Web | Baja | Medio | **Bajo** |
| 8 | **Clickjacking** (secuestro de clics en iframes maliciosos) | Sesión del usuario | Externo / Web | Baja | Medio | **Bajo** |
| 9 | **Fuga de información** (error messages, debug info expuesta) | Configuración, Datos de usuarios | Externo / Web | Media | Medio | **Medio** |

### 2.2 Medidas de Seguridad Implementadas (justificación técnica detallada)

#### 1. Flask-Bcrypt — Hashing de contraseñas

**Qué problema resuelve:** Las contraseñas nunca deben almacenarse en texto plano. Si la base de datos se ve comprometida, los hashes bcrypt son computacionalmente costosos de revertir, protegiendo las credenciales incluso con hashes expuestos.

**Implementación en SGTA** (`app/models.py`, líneas 58-64):

```python
def set_password(self, password: str) -> None:
    """Hash and store the password using bcrypt."""
    self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(self, password: str) -> bool:
    """Verify a plain-text password against the stored bcrypt hash."""
    return bcrypt.check_password_hash(self.password_hash, password)
```

**Configuración** (`config.py`, línea 15):
```python
BCRYPT_LOG_ROUNDS = 12
```

**Efectividad:**
- Cost factor 12 (~250ms por hash en hardware moderno) hace que ataques de fuerza bruta sean inviables: probar 1000 contraseñas tomaría ~4 minutos por hash.
- Cada hash incluye un salt automático de 128 bits (integrado en el propio hash `$2b$12$...`), lo que hace que los ataques con rainbow tables sean imposibles — dos usuarios con la misma contraseña tienen hashes completamente diferentes.
- El algoritmo bcrypt está específicamente diseñado para ser lento en GPU/FPGA, a diferencia de SHA256 o MD5 que son rápidos y paralelizables.
- Ver evidencia en BD: los hashes reales almacenados comienzan con `$2b$12$`, confirmando 12 rounds de bcrypt.

#### 2. Flask-Login + RBAC — Gestión de sesiones y control de acceso basado en roles

**Qué problema resuelve:** Controlar qué usuarios pueden acceder a qué rutas y funcionalidades. Las sesiones deben ser seguras, con renovación periódica y verificación en cada request.

**Implementación del decorador RBAC** (`app/decorators.py`, líneas 9-45):

```python
def roles_required(*roles):
    """Decorator — restrict route access to one or more roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor inicia sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))

            if not current_user.is_active:
                flash('Tu cuenta está desactivada.', 'danger')
                return redirect(url_for('auth.login'))

            if current_user.role not in roles:
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

**Defensa en profundidad:** Cada ruta protegida usa dos decoradores anidados:
1. `@login_required` (Flask-Login) — verifica que hay una sesión activa y válida
2. `@roles_required('rol')` (decorador personalizado) — verifica el rol específico

Esto significa que incluso si un decorador falla, el otro sigue protegiendo. Ejemplo típico en rutas:

```python
@users_bp.route('/usuarios')
@login_required
@roles_required('administrador')
def list_users():
    ...
```

#### 3. Flask-Talisman — Seguridad de comunicaciones

**Qué problema resuelve:** Los navegadores necesitan instrucciones explícitas sobre cómo manejar el contenido y las conexiones. Sin estos headers, la aplicación es vulnerable a clickjacking, MIME sniffing, XSS y ataques MITM.

**Configuración en SGTA** (`config.py`, líneas 17-31 y `app/__init__.py`, líneas 19-23):

```python
# config.py
TALISMAN_CONTENT_SECURITY_POLICY = {
    'default-src': "'self'",
    'style-src': ["'self'", 'https://cdn.jsdelivr.net'],
    'script-src': ["'self'", 'https://cdn.jsdelivr.net'],
    'font-src': ["'self'", 'https://cdn.jsdelivr.net'],
    'img-src': ["'self'", 'data:'],
}
TALISMAN_X_FRAME_OPTIONS = 'DENY'
TALISMAN_X_CONTENT_TYPE_OPTIONS = 'nosniff'
TALISMAN_SESSION_COOKIE_SECURE = False  # True en producción
TALISMAN_SESSION_COOKIE_HTTPONLY = True
TALISMAN_SESSION_COOKIE_SAMESITE = 'Lax'
```

```python
# __init__.py
talisman.init_app(
    flask_app,
    force_https=False,
    content_security_policy=config_class.TALISMAN_CONTENT_SECURITY_POLICY,
)
```

**Headers aplicados:**
- **CSP** (Content-Security-Policy): `default-src 'self'` — solo se permite cargar recursos del mismo origen. Se exceptúan Bootstrap y Bootstrap Icons desde CDN de jsdelivr.net. Esto mitiga XSS incluso si hay un bug en el código, porque scripts inline maliciosos no se ejecutarían.
- **X-Frame-Options: DENY** — imposibilita cargar la aplicación en un iframe, protegiendo contra clickjacking.
- **X-Content-Type-Options: nosniff** — evita que el navegador adivine el MIME type (MIME sniffing), previniendo ataques donde un archivo .txt se interpreta como .html con scripts maliciosos.
- **Session cookie httpOnly=True** — la cookie de sesión no es accesible desde JavaScript, protegiendo contra XSS que intente robar la cookie.
- **Session cookie SameSite=Lax** — la cookie solo se envía en navegación de alto nivel (clics en enlaces), protegiendo contra ataques CSRF.

#### 4. WTForms + CSRF — Protección contra Cross-Site Request Forgery

**Qué problema resuelve:** Un atacante no puede engañar a un usuario autenticado para que ejecute acciones no deseadas (cambiar email, crear usuario, cancelar tutoría) desde un sitio malicioso.

**Configuración** (`config.py`, líneas 33-34):
```python
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 3600  # 1 hora
```

**Implementación:** Cada formulario incluye `{{ form.hidden_tag() }}` que genera un campo oculto con un token CSRF único y firmado. Ejemplo en login (`app/templates/auth/login.html`, línea 17):

```html
<form method="POST" action="{{ url_for('auth.login') }}">
    {{ form.hidden_tag() }}
    ...
</form>
```

El token CSRF está ligado a la sesión del usuario y expira después de 3600 segundos (1 hora). Cada formulario tiene su propio token, por lo que interceptar un token no permite reutilizarlo en otro formulario.

#### 5. SQLAlchemy ORM — Prevención de Inyección SQL

**Qué problema resuelve:** La inyección SQL (SQLi) ocurre cuando datos no confiables se concatenan en consultas SQL. SQLAlchemy ORM parametriza automáticamente todas las consultas, separando el código SQL de los datos.

**Implementación en SGTA:** En **todo el código fuente** se usa SQLAlchemy ORM. No existe ni una sola consulta SQL cruda. Ejemplos:

- `User.query.filter_by(username=form.username.data).first()` (`auth/routes.py:46`)
- `Appointment.query.filter_by(teacher_id=current_user.id).all()` (`appointments/routes.py:123-126`)
- `AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(...)` (`audit/routes.py:19-24`)

Incluso la construcción dinámica de filtros usa métodos ORM:
```python
query = Appointment.query.filter_by(student_id=current_user.id)
if status_filter:
    query = query.filter_by(status=status_filter)
```

La parametrización ocurre en la capa del dialecto SQLAlchemy para SQLite, que escapa y entrecomilla los valores automáticamente.

#### 6. Jinja2 Autoescapado — Prevención de XSS

**Qué problema resuelve:** Cross-Site Scripting (XSS) ocurre cuando datos ingresados por usuarios se renderizan como HTML sin escapar, permitiendo la inyección de scripts maliciosos.

**Implementación:** Jinja2 (el motor de templates de Flask) escapa automáticamente el contenido en bloques `{{ }}`. Caracteres como `<`, `>`, `"`, `&` se convierten a entidades HTML (`&lt;`, `&gt;`, etc.). Todo el contenido dinámico en los templates usa doble llave `{{ }}`, nunca `{% raw %}`.

Además, la política CSP (`default-src 'self'`, `script-src 'self' + CDN`) actúa como segunda capa de defensa: incluso si un script se inyecta vía un template, el navegador lo bloquearía por CSP.

#### 7. AuditLog — Registro Inmutable de Acciones Sensibles

**Qué problema resuelve:** Sin auditoría, es imposible determinar qué ocurrió durante un incidente de seguridad. El registro debe capturar quién, qué, cuándo y desde dónde.

**Estructura del modelo** (`app/models.py`, líneas 130-150):
```python
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    username = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(100), nullable=False, index=True)
    table_affected = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON-encoded
    ip_address = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
```

**Función de registro** (`app/log_audit.py`, líneas 13-41):
```python
def log_audit(action, table_affected, record_id=None, details=None):
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
```

**Detalles importantes:**
- El `username` se guarda explícitamente (no solo el `user_id` FK) para preservar la trazabilidad incluso si el usuario se elimina posteriormente.
- La IP se captura del request real (`request.remote_addr`).
- Los detalles se almacenan como JSON estructurado para consultas forenses.
- `user_id` es nullable para acciones que ocurren antes de la autenticación (registro de usuario).
- `created_at` usa UTC con timezone-aware datetime.

#### 8. Validación WTForms — Validación en backend

**Qué problema resuelve:** Los datos maliciosos o inválidos deben rechazarse en el servidor. La validación solo en frontend es insegura porque puede omitirse.

**Implementación:** Todos los formularios usan validadores WTForms que se ejecutan en el servidor:

- **Unicidad de username/email** (`auth/forms.py`, líneas 50-58):
  ```python
  def validate_username(self, field):
      if User.query.filter_by(username=field.data).first():
          raise ValidationError('Este nombre de usuario ya está registrado.')
  ```

- **Fecha futura** (`appointments/forms.py`, líneas 56-59):
  ```python
  def validate_scheduled_date(self, field):
      if field.data and field.data <= date.today():
          raise ValidationError('La fecha debe ser posterior a hoy.')
  ```

- **Longitud mínima de password** (8 caracteres, en `auth/forms.py` y `users/forms.py`)
- **Email válido** con validador `Email()` de WTForms + `email-validator`
- **Start < end time** (`availability/forms.py`, líneas 41-45):
  ```python
  def validate_end_time(self, field):
      if self.start_time.data and field.data and self.start_time.data >= field.data:
          raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')
  ```

### 2.3 Plan de Mitigación Detallado

| # | Amenaza | Medidas que la Mitigan | Estado | Recomendación |
|---|---------|----------------------|--------|---------------|
| 1 | Robo de credenciales | Bcrypt (cost 12), httpOnly cookies, SameSite=Lax, bloqueo de cuenta desactivada | **Implementado** | Agregar rate limiting en login (Flask-Limiter) y bloqueo tras N intentos fallidos. Implementar forced HTTPS. |
| 2 | Inyección SQL / XSS | SQLAlchemy ORM (no raw SQL), Jinja2 autoescapado, CSP restrictivo | **Implementado** | Verificar que no haya `|safe` sin necesidad en templates. Monitorear que no se introduzca SQL crudo en el futuro. |
| 3 | Alteración de registros | RBAC con decoradores, guards por ownership (ej: `appointment.student_id != current_user.id`), AuditLog | **Implementado** | AuditLog no es inmutable en SQLite (UPDATE/DELETE directo). Considerar append-only log o trigger de BD. |
| 4 | Acceso no autorizado / escalada | RBAC doble decorador (`@login_required` + `@roles_required`), guards de ownership | **Implementado** | Verificar que todas las rutas POST tengan ambos decoradores. **BUG detectado**: en `cancel_tutoria` (línea 103) se registra `previous_status` después de cambiarlo, por lo que siempre dice "cancelled". |
| 5 | Suplantación de identidad | Flask-Login con sesiones del lado servidor, httpOnly cookie, SameSite=Lax, SECRET_KEY | **Implementado** | Asegurar SECRET_KEY en producción con variable de entorno (no el default). Considere renovar SECRET_KEY periódicamente. |
| 6 | Pérdida de datos | No hay sistema de backups implementado | **No implementado** | **CRÍTICO**: Implementar backup automatizado de `instance/sgta.db`. SQLite no soporta replication nativa. Considere migrar a PostgreSQL si se requiere alta disponibilidad. |
| 7 | CSRF | WTForms CSRF tokens (tiempo límite 3600s), SameSite=Lax | **Implementado** | Verificar que todos los formularios incluyan `form.hidden_tag()`. Los formularios de búsqueda/filtro (GET) no necesitan CSRF. |
| 8 | Clickjacking | Talisman `X-Frame-Options: DENY` | **Implementado** | No requiere acciones adicionales. |
| 9 | Fuga de información | Error handlers (403, 404, 500) con templates personalizados. `debug=False` en producción. | **Parcial** | `run.py` línea 8 tiene `app.run(debug=True)`. En producción debe ser `debug=False`. No usar `run.py` para producción — usar Gunicorn + Nginx. |

---

## 3. ARQUITECTURA DE SEGURIDAD (para Analista 2)

### 3.1 Diagrama de Arquitectura (descripción textual para que el analista lo dibuje)

**Vista General:**

```
[Navegador Usuario]
       |
       | HTTPS (en producción) / HTTP (en desarrollo)
       |
[Flask Application Server]
  |-- Flask-Talisman (middleware de seguridad: CSP, HSTS, XFO, HTP)
  |-- Flask-WTF CSRF (middleware de tokens CSRF por formulario)
  |-- Flask-Login (gestión de sesiones)
  |
  |-- [Blueprints]
  |     |-- /auth → register, login, logout
  |     |-- / (main) → dashboard, landing
  |     |-- /admin → usuarios CRUD, auditoría
  |     |-- /tutorias → solicitar, cancelar, aceptar, feedback
  |     |-- /disponibilidad → gestión de horarios
  |
  |-- [SQLAlchemy ORM] → parametrización automática
       |
       [SQLite: instance/sgta.db]
         |-- users
         |-- appointments
         |-- availability
         |-- audit_logs
```

**Flujo de Autenticación:**

1. El usuario ingresa credenciales en el formulario de login (`/auth/login`)
2. WTForms valida los datos: campos obligatorios, formato de email (no aplica en login), longitud
3. El formulario incluye `form.hidden_tag()` que genera un token CSRF único
4. Se envía POST a `/auth/login` con: `username`, `password`, `remember_me`, `csrf_token`
5. Flask-Login busca al usuario por `username` en la BD: `User.query.filter_by(username=form.username.data).first()`
6. Si el usuario no existe → flash "Credenciales inválidas" + render template (sin revelar si el usuario existe)
7. Si existe, se verifica el hash: `user.check_password(form.password.data)` → llama a `bcrypt.check_password_hash(self.password_hash, password)`
8. Si el password es incorrecto → flash "Credenciales inválidas" (mensaje genérico, no revela cuál es incorrecto)
9. Si la cuenta está desactivada (`not user.is_active`) → flash "Tu cuenta está desactivada"
10. Si todo OK: `login_user(user, remember=form.remember_me.data)` crea la sesión
11. Se registra en AuditLog: `log_audit('LOGIN', 'users', record_id=user.id)` con IP del request
12. Redirección post-login:
    - Si hay parámetro `next` en URL y comienza con `/` → redirect a esa URL
    - Si no: según rol, todos los roles van a `main.dashboard`
13. `main.dashboard` renderiza template según rol: `estudiante.html`, `docente.html`, `admin.html`

**Flujo de Autorización (RBAC):**

1. Cada ruta protegida tiene `@login_required` (verifica sesión activa)
2. Inmediatamente después, `@roles_required('rol')` verifica:
   - `current_user.is_authenticated` → False: redirect a login con flash
   - `current_user.is_active` → False: flash "cuenta desactivada" + redirect a login
   - `current_user.role not in roles` → `abort(403)` → template `errors/403.html`
3. Guards adicionales por ownership en cada operación:
   - `appointment.student_id != current_user.id` → flash "No puedes cancelar una tutoría que no te pertenece"
   - `appointment.teacher_id != current_user.id` → flash "No puedes aceptar una tutoría que no te fue asignada"
   - `user.id == current_user.id` y acción es DEACTIVATE → flash "No puedes desactivar tu propia cuenta"
4. Template navbar renderiza opciones según `current_user.role`:
   - `estudiante`: Solicitar Tutoría, Mis Tutorías
   - `docente`: Mi Disponibilidad, Estudiantes Agendados
   - `administrador`: Usuarios, Auditoría
   - No autenticado: Iniciar sesión, Registrarse

**Flujo de Cifrado en Tránsito:**

1. Flask-Talisman aplica headers de seguridad a TODAS las respuestas HTTP
2. `Content-Security-Policy`: `default-src 'self'` → todo contenido debe ser del mismo origen
3. `style-src`: permite `'self'` y `https://cdn.jsdelivr.net` (Bootstrap CSS con SRI)
4. `script-src`: permite `'self'` y `https://cdn.jsdelivr.net` (Bootstrap JS con SRI)
5. `X-Frame-Options: DENY` → imposible cargar en iframe
6. `X-Content-Type-Options: nosniff` → no MIME sniffing
7. Cookie de sesión: `HttpOnly`, `SameSite=Lax`
8. En producción: `force_https=True` y `SESSION_COOKIE_SECURE=True` (requiere TLS configurado en Nginx/reverse proxy)

**Aislamiento de Base de Datos:**

1. SQLite con archivo único `instance/sgta.db`
2. El archivo está dentro de `instance/` que no es servido por Flask (por defecto)
3. Solo el proceso de la aplicación tiene acceso al archivo (a nivel de sistema operativo)
4. SQLAlchemy ORM como única capa de acceso a datos — no hay SQL directo en ninguna parte
5. Modelos separados por dominio: `User`, `Appointment`, `Availability`, `AuditLog`
6. Relaciones explícitas entre modelos con ForeignKeys:
   - `appointments.student_id` → `users.id`
   - `appointments.teacher_id` → `users.id`
   - `availability.teacher_id` → `users.id`
   - `audit_logs.user_id` → `users.id`

### 3.2 Diseño de Red / Comunicaciones

**Arquitectura actual (desarrollo):**
- **Cliente-Servidor tradicional** con Flask como servidor de desarrollo
- Flask corre en `http://127.0.0.1:5000` con `app.run(debug=True)` (NO seguro para producción)
- Comunicación HTTP plano (sin TLS en desarrollo)
- Sesiones gestionadas del lado del servidor con cookies firmadas (no JWT)
- Base de datos SQLite local en el servidor

**Arquitectura recomendada para producción:**

```
[Cliente] --HTTPS (TLS 1.3)--> [Nginx reverse proxy] --HTTP--> [Gunicorn WSGI] --> [Flask App] --> [SQLite/PostgreSQL]
                                  |
                                  |--> Sirve archivos estáticos
                                  |--> Termina TLS con certificado Let's Encrypt
                                  |--> Headers de seguridad adicionales (HSTS)
```

**Recomendaciones de producción:**
- **TLS 1.3** con certificado de Let's Encrypt (renovación automática con Certbot)
- **Nginx** como reverse proxy: termina TLS, sirve archivos estáticos, proxy inverso a Gunicorn
- **Gunicorn** como servidor WSGI: `gunicorn -w 4 -b 127.0.0.1:8000 run:app`
- **Headers HSTS** desde Nginx o Flask-Talisman para forzar HTTPS
- **Migrar a PostgreSQL** si se requiere alta disponibilidad, concurrencia, o backups point-in-time
- **Firewall** que solo exponga puertos 80 (redirección a 443) y 443

**Seguridad de sesiones:**
- Cookies de sesión: httpOnly (no accesibles desde JS), SameSite=Lax, Secure (solo HTTPS)
- Sesiones del lado del servidor con Flask-Login (no JWT) — la sesión contiene solo el ID del usuario
- El estado real de la sesión se valida contra la BD en cada request via `user_loader`
- No hay tokens JWT que puedan ser interceptados y reutilizados fuera de la sesión

### 3.3 Modelo de Roles y Permisos Detallado

| Rol | Permisos | Rutas Accesibles | Funcionalidad |
|-----|----------|------------------|---------------|
| **estudiante** | `ver_horarios`, `solicitar_tutoria`, `ver_mis_tutorias`, `cancelar_tutoria` | `/solicitar` (GET/POST), `/mis-tutorias` (GET), `/<id>/cancelar` (POST) | Solicitar nuevas tutorías, ver historial de sus tutorías, cancelar tutorías pendientes |
| **docente** | `gestionar_disponibilidad`, `ver_estudiantes_agendados`, `aceptar_tutoria`, `registrar_feedback` | `/disponibilidad/` (GET), `/disponibilidad/crear` (POST), `/disponibilidad/<id>/eliminar` (POST), `/docente/agendados` (GET), `/<id>/aceptar` (POST), `/<id>/feedback` (GET/POST) | Gestionar bloques de disponibilidad, ver estudiantes agendados, aceptar/rechazar tutorías, registrar feedback |
| **administrador** | `gestion_usuarios`, `asignar_roles`, `ver_auditoria` | `/admin/usuarios` (GET), `/admin/usuarios/crear` (GET/POST), `/admin/usuarios/<id>/editar` (GET/POST), `/admin/usuarios/<id>/baja` (POST), `/admin/auditoria` (GET) | CRUD completo de usuarios (crear, editar, desactivar), consultar registro de auditoría |

**Código real de los decoradores RBAC** (`app/decorators.py`):

```python
def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor inicia sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))

            if not current_user.is_active:
                flash('Tu cuenta está desactivada.', 'danger')
                return redirect(url_for('auth.login'))

            if current_user.role not in roles:
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

**Uso en rutas:**

Ruta de estudiante:
```python
@appointments_bp.route('/solicitar', methods=['GET', 'POST'])
@login_required
@roles_required('estudiante')
def request_tutoria():
    ...
```

Ruta de docente:
```python
@appointments_bp.route('/docente/agendados')
@login_required
@roles_required('docente')
def assigned_students():
    ...
```

Ruta de administrador:
```python
@audit_bp.route('/auditoria')
@login_required
@roles_required('administrador')
def view_audit_log():
    ...
```

---

## 4. AUDITORÍA Y VALIDACIÓN (para Analista 3)

### 4.1 Estructura del AuditLog

La tabla `audit_logs` se define en `app/models.py` (líneas 130-150) con la siguiente estructura exacta verificada en la BD:

| Campo | Tipo SQL | Python | Ejemplo | Notas |
|-------|----------|--------|---------|-------|
| `id` | INTEGER (PK) | `db.Integer, primary_key=True` | 1 | Auto-incremental, clave primaria |
| `user_id` | INTEGER (FK→users.id, nullable) | `db.Integer, db.ForeignKey('users.id'), nullable=True` | 1 | Puede ser `NULL` para acciones sin sesión (ej: registro) |
| `username` | VARCHAR(80) NOT NULL | `db.String(80), nullable=False` | "admin" | Se guarda explícitamente, no depende de FK, preserva trazabilidad si el usuario se elimina |
| `action` | VARCHAR(100) NOT NULL, INDEX | `db.String(100), nullable=False, index=True` | "LOGIN" | Indexado para búsquedas y filtros en la vista de auditoría |
| `table_affected` | VARCHAR(50) NOT NULL | `db.String(50), nullable=False` | "users" | Tabla donde ocurrió la acción |
| `record_id` | INTEGER (nullable) | `db.Integer, nullable=True` | 5 | ID del registro afectado (nullable para acciones sin registro específico) |
| `details` | TEXT (nullable) | `db.Text, nullable=True` | `{"ip": "127.0.0.1"}` | JSON-encoded con contexto adicional estructurado |
| `ip_address` | VARCHAR(45) NOT NULL | `db.String(45), nullable=False` | "192.168.1.10" | Soporta IPv4 e IPv6. Máximo 45 caracteres |
| `created_at` | DATETIME, INDEX | `db.DateTime, default=lambda: datetime.now(timezone.utc), index=True` | 2026-07-03 14:30:00 UTC | Indexado, con timezone UTC |

### 4.2 Acciones Auditadas (lista COMPLETA)

| Acción | Tabla | Disparador | Código de Referencia |
|--------|-------|-----------|----------------------|
| `REGISTER_USER` | users | Registro de nuevo estudiante desde formulario público | `auth/routes.py:30` |
| `LOGIN` | users | Inicio de sesión exitoso | `auth/routes.py:57` |
| `CREATE_USER` | users | Admin crea usuario (con rol seleccionable) | `users/routes.py:47-51` |
| `CREATE_USER` | users | CLI `seed` command crea usuarios iniciales | `app/cli.py:54-62` |
| `UPDATE_USER` | users | Admin edita usuario (username, email, rol) | `users/routes.py:78-85` |
| `DEACTIVATE_USER` | users | Admin desactiva usuario (soft-delete) | `users/routes.py:111-115` |
| `REQUEST_TUTORIA` | appointments | Estudiante solicita nueva tutoría | `appointments/routes.py:38-46` |
| `CANCEL_TUTORIA` | appointments | Estudiante cancela su tutoría | `appointments/routes.py:99-106` |
| `ACCEPT_TUTORIA` | appointments | Docente acepta tutoría pendiente | `appointments/routes.py:160-167` |
| `COMPLETE_TUTORIA` | appointments | Docente completa tutoría con feedback | `appointments/routes.py:199-206` |

**Detalle adicional sobre cada acción:**

**REGISTER_USER** (`auth/routes.py:30`):
```python
log_audit('REGISTER_USER', 'users', record_id=user.id)
```
- Se registra ANTES del commit (el flush de SQLAlchemy da el ID)
- `user_id` es `None` porque `current_user` no está autenticado (registro público)
- `username` se registra como "anonymous"

**LOGIN** (`auth/routes.py:57`):
```python
log_audit('LOGIN', 'users', record_id=user.id)
```
- Se registra DESPUÉS de `login_user()` exitoso
- Captura la IP real del request
- No se registran intentos fallidos de login (mejora posible)

**CREATE_USER** (`users/routes.py:47-51`):
```python
log_audit(
    'CREATE_USER', 'users',
    record_id=user.id,
    details={'role': form.role.data, 'username': form.username.data},
)
```
- Incluye detalles JSON con el rol asignado y username
- Ejecutado por admin autenticado

**UPDATE_USER** (`users/routes.py:78-85`):
```python
log_audit(
    'UPDATE_USER', 'users',
    record_id=user.id,
    details={'username': user.username, 'role': user.role},
)
```

**DEACTIVATE_USER** (`users/routes.py:111-115`):
```python
log_audit(
    'DEACTIVATE_USER', 'users',
    record_id=user.id,
    details={'username': user.username},
)
```
- Guard contra auto-desactivación: `if user.id == current_user.id: flash(...)`

**REQUEST_TUTORIA** (`appointments/routes.py:38-46`):
```python
log_audit(
    'REQUEST_TUTORIA', 'appointments',
    record_id=appointment.id,
    details={
        'teacher_id': form.teacher.data,
        'subject': form.subject.data,
        'date': str(form.scheduled_date.data),
    },
)
```

**CANCEL_TUTORIA** (`appointments/routes.py:99-106`):
```python
log_audit(
    'CANCEL_TUTORIA', 'appointments',
    record_id=appointment.id,
    details={
        'previous_status': appointment.status,
        'subject': appointment.subject,
    },
)
```
⚠️ **BUG DETECTADO:** En la línea 96 se cambia `appointment.status = 'cancelled'` ANTES de llamar a `log_audit` en la línea 99. Por lo tanto, `appointment.status` en el detalle siempre será `'cancelled'` en lugar del estado anterior real (ej: `'pending'` o `'accepted'`). El detalle `previous_status` es incorrecto. La corrección sería guardar el estado anterior en una variable antes de modificarlo.

**ACCEPT_TUTORIA** (`appointments/routes.py:160-167`):
```python
log_audit(
    'ACCEPT_TUTORIA', 'appointments',
    record_id=appointment.id,
    details={'student_id': appointment.student_id, 'subject': appointment.subject},
)
```

**COMPLETE_TUTORIA** (`appointments/routes.py:199-206`):
```python
log_audit(
    'COMPLETE_TUTORIA', 'appointments',
    record_id=appointment.id,
    details={'student_id': appointment.student_id, 'subject': appointment.subject},
)
```

### 4.3 Validación del Registro de Auditoría (guía para el Analista 3)

**Requisitos previos:**
- Flask app en ejecución (`& '.\venv\Scripts\python' run.py` o `flask run`)
- Base de datos con datos de prueba (ejecutar `flask seed` si está limpia)

**Herramientas:**
- `sqlite3 instance\sgta.db` (CLI)
- O DB Browser for SQLite (GUI)

**Verificar estructura de la tabla:**
```sql
.schema audit_logs
```

**Para cada acción, ejecutar y verificar:**

**1. REGISTER_USER:**
- Acción: Registrar nuevo usuario en `/auth/register`
- Consulta: `SELECT * FROM audit_logs WHERE action='REGISTER_USER';`
- Verificar: `username='anonymous'`, `user_id=NULL`, `ip_address=127.0.0.1` (o IP real)

**2. LOGIN:**
- Acción: Iniciar sesión en `/auth/login`
- Consulta: `SELECT * FROM audit_logs WHERE action='LOGIN';`
- Verificar: `username` coincide con el usuario, `user_id` es el ID del usuario, `ip_address` es la IP real

**3. CREATE_USER (admin):**
- Acción: Admin crea usuario en `/admin/usuarios/crear`
- Consulta: `SELECT * FROM audit_logs WHERE action='CREATE_USER';`
- Verificar: `username` es el admin, `details` contiene JSON con `role` y `username`

**4. UPDATE_USER:**
- Acción: Admin edita usuario en `/admin/usuarios/<id>/editar`
- Consulta: `SELECT * FROM audit_logs WHERE action='UPDATE_USER';`
- Verificar: `details` tiene los nuevos valores

**5. DEACTIVATE_USER:**
- Acción: Admin desactiva usuario via POST a `/admin/usuarios/<id>/baja`
- Consulta: `SELECT * FROM audit_logs WHERE action='DEACTIVATE_USER';`
- Verificar: `record_id` es el ID del usuario desactivado

**6. REQUEST_TUTORIA:**
- Acción: Estudiante solicita tutoría en `/tutorias/solicitar`
- Consulta: `SELECT * FROM audit_logs WHERE action='REQUEST_TUTORIA';`
- Verificar: `details` contiene `teacher_id`, `subject`, `date`

**7. CANCEL_TUTORIA:**
- Acción: Estudiante cancela tutoría via POST a `/tutorias/<id>/cancelar`
- Consulta: `SELECT * FROM audit_logs WHERE action='CANCEL_TUTORIA';`
- Nota: Verificar que `previous_status` diga "cancelled" (por el bug documentado)

**8. ACCEPT_TUTORIA:**
- Acción: Docente acepta tutoría via POST a `/tutorias/<id>/aceptar`
- Consulta: `SELECT * FROM audit_logs WHERE action='ACCEPT_TUTORIA';`

**9. COMPLETE_TUTORIA:**
- Acción: Docente completa tutoría en `/tutorias/<id>/feedback`
- Consulta: `SELECT * FROM audit_logs WHERE action='COMPLETE_TUTORIA';`

**Comando de validación rápida (ver últimas 10 entradas):**
```sql
SELECT id, username, action, table_affected, ip_address, created_at
FROM audit_logs
ORDER BY id DESC
LIMIT 10;
```

**Verificar IP real vs localhost:**
```sql
SELECT DISTINCT ip_address FROM audit_logs;
```

### 4.4 Guía de Evidencias Técnicas (Capturas de Pantalla)

| # | Captura | Herramienta | URL / Acción | Qué debe verse | Qué demuestra |
|---|---------|-------------|-------------|----------------|---------------|
| 1 | **Estructura de la BD** | `sqlite3 instance\sgta.db` + `.schema` o DB Browser | CLI o GUI | Esquema completo de tablas: `users`, `appointments`, `availability`, `audit_logs` con columnas, tipos, PKs y FKs | La BD está correctamente normalizada con relaciones referenciales |
| 2 | **Hash bcrypt en BD** | `sqlite3 instance\sgta.db` | `SELECT username, password_hash FROM users;` | Columna `password_hash` con valores como `$2b$12$...` (60+ caracteres, comienzan con `$2b$12$`) | Las contraseñas se almacenan hasheadas con bcrypt (no texto plano, no SHA/MD5) |
| 3 | **Denegación 403 por rol incorrecto** | Navegador | Estudiante accede a `/admin/usuarios` | Página "403 No tienes permiso" con opciones "Ir al inicio" y "Cerrar sesión" | El RBAC funciona: usuarios sin rol adecuado reciben 403 |
| 4 | **Denegación 403 por ruta de docente** | Navegador | Estudiante accede a `/disponibilidad/` | Página 403 o flash message | Las rutas de docente están protegidas de estudiantes |
| 5 | **Registro de auditoría completo** | Navegador | Admin en `/admin/auditoria` | Tabla con columnas: #, Usuario, Acción (badge), Tabla (code), ID Registro, IP (code), Detalles (botón zoom), Fecha/Hora | El sistema audita todas las acciones sensibles con IP y timestamp |
| 6 | **Auditoría con IP real** | Navegador + DevTools o `sqlite3` | Columna `ip_address` | Direcciones IP reales visibles (ej: `127.0.0.1` en local, `192.168.x.x` en red local) | La IP del cliente se captura y almacena para forense |
| 7 | **Talisman security headers** | DevTools (F12) → Red → clic en request → Headers | Cualquier página de SGTA | Headers: `content-security-policy`, `x-frame-options: DENY`, `x-content-type-options: nosniff` | Flask-Talisman aplica headers de seguridad a todas las respuestas |
| 8 | **CSRF token en formularios** | DevTools (F12) → Elementos | `/auth/login`, `/tutorias/solicitar`, etc. | Input oculto: `<input id="csrf_token" name="csrf_token" type="hidden" value="...">` como primer campo del formulario | WTForms genera token CSRF único por formulario |
| 9 | **Login exitoso + redirect según rol** | Navegador | Login como estudiante → dashboard; login como admin → dashboard con navbar completa | Navbar muestra opciones según el rol del usuario logueado | La redirección post-login y el menú son role-aware |
| 10 | **Validación de formulario** | Navegador | Registrar con email inválido o fecha pasada en `/tutorias/solicitar` | Mensajes de error: "Ingresa un correo electrónico válido" o "La fecha debe ser posterior a hoy" junto al campo en rojo | Las validaciones de backend funcionan correctamente |
| 11 | **Error CSRF expirado** | Navegador | Esperar >1h con formulario abierto y enviar, o manipular token | Página de error 400 (Bad Request) con mensaje "The CSRF token has expired" | Los tokens CSRF expiran después de 3600 segundos |
| 12 | **Login con IP en auditoría** | Navegador login + `sqlite3` | Login exitoso y luego `SELECT * FROM audit_logs WHERE action='LOGIN'` | Fila con acción LOGIN, username correcto, IP del cliente | Cada login queda registrado con IP |

### 4.5 Preparación de la Defensa

Puntos clave a resaltar en la defensa del documento:

**1. Enfoque "Defense in Depth" (capas múltiples de seguridad)**

SGTA implementa seguridad en capas, no depende de una sola medida:
- **Capa 1 (Red):** Talisman headers + HTTPS (producción)
- **Capa 2 (Aplicación):** RBAC con decoradores, validación WTForms, guards de ownership
- **Capa 3 (Datos):** ORM parametrizado, bcrypt hashing, CSRF tokens
- **Capa 4 (Renderizado):** Jinja2 autoescapado, CSP restrictivo
- **Capa 5 (Auditoría):** AuditLog completo para forense post-incidente

Si una capa falla, las siguientes siguen protegiendo.

**2. Justificación de bcrypt sobre SHA256/MD5**

| Algoritmo | Tiempo por hash | Resistencia a GPU | Salt automático | Adecuado para passwords |
|-----------|-----------------|-------------------|-----------------|------------------------|
| MD5 | ~1μs | Muy baja (paralelizable masivamente) | No | No |
| SHA256 | ~1μs | Baja (ASICs dedicados) | No | No |
| bcrypt (cost 12) | ~250ms | Alta (diseñado para ser lento en GPU) | Sí, 128 bits | **Sí** |
| Argon2id | ~300ms | Muy alta (resistente a GPU/ASIC) | Sí | Sí (alternativa moderna) |

bcrypt es el estándar de la industria para almacenamiento de contraseñas. Aunque Argon2id es más moderno, bcrypt con cost 12 es ampliamente aceptado y suficiente para los niveles de amenaza de este sistema.

**3. Por qué decoradores RBAC y no if-else en cada ruta**

Beneficios de usar decoradores vs. if-else inline:
- **Separación de concerns:** La lógica de autorización está en un solo lugar (`decorators.py`)
- **Reutilización:** Un decorador se aplica con una línea en cualquier ruta
- **Consistencia:** Todos los chequeos de rol pasan por la misma función, no hay riesgo de lógica inconsistente
- **Testeabilidad:** El decorador se prueba una vez, no en cada ruta
- **Legibilidad:** `@roles_required('administrador')` expresa la intención claramente

**4. CSP como defensa contra XSS incluso si hay un bug en el código**

La política CSP (`default-src 'self'`) significa que incluso si un template renderiza contenido sin escapar (olvido del desarrollador), el navegador bloqueará cualquier script que no venga de `'self'` o del CDN de Bootstrap. Esto es particularmente importante porque:
- Protege contra XSS almacenado (datos maliciosos en BD que se renderizan)
- Protege contra XSS reflejado (parámetros URL maliciosos)
- No requiere cambios en el código existente

**5. Auditoría como requisito de compliance y forense**

- **Cumplimiento normativo:** La auditoría es requerida por estándares como ISO 27001, SOC 2, y regulaciones de protección de datos
- **Detección de incidentes:** Permite identificar accesos no autorizados, patrones anómalos, o intentos de ataque
- **No-repudio:** Los registros con IP, timestamp, y user_id proporcionan evidencia forense
- **Mejora continua:** El análisis de logs permite identificar brechas de seguridad y mejorar las defensas

**6. Diferencias entre desarrollo y producción**

| Aspecto | Desarrollo | Producción |
|---------|-----------|------------|
| Servidor | Flask dev server (`run.py`) | Gunicorn + Nginx |
| HTTPS | No (HTTP plano) | Sí (TLS 1.3 con Let's Encrypt) |
| Debug | `app.run(debug=True)` | `debug=False` |
| SECRET_KEY | `'dev-secret-change-in-prod'` | Variable de entorno segura |
| Session Cookie Secure | `False` | `True` |
| Force HTTPS | `False` | `True` |
| BD | SQLite (`instance/sgta.db`) | SQLite o PostgreSQL (recomendado) |

---

## 5. ANEXOS

### A. Stack Tecnológico con Versiones Exactas

**Entorno de ejecución:**
- Python 3.14.4 (64-bit)
- Sistema operativo: Windows (desarrollo)

**Paquetes del proyecto verificados:**

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| Flask | 3.1.3 | Framework web WSGI |
| Flask-SQLAlchemy | 3.1.1 | ORM para base de datos SQL |
| SQLAlchemy | 2.0.51 | Motor ORM subyacente |
| Flask-Bcrypt | 1.0.1 | Hashing de contraseñas con bcrypt |
| bcrypt | 5.0.0 | Implementación de bcrypt |
| Flask-Login | 0.6.3 | Gestión de sesiones de usuario |
| Flask-Talisman | 1.1.0 | Headers de seguridad HTTP (CSP, HSTS, XFO) |
| Flask-WTF | 1.3.0 | Integración WTForms con Flask |
| WTForms | 3.2.2 | Validación y renderizado de formularios |
| Werkzeug | 3.1.8 | Utilidades WSGI (subyacente a Flask) |
| Jinja2 | 3.1.6 | Motor de templates |
| MarkupSafe | 3.0.3 | Escape seguro de HTML (usado por Jinja2) |
| email-validator | 2.3.0 | Validación de direcciones de email |
| click | 8.4.2 | CLI (comandos flask seed, etc.) |

### B. Comandos Útiles

**Exploración de la base de datos:**

```bash
# Conectar a la BD SQLite
sqlite3 instance\sgta.db

# Esquema completo
.schema

# Tabla específica
.schema users
.schema audit_logs

# Todos los usuarios
SELECT id, username, email, role, is_active FROM users;

# Hashes de contraseñas (confirmar bcrypt)
SELECT username, substr(password_hash, 1, 30) AS hash_preview FROM users;

# Últimas acciones de auditoría
SELECT id, username, action, table_affected, ip_address, created_at
FROM audit_logs ORDER BY id DESC LIMIT 20;

# Auditoría filtrada por acción
SELECT * FROM audit_logs WHERE action='LOGIN';

# IPs únicas que han accedido al sistema
SELECT DISTINCT ip_address FROM audit_logs;

# Conteo de acciones
SELECT action, COUNT(*) as total FROM audit_logs GROUP BY action ORDER BY total DESC;
```

**Ejecutar aplicación en desarrollo:**
```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Ejecutar servidor de desarrollo
python run.py

# O alternativamente:
flask run

# Seed de datos iniciales
flask seed
```

**Verificación de seguridad en producción (recomendado):**
```bash
# Verificar headers de seguridad
curl -I https://sgta.dominio.com

# Verificar CSP
curl -s -D- https://sgta.dominio.com | findstr "content-security-policy"

# Verificar que no hay SQL crudo en el código
Get-ChildItem -Recurse -Filter "*.py" | Select-String "execute\(|text\("
```

**Herramientas de prueba de seguridad recomendadas:**
- **OWASP ZAP** — Escáner de seguridad automatizado
- **sqlmap** — Prueba de inyección SQL (aunque ORM debería prevenirlo)
- **SSL Labs** — Prueba de configuración TLS
- **Burp Suite** — Proxy de interceptación para pruebas manuales

---

*Documento generado el Julio 2026 basado en el análisis del código fuente de SGTA v1.0.*
