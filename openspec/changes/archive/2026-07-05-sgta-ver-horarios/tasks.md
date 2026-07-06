# SGTA — Ver Horarios Disponibles para Estudiantes

**Change:** `sgta-ver-horarios`
**Status:** Draft

---

## Resumen de Tareas

| ID | Nombre | Archivos | Esfuerzo | Dependencias |
|----|--------|----------|----------|-------------|
| [x] T01 | Rutas de disponibilidad pública | `availability/routes.py` | 30 min | — |
| [x] T02 | Template teacher_list.html | `templates/availability/teacher_list.html` | 20 min | T01 |
| [x] T03 | Template teacher_slots.html | `templates/availability/teacher_slots.html` | 25 min | T01 |
| [x] T04 | Navbar de estudiante | `templates/base.html` | 5 min | T01 |
| [x] T05 | Filtro de docentes en AppointmentForm | `appointments/forms.py` | 15 min | — |
| [x] T06 | Pre-selección y validación server-side | `appointments/routes.py` | 30 min | T05 |

**Total estimado:** ~125 líneas, ~2 horas

---

## Tareas Detalladas

### T01: Rutas de disponibilidad pública

**Objetivo:** Agregar 2 rutas GET en `availability/routes.py` para que estudiantes
(y docentes) puedan consultar horarios disponibles.

**Archivo:** `app/availability/routes.py`

**Cambios:**
```python
# Al inicio del archivo, agregar constante
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

**Criterio de aceptación:** GET a `/disponibilidad/docentes` devuelve 200 para
estudiante autenticado. GET a `/disponibilidad/docente/1` devuelve 200 si el
docente existe.

---

### T02: Template teacher_list.html

**Objetivo:** Template que muestra tarjetas de docentes con disponibilidad.

**Archivo:** `app/templates/availability/teacher_list.html` (CREAR)

**Contenido:**
- Extiende `base.html`
- Título "Horarios Disponibles"
- Grid de tarjetas (col-md-4) con: nombre, email, botón "Ver Horarios"
- Mensaje "No hay horarios disponibles en este momento" si `teachers` está vacío
- Enlace alternativo "Solicitar Tutoría Directamente" cuando no hay horarios
- Iconos Bootstrap (bi-calendar-week, bi-person-video3, bi-envelope, bi-eye)

**Criterio de aceptación:** El template se renderiza correctamente con y sin datos.
Coincide con el diseño en `design.md`.

---

### T03: Template teacher_slots.html

**Objetivo:** Template que muestra la tabla semanal de slots de un docente.

**Archivo:** `app/templates/availability/teacher_slots.html` (CREAR)

**Contenido:**
- Extiende `base.html`
- Breadcrumb: Horarios Disponibles > nombre del docente
- Título "Horarios de {docente}"
- Tabla responsiva con columnas: Día, Horario, Acción
- `day_map[slot.day_of_week]` para mostrar nombre del día
- Formato HH:MM con `strftime('%H:%M')`
- Botón "Solicitar Tutoría" que enlaza a `appointments.request_tutoria` con `teacher_id`
- Mensaje "Este docente no tiene horarios disponibles registrados" si no hay slots
- Botón "Volver a lista de docentes"
- Iconos Bootstrap

**Criterio de aceptación:** El template se renderiza correctamente. Los enlaces
incluyen `?teacher_id=` correcto.

---

### T04: Navbar de estudiante

**Objetivo:** Agregar link "Horarios Disponibles" en el navbar del estudiante.

**Archivo:** `app/templates/base.html`

**Cambio:** Dentro del bloque `{% if current_user.role == 'estudiante' %}`, después
del link "Mis Tutorías":

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('availability.list_teachers') }}">
        <i class="bi bi-calendar-week me-1"></i>Horarios Disponibles
    </a>
</li>
```

**Criterio de aceptación:** Estudiante autenticado ve el link en el navbar.
Docente y admin no lo ven.

---

### T05: Filtro de docentes en AppointmentForm

**Objetivo:** El selector de docente en el formulario de solicitud solo muestra
docentes con al menos un slot activo.

**Archivo:** `app/appointments/forms.py`

**Cambio:** Modificar el `__init__` de `AppointmentForm`:

```python
class AppointmentForm(FlaskForm):
    teacher = SelectField('Docente', coerce=int, validators=[DataRequired()])
    subject = StringField('Materia', validators=[DataRequired(), Length(3, 200)])
    description = TextAreaField('Descripción', validators=[Length(max=2000)])
    scheduled_date = DateField('Fecha', validators=[DataRequired()])
    scheduled_time = TimeField('Hora', validators=[DataRequired()])

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

**Criterio de aceptación:** El select de docente en `/tutorias/solicitar` solo
contiene docentes con slots activos. No aparecen docentes sin disponibilidad.

---

### T06: Pre-selección de docente y validación server-side

**Objetivo:** 
1. Si viene `teacher_id` por query string, preseleccionar ese docente
2. Al enviar, validar que la fecha/hora esté dentro de un slot activo

**Archivo:** `app/appointments/routes.py`

**Cambio 1 — Pre-selección en GET:**
```python
# Dentro de request_tutoria(), antes de if form.validate_on_submit():
teacher_id = request.args.get('teacher_id', type=int)
if teacher_id and request.method == 'GET':
    teacher = User.query.get(teacher_id)
    if teacher and teacher.role == 'docente':
        form.teacher.data = teacher_id
```

**Cambio 2 — Validación en POST:**
```python
# Dentro de if form.validate_on_submit(), ANTES de crear el Appointment:
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
```

**Criterio de aceptación:**
- GET a `/tutorias/solicitar?teacher_id=1` preselecciona al docente 1
- POST con fecha/hora válida dentro de un slot → crea la tutoría
- POST con fecha/hora fuera de cualquier slot → flash error + re-renderiza form

---

## Orden de Implementación

```
T01 (rutas)
  ├── T02 (template listado)
  ├── T03 (template slots)
  └── T04 (navbar)
T05 (filtro form)
  └── T06 (validación + pre-selección)
```

**Batch único:** T01-T06 pueden implementarse en un solo batch porque:
- Sin migraciones de BD
- ~125 líneas totales estimadas
- Sin cambios complejos en lógica existente
- Templates Bootstrap simples

---

## Review Workload Forecast

| Métrica | Valor |
|---------|-------|
| Líneas nuevas estimadas | ~125 |
| Archivos nuevos | 2 (templates) |
| Archivos modificados | 4 (routes.py×2, forms.py, base.html) |
| 400-line budget risk | **Bajo** (~125 líneas) |
| Chained PRs recommended | **No** — batch único |
| Decision needed before apply | **No** |

---

## Plan de Retroceso

Por tarea individual:

| Tarea | Rollback |
|-------|----------|
| T01 | Eliminar las 2 rutas nuevas de `availability/routes.py` |
| T02 | Eliminar `teacher_list.html` |
| T03 | Eliminar `teacher_slots.html` |
| T04 | Revertir cambio en `base.html` |
| T05 | Revertir `AppointmentForm.__init__` a la query original |
| T06 | Revertir cambios en `request_tutoria()` |

Sin migraciones de BD involucradas, rollback es siempre seguro.
