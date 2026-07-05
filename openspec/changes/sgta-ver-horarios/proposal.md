# Propuesta: SGTA — Ver Horarios Disponibles para Estudiantes

**Change:** `sgta-ver-horarios`
**Status:** Draft

---

## Intención

Los estudiantes solicitan tutorías sin conocer la disponibilidad real de los docentes,
generando solicitudes que son rechazadas manualmente. Se necesita que el estudiante
pueda consultar horarios disponibles y que el formulario de solicitud filtre y valide
contra esos horarios.

## Alcance

### Incluye
- **Fase 1 — Visualización:** listado de docentes con slots activos, tabla semanal
  por docente, link en navbar de estudiante
- **Fase 2 — Integración:** filtro de docentes en `AppointmentForm`, validación
  server-side de fecha/hora contra `Availability`

### Excluye
- CRUD de disponibilidad para estudiantes (solo lectura)
- Calendario visual/interactivo (JavaScript)
- Notificaciones cuando un docente agrega slots
- Validación de solapamiento entre docentes

## Capacidades

### Nuevas
- `disponibilidad-visualizacion`: consulta read-only de horarios disponibles para
  estudiantes, con listado de docentes y tabla semanal por docente

### Modificadas
- `appointments`: `AppointmentForm` filtra docentes con disponibilidad activa;
  `request_tutoria()` valida fecha/hora contra `Availability`

## Enfoque

2 rutas GET nuevas en `availability/routes.py` con `@roles_required('estudiante')`,
2 templates Bootstrap 5, filtro en `AppointmentForm.__init__` con subquery a
`Availability`, validación server-side por `day_of_week` + rango horario, y
recepción de `teacher_id` pre-seleccionado desde query string.

## Áreas Afectadas

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `app/availability/routes.py` | +2 rutas | `list_teachers`, `teacher_slots` |
| `app/templates/availability/teacher_list.html` | Crear | Tarjetas de docentes con disponibilidad |
| `app/templates/availability/teacher_slots.html` | Crear | Tabla semanal Lun-Dom con horarios |
| `app/templates/base.html` | Modificar | +1 link "Horarios Disponibles" en navbar estudiante |
| `app/appointments/forms.py` | Modificar | Filtrar docentes con disponibilidad activa |
| `app/appointments/routes.py` | Modificar | Validar fecha/hora vs availability + recibir teacher_id |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Docente sin slots → lista/docente vacío | Baja | Mensaje claro "Sin horarios registrados" |
| Timezone implícito en datos existentes | Media | Usar misma zona horaria server-side sin cambio de schema |
| Slot eliminado entre GET y POST | Baja | Validar en POST + flash error + re-cargar form |

## Plan de Retroceso

Eliminar las 2 rutas nuevas en `availability/routes.py`, borrar los 2 templates
creados, revertir `base.html`, restaurar `AppointmentForm` y `request_tutoria()`
a su versión anterior. Sin migraciones de BD involucradas.

## Dependencias

- Modelo `Availability` ya existe (creado en `sgta-core-inicial`)
- `DAY_CHOICES` en `availability/forms.py` reutilizable para template
- Blueprint `availability` ya registrado en la app

## Criterios de Éxito

- [ ] Estudiante navega a `/disponibilidad/docentes` y ve lista de docentes con slots
- [ ] Estudiante clickea un docente y ve tabla semanal con horarios disponibles
- [ ] "Solicitar Tutoría" en tabla lleva al form con docente pre-seleccionado
- [ ] Select de docentes en el form solo muestra aquellos con >= 1 slot activo
- [ ] Solicitud con fecha/hora fuera de un slot activo es rechazada con flash error
- [ ] Navbar de estudiante muestra "Horarios Disponibles"
