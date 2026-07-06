# SGTA — Ver Horarios Disponibles para Estudiantes

**Change:** `sgta-ver-horarios`
**Status:** Draft

---

## 1. Arquitectura

Se extiende el blueprint `availability/` existente con 2 rutas GET de solo lectura
accesibles para estudiantes y docentes. No se crean nuevos blueprints ni modelos de
datos. El módulo `appointments/` se modifica para integrar la validación contra
disponibilidad.

```
┌─────────────────────────────────────────────────────────────┐
│                      Flask Application                       │
│                                                              │
│  ┌──────────────┐   ┌──────────────────┐   ┌──────────────┐│
│  │  auth/       │   │  availability/   │   │ appointments/ ││
│  │  (sin cambio)│   │                  │   │              ││
│  │              │   │  + list_teachers │   │  + filtro    ││
│  │              │   │  + teacher_slots │   │    docentes  ││
│  │              │   │                  │   │  + validación││
│  └──────────────┘   └──────────────────┘   └──────────────┘│
│                              ↕                               │
│                      SQLite (sgta.db)                        │
│              ┌──────────────────────────────┐                │
│              │  Availability | User         │                │
│              │  (solo lectura)              │                │
│              └──────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Componentes

| Componente | Tipo | Archivo | Descripción |
|-----------|------|---------|-------------|
| `list_teachers()` | Ruta GET | `availability/routes.py` | Lista docentes con ≥1 slot activo |
| `teacher_slots(id)` | Ruta GET | `availability/routes.py` | Tabla semanal de slots por docente |
| `teacher_list.html` | Template | `templates/availability/` | Tarjetas de docentes con disponibilidad |
| `teacher_slots.html` | Template | `templates/availability/` | Tabla semanal con horarios |
| `AppointmentForm.__init__` | Modif. | `appointments/forms.py` | Filtro docentes con disponibilidad |
| `request_tutoria()` | Modif. | `appointments/routes.py` | Validación + pre-selección docente |
| Navbar estudiante | Modif. | `templates/base.html` | Link "Horarios Disponibles" |

---

## 3. Flujos de Datos Detallados

### 3.1 Flujo: Ver horarios disponibles

```
Estudiante                     Servidor                      BD
    │                             │                          │
    ├── GET /disponibilidad/docentes                          │
    │                             │                          │
    │                             ├── list_teachers()        │
    │                             │   User.query             │
    │                             │   .join(Availability)    │
    │                             │   .filter(is_available)  │
    │                             │   .distinct()            │
    │                             │─────────────────────────►│
    │                             │◄─────────────────────────│
    │                             │                          │
    │◄── teacher_list.html ───────┤                          │
    │                             │                          │
    ├── GET /disponibilidad/docente/1                        │
    │                             │                          │
    │                             ├── teacher_slots(1)       │
    │                             │   Availability.query     │
    │                             │   .filter(teacher_id=1)  │
    │                             │   .order_by(day, time)   │
    │                             │─────────────────────────►│
    │                             │◄─────────────────────────│
    │                             │                          │
    │◄── teacher_slots.html ──────┤                          │
    │                             │                          │
    ├── Click "Solicitar Tutoría" │                          │
    │    teacher_id=1 pre-cargado │                          │
```

### 3.2 Flujo: Solicitar tutoría con validación

```
Estudiante                     Servidor                      BD
    │                             │                          │
    │── GET /tutorias/solicitar?teacher_id=1                 │
    │                             │                          │
    │                             ├── request_tutoria(GET)   │
    │                             │   teacher_id→template    │
    │                             │                          │
    │◄── request.html ────────────┤                          │
    │   (docente pre-seleccionado)│                          │
    │                             │                          │
    │── POST /tutorias/solicitar  │                          │
    │   teacher=1                 │                          │
    │   scheduled_date=2026-07-13 │                          │
    │   scheduled_time=10:30      │                          │
    │                             │                          │
    │                             ├── request_tutoria(POST)  │
    │                             │   1. Validar WTForms     │
    │                             │   2. Calcular day_of_week│
    │                             │      (2026-07-13 = Lunes = 0)
    │                             │                          │
    │                             ├── Buscar Availability    │
    │                             │   teacher_id=1           │
    │                             │   day_of_week=0          │
    │                             │   is_available=True      │
    │                             │   start_time≤10:30       │
    │                             │   end_time>10:30         │
    │                             │─────────────────────────►│
    │                             │◄── slot encontrado ──────│
    │                             │                          │
    │                             ├── Crear Appointment      │
    │                             │   status='pending'       │
    │                             ├── log_audit()            │
    │                             ├── db.session.commit()    │
    │                             │                          │
    │◄── Flash success ───────────┤                          │
    │   redirect→ /mis-tutorias   │                          │
```

### 3.3 Flujo: Validación fallida

```
Estudiante                     Servidor                      BD
    │                             │                          │
    │── POST /tutorias/solicitar  │                          │
    │   teacher=1                 │                          │
    │   scheduled_date=2026-07-14 │                          │
    │   scheduled_time=14:00      │                          │
    │                             │                          │
    │                             ├── Validar WTForms (OK)   │
    │                             ├── day_of_week=1 (Martes) │
    │                             │                          │
    │                             ├── Buscar Availability    │
    │                             │   teacher_id=1           │
    │                             │   day_of_week=1          │
    │                             │─────────────────────────►│
    │                             │◄── sin resultados ───────│
    │                             │                          │
    │◄── Flash warning ───────────┤                          │
    │   "El docente seleccionado  │                          │
    │   no tiene disponibilidad   │                          │
    │   en esa fecha y hora"      │                          │
    │   + form con datos previos  │                          │
```

---

## 4. Estructura de Templates

### teacher_list.html

```html
{% extends "base.html" %}
{% block title %}Horarios Disponibles{% endblock %}
{% block content %}
<div class="container mt-4">
  <h1 class="mb-4"><i class="bi bi-calendar-week me-2"></i>Horarios Disponibles</h1>

  {% if teachers %}
    <div class="row">
      {% for teacher in teachers %}
        <div class="col-md-4 mb-3">
          <div class="card h-100 shadow-sm">
            <div class="card-body">
              <h5 class="card-title">
                <i class="bi bi-person-video3 me-1"></i>{{ teacher.username }}
              </h5>
              <p class="card-text text-muted">
                <i class="bi bi-envelope me-1"></i>{{ teacher.email }}
              </p>
              <a href="{{ url_for('availability.teacher_slots', teacher_id=teacher.id) }}"
                 class="btn btn-primary">
                <i class="bi bi-eye me-1"></i>Ver Horarios
              </a>
            </div>
          </div>
        </div>
      {% endfor %}
    </div>
  {% else %}
    <div class="alert alert-info">
      <i class="bi bi-info-circle me-2"></i>
      No hay horarios disponibles en este momento.
    </div>
    <a href="{{ url_for('appointments.request_tutoria') }}" class="btn btn-outline-primary">
      Solicitar Tutoría Directamente
    </a>
  {% endif %}
</div>
{% endblock %}
```

### teacher_slots.html

```html
{% extends "base.html" %}
{% block title %}Horarios de {{ teacher.username }}{% endblock %}
{% block content %}
<div class="container mt-4">
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb">
      <li class="breadcrumb-item">
        <a href="{{ url_for('availability.list_teachers') }}">Horarios Disponibles</a>
      </li>
      <li class="breadcrumb-item active">{{ teacher.username }}</li>
    </ol>
  </nav>

  <h1 class="mb-4">
    <i class="bi bi-person-video3 me-2"></i>Horarios de {{ teacher.username }}
  </h1>

  {% if slots %}
    <div class="table-responsive">
      <table class="table table-striped table-hover">
        <thead class="table-dark">
          <tr>
            <th>Día</th>
            <th>Horario</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          {% for slot in slots %}
          <tr>
            <td><strong>{{ day_map[slot.day_of_week] }}</strong></td>
            <td>{{ slot.start_time.strftime('%H:%M') }} — {{ slot.end_time.strftime('%H:%M') }}</td>
            <td>
              <a href="{{ url_for('appointments.request_tutoria', teacher_id=teacher.id) }}"
                 class="btn btn-sm btn-success">
                <i class="bi bi-plus-circle me-1"></i>Solicitar Tutoría
              </a>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  {% else %}
    <div class="alert alert-warning">
      <i class="bi bi-exclamation-triangle me-2"></i>
      Este docente no tiene horarios disponibles registrados.
    </div>
  {% endif %}

  <a href="{{ url_for('availability.list_teachers') }}" class="btn btn-outline-secondary">
    <i class="bi bi-arrow-left me-1"></i>Volver a lista de docentes
  </a>
</div>
{% endblock %}
```

---

## 5. Modificaciones a Componentes Existentes

### 5.1 `app/availability/routes.py` — 2 rutas nuevas

```python
DIA_MAP = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
           4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}


@availability_bp.route('/docentes')
@login_required
@roles_required('estudiante', 'docente')
def list_teachers():
    """Lista docentes con al menos un slot de disponibilidad activo."""
    teachers = (
        User.query
        .filter_by(role='docente', is_active=True)
        .join(Availability)
        .filter(Availability.is_available == True)
        .distinct()
        .order_by(User.username)
        .all()
    )
    return render_template('availability/teacher_list.html', teachers=teachers)


@availability_bp.route('/docente/<int:teacher_id>')
@login_required
@roles_required('estudiante', 'docente')
def teacher_slots(teacher_id):
    """Muestra la tabla semanal de slots de un docente específico."""
    teacher = User.query.get_or_404(teacher_id)
    slots = (
        Availability.query
        .filter_by(teacher_id=teacher_id, is_available=True)
        .order_by(Availability.day_of_week, Availability.start_time)
        .all()
    )
    return render_template(
        'availability/teacher_slots.html',
        teacher=teacher,
        slots=slots,
        day_map=DIA_MAP,
    )
```

### 5.2 `app/templates/base.html` — Navbar de estudiante

Agregar después del link "Mis Tutorías" (dentro del bloque `if current_user.role == 'estudiante'`):

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('availability.list_teachers') }}">
        <i class="bi bi-calendar-week me-1"></i>Horarios Disponibles
    </a>
</li>
```

### 5.3 `app/appointments/forms.py` — Filtro en AppointmentForm

Modificar el `__init__` de `AppointmentForm` para que el campo `teacher` solo cargue
docentes con al menos un slot activo:

```python
class AppointmentForm(FlaskForm):
    teacher = SelectField('Docente', coerce=int, validators=[DataRequired()])
    # ... otros campos ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher.choices = [
            (t.id, t.username)
            for t in User.query
            .filter_by(role='docente', is_active=True)
            .join(Availability)
            .filter(Availability.is_available == True)
            .distinct()
            .order_by(User.username)
            .all()
        ]
```

### 5.4 `app/appointments/routes.py` — Validación + pre-selección

**En el GET**: leer `teacher_id` del query string para preseleccionar:

```python
@appointments_bp.route('/solicitar', methods=['GET', 'POST'])
@login_required
@roles_required('estudiante')
def request_tutoria():
    form = AppointmentForm()

    # Pre-seleccionar docente si viene por query string
    teacher_id = request.args.get('teacher_id', type=int)
    if teacher_id and request.method == 'GET':
        teacher = User.query.get(teacher_id)
        if teacher and teacher.role == 'docente':
            form.teacher.data = teacher_id

    if form.validate_on_submit():
        # Validar disponibilidad del docente
        day_of_week = form.scheduled_date.data.weekday()
        slot = Availability.query.filter(
            Availability.teacher_id == form.teacher.data,
            Availability.day_of_week == day_of_week,
            Availability.is_available == True,
            Availability.start_time <= form.scheduled_time.data,
            Availability.end_time > form.scheduled_time.data,
        ).first()

        if not slot:
            flash(
                'El docente seleccionado no tiene disponibilidad '
                'en esa fecha y hora.',
                'warning',
            )
            return render_template('appointments/request.html', form=form)

        # ... resto del flujo existente (crear Appointment, log_audit, etc.) ...
```

---

## 6. Decisiones de Diseño

| Decisión | Opción elegida | Alternativa | Motivo |
|----------|---------------|-------------|--------|
| Ubicación rutas | `availability/routes.py` | `appointments/routes.py` | Cohesión semántica: el recurso es disponibilidad |
| Mapa de días | Constante `DIA_MAP` en routes.py | Reusar `DAY_CHOICES` de forms.py | `DAY_CHOICES` usa tuplas (value, label); templates necesitan dict {id: label} |
| Protección roles | `@roles_required('estudiante', 'docente')` | Solo estudiante | Docente también puede consultar disponibilidad de colegas |
| Validación server-side | Query SQLAlchemy con filtros | Validación en Python | Aprovecha índice de BD, más eficiente |
| Pre-selección docente | `request.args.get('teacher_id')` en GET | Session o POST redirect | Simple, sin estado compartido, funcional sin JS |

---

## 7. Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Slot eliminado entre GET y POST | Baja | Medio | Validación server-side en POST + flash error |
| Docente sin slots | Baja | Bajo | Query con JOIN filtra automáticamente |
| Timezone implícito | Media | Bajo | Misma zona horaria server-side; sin cambio de schema |
| `day_of_week` vs fecha concreta | Baja | Bajo | La validación convierte `scheduled_date` a `day_of_week` para matchear slots semanales |

---

## 8. Dependencias

- **Modelo `Availability`**: ya existe en `app/models.py`
- **Constante `DAY_CHOICES`**: existe en `availability/forms.py` (no se reusa directamente)
- **Blueprint `availability`**: ya registrado en `app/__init__.py` con `url_prefix='/disponibilidad'`
- **Blueprint `appointments`**: ya registrado con `url_prefix='/tutorias'`
- **`AppointmentForm`**: ya existe en `appointments/forms.py`
- **`request_tutoria()`**: ya existe en `appointments/routes.py`

Sin nuevas dependencias de paquetes Python. Sin migraciones de base de datos.
