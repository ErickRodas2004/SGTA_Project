# Sistema de Gestión de Tutorías Académicas (SGTA)

## 👥Integrantes
* *Amaguaya Satan Angel Hernan*
* *Bohórquez Yagual Leonardo Alexy*
* *Centeno Lozano Bryant Snayder*
* *Pincay Salazar Marlon Jose*
* *Erick Josue Rodas Quimis*

## 🎥 Video de Defensa del Proyecto
https://youtu.be/IhgYUO7sXV4

## 📝Descripción del Proyecto
El **Sistema de Gestión de Tutorías Académicas (SGTA)** es una aplicación web desarrollada en Python diseñada para optimizar y asegurar el proceso de asesorías universitarias. El sistema centraliza la comunicación académica permitiendo a los estudiantes solicitar tutorías de manera eficiente, a los docentes organizar sus agendas y registrar retroalimentación, y a la administración gestionar los accesos, todo bajo un entorno estrictamente seguro y auditable.

## Principales Funcionalidades
El sistema implementa un modelo de Control de Acceso Basado en Roles (RBAC) con tres perfiles principales:

*   **Estudiantes:** Visualización de disponibilidad, agendamiento de tutorías y gestión de citas (cancelaciones).
*   **Docentes:** Administración de horarios disponibles, revisión de estudiantes agendados y registro de notas/feedback de las sesiones.
*   **Administrador:** Control total del ciclo de vida de los usuarios (creación y baja de cuentas), asignación de roles y supervisión de los registros de auditoría del sistema.

## ⚙️Stack Tecnológico y Seguridad
El proyecto fue construido priorizando un desarrollo ágil y seguro, utilizando el ecosistema de Python y herramientas que garantizan la protección de los datos:

*   **Framework Base:** Flask / FastAPI.
*   **Base de Datos y ORM:** SQLite gestionado a través de Flask-SQLAlchemy, operando como un archivo local sin necesidad de servidores externos.
*   **Seguridad y Autenticación:** 
    *   **Flask-Bcrypt:** Hashing seguro de contraseñas con generación automática de *salts*.
    *   **Flask-Login:** Gestión de sesiones y protección de rutas mediante decoradores personalizados (ej. `@roles_required`).
    *   **Flask-Talisman:** Forzado de HTTPS, configuración de CSP y protección automática contra XSS y Clickjacking.
    *   **Flask-WTF:** Mitigación de ataques CSRF en la validación de formularios.
*   **Trazabilidad:** Tabla de auditoría (AuditLog) que captura acciones de usuarios, tablas afectadas, IPs y marcas de tiempo.


