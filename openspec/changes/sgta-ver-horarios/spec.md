# SGTA — Ver Horarios Disponibles para Estudiantes

**Change:** `sgta-ver-horarios`
**Status:** Draft

---

## Resumen

Los estudiantes solicitan tutorías sin conocer la disponibilidad real de los docentes,
generando solicitudes que son rechazadas manualmente. Este cambio agrega consulta de
horarios disponibles para estudiantes (Fase 1) e integra la validación contra
disponibilidad en el formulario de solicitud de tutoría (Fase 2).

---

## Requisitos Funcionales

### RF-001: Listado de docentes con disponibilidad

**Descripción:** El estudiante puede ver un listado de docentes que tienen al menos
un slot de disponibilidad activo registrado.

**Escenario:**
```gherkin
Given el estudiante ha iniciado sesión
When accede a /disponibilidad/docentes
Then ve una lista de docentes con al menos un slot de disponibilidad activo
And cada docente muestra su nombre de usuario y email
And cada docente tiene un botón "Ver Horarios"
```

**Escenario (sin disponibilidad):**
```gherkin
Given el estudiante ha iniciado sesión
And ningún docente tiene slots de disponibilidad activos
When accede a /disponibilidad/docentes
Then ve el mensaje "No hay horarios disponibles en este momento"
```

---

### RF-002: Tabla semanal de slots por docente

**Descripción:** El estudiante puede ver los slots de disponibilidad de un docente
específico organizados por día de la semana.

**Escenario:**
```gherkin
Given el estudiante ha iniciado sesión
And existe un docente con slots de lunes 10:00-12:00 y miércoles 14:00-16:00
When accede a /disponibilidad/docente/{id_docente}
Then ve una tabla ordenada por día de la semana
And la fila de Lunes muestra "10:00 - 12:00"
And la fila de Miércoles muestra "14:00 - 16:00"
And cada slot tiene un botón "Solicitar Tutoría"
```

**Escenario (docente inexistente):**
```gherkin
Given el estudiante ha iniciado sesión
When accede a /disponibilidad/docente/9999
Then recibe un error 404
```

---

### RF-003: Navegación desde navbar

**Descripción:** El navbar del estudiante incluye un enlace directo a la vista de
horarios disponibles.

**Escenario:**
```gherkin
Given el estudiante ha iniciado sesión
When ve el navbar
Then existe un enlace con texto "Horarios Disponibles"
And el enlace apunta a /disponibilidad/docentes
```

**Escenario (otro rol):**
```gherkin
Given el docente ha iniciado sesión
When ve el navbar
Then NO existe el enlace "Horarios Disponibles" (el docente usa su propia gestión)
```

---

### RF-004: Pre-selección de docente desde disponibilidad

**Descripción:** Al hacer clic en "Solicitar Tutoría" desde la tabla de slots, el
formulario de solicitud se carga con ese docente ya seleccionado.

**Escenario:**
```gherkin
Given el estudiante está viendo los slots del docente "profesor1"
When hace clic en "Solicitar Tutoría" en un slot
Then es redirigido a /tutorias/solicitar?teacher_id={id_profesor1}
And el selector de docente en el formulario muestra "profesor1" preseleccionado
```

---

### RF-005: Filtro de docentes en formulario de solicitud

**Descripción:** El selector de docentes en el formulario de solicitud de tutoría solo
muestra docentes que tienen al menos un slot de disponibilidad activo.

**Escenario:**
```gherkin
Given existe un docente "activo" con slots disponibles
And existe un docente "inactivo" sin slots
When el estudiante accede a /tutorias/solicitar
Then el selector de docente contiene a "activo"
And el selector de docente NO contiene a "inactivo"
```

---

### RF-006: Validación de fecha/hora contra disponibilidad

**Descripción:** Al enviar una solicitud de tutoría, el servidor valida que la fecha
y hora seleccionadas caigan dentro de un slot de disponibilidad activo del docente.

**Escenario (válido):**
```gherkin
Given el docente tiene un slot Lunes 10:00-12:00
When el estudiante solicita una tutoría para el próximo Lunes a las 10:30
Then la solicitud se crea correctamente con status "pending"
```

**Escenario (hora fuera del slot):**
```gherkin
Given el docente tiene un slot Lunes 10:00-12:00
When el estudiante solicita una tutoría para el próximo Lunes a las 14:00
Then la solicitud es rechazada
And ve el mensaje "El docente seleccionado no tiene disponibilidad en esa fecha y hora"
```

**Escenario (día sin disponibilidad):**
```gherkin
Given el docente tiene un slot Lunes 10:00-12:00
When el estudiante solicita una tutoría para el próximo Martes a las 10:30
Then la solicitud es rechazada
And ve el mensaje "El docente seleccionado no tiene disponibilidad en esa fecha y hora"
```

**Escenario (slot eliminado entre GET y POST):**
```gherkin
Given el estudiante ve los slots del docente
When el docente elimina todos sus slots
And el estudiante envía el formulario con datos que ya no son válidos
Then la solicitud es rechazada
And ve un mensaje de error indicando que el docente ya no tiene disponibilidad
```

---

### RF-007: Protección por roles

**Descripción:** Las rutas de disponibilidad pública solo son accesibles para
estudiantes autenticados. Docentes y administradores también pueden verlas (uso
compartido).

**Escenario (estudiante autenticado):**
```gherkin
Given el estudiante ha iniciado sesión
When accede a /disponibilidad/docentes
Then ve el contenido correctamente (HTTP 200)
```

**Escenario (no autenticado):**
```gherkin
Given el usuario no ha iniciado sesión
When accede a /disponibilidad/docentes
Then es redirigido a la página de login
```

**Escenario (docente):**
```gherkin
Given el docente ha iniciado sesión
When accede a /disponibilidad/docentes
Then ve el contenido correctamente (HTTP 200)
```

---

### RF-008: Auditoría de solicitudes

**Descripción:** Las solicitudes de tutoría siguen registrando la acción en AuditLog
como antes. No se modificó el comportamiento de auditoría existente.

**Escenario:**
```gherkin
Given el estudiante solicita una tutoría válida
Then se registra una entrada en audit_logs con action="REQUEST_TUTORIA"
And la entrada contiene el teacher_id, student_id, y la IP del estudiante
```

---

## Requisitos No Funcionales

### RNF-001: Seguridad
- Las rutas nuevas deben usar `@login_required` y `@roles_required('estudiante', 'docente')`
- No se exponen datos sensibles (el email del docente es información de contacto)
- La validación de disponibilidad es server-side, no confiable en cliente
- CSRF protegido (ya incluido por Flask-WTF global)

### RNF-002: Usabilidad
- Los mensajes de error deben usar flash messages con categoría `warning`
- Los mensajes de éxito deben usar flash messages con categoría `success`
- La interfaz debe ser responsive (Bootstrap 5.3)
- Los horarios deben mostrarse en formato HH:MM de 24 horas

### RNF-003: Compatibilidad
- Sin cambios en el modelo de datos (no hay migraciones)
- Sin cambios en rutas existentes
- Sin nuevas dependencias

### RNF-004: Rendimiento
- Las consultas a disponibilidad deben usar filtros eficientes con índices existentes
- La lista de docentes con disponibilidad debe usar JOIN + DISTINCT para evitar duplicados

---

## Criterios de Aceptación

- [ ] RF-001: Listado de docentes con disponibilidad funciona correctamente
- [ ] RF-002: Tabla semanal muestra slots ordenados por día y hora
- [ ] RF-003: Navbar de estudiante tiene enlace "Horarios Disponibles"
- [ ] RF-004: Pre-selección de docente vía query string funciona
- [ ] RF-005: Selector de docentes solo muestra aquellos con slots activos
- [ ] RF-006: Validación server-side rechaza fechas/horas fuera de disponibilidad
- [ ] RF-006: Validación server-side acepta fechas/horas dentro de disponibilidad
- [ ] RF-007: Rutas protegidas — no autenticados redirigidos al login
- [ ] RF-007: Roles correctos — estudiante y docente pueden acceder
- [ ] RF-008: Auditoría sigue funcionando sin cambios

---

## Matriz de Trazabilidad

| Requisito | Archivo(s) Afectados | Tipo de Cambio |
|-----------|---------------------|----------------|
| RF-001 | `app/availability/routes.py`, `app/templates/availability/teacher_list.html` | +ruta, +template |
| RF-002 | `app/availability/routes.py`, `app/templates/availability/teacher_slots.html` | +ruta, +template |
| RF-003 | `app/templates/base.html` | +link navbar |
| RF-004 | `app/appointments/routes.py`, `app/templates/appointments/request.html` | +query string handling |
| RF-005 | `app/appointments/forms.py` | +filtro en query |
| RF-006 | `app/appointments/routes.py` | +validación server-side |
| RF-007 | `app/availability/routes.py` | decoradores existentes |
| RF-008 | Sin cambios | ya funciona |

---

## Dependencias

- Modelo `Availability` ya existe en `app/models.py`
- DÍA_MAP disponible en `app/availability/forms.py` (`DAY_CHOICES`)
- Blueprint `availability` ya registrado en `app/__init__.py`
- `AppointmentForm` ya existe en `app/appointments/forms.py`
- Ruta `request_tutoria()` ya existe en `app/appointments/routes.py`
