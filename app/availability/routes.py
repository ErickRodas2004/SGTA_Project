"""Availability routes — docente CRUD for time slots."""

from flask import redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Availability, User
from app.decorators import roles_required
from app.availability import availability_bp
from app.availability.forms import AvailabilityForm, DAY_CHOICES


# Build a reverse lookup: int → Spanish day name
DAY_MAP = dict(DAY_CHOICES)

# Mapping int day → Spanish display name (independent of form choices)
DIA_MAP = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}


@availability_bp.route('/', methods=['GET'])
@login_required
@roles_required('docente')
def manage_availability():
    """List the docente's current availability slots."""
    slots = (
        Availability.query
        .filter_by(teacher_id=current_user.id)
        .order_by(Availability.day_of_week, Availability.start_time)
        .all()
    )

    form = AvailabilityForm()

    return render_template(
        'availability/manage.html',
        slots=slots,
        form=form,
        day_map=DAY_MAP,
    )


@availability_bp.route('/crear', methods=['POST'])
@login_required
@roles_required('docente')
def create_slot():
    """Create a new availability slot."""
    form = AvailabilityForm()
    if form.validate_on_submit():
        slot = Availability(
            teacher_id=current_user.id,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
        )
        db.session.add(slot)
        db.session.commit()

        flash('Bloque de disponibilidad agregado correctamente.', 'success')
    else:
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, 'danger')

    return redirect(url_for('availability.manage_availability'))


@availability_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@roles_required('docente')
def delete_slot(id):
    """Delete an availability slot."""
    slot = Availability.query.get_or_404(id)

    # Guard: only the owning teacher can delete their slots
    if slot.teacher_id != current_user.id:
        flash('No puedes eliminar un bloque de disponibilidad que no te pertenece.', 'danger')
        return redirect(url_for('availability.manage_availability'))

    day_name = DAY_MAP.get(slot.day_of_week, str(slot.day_of_week))
    db.session.delete(slot)
    db.session.commit()

    flash(
        f'Bloque de {day_name} ({slot.start_time.strftime("%H:%M")} - '
        f'{slot.end_time.strftime("%H:%M")}) eliminado correctamente.',
        'success',
    )
    return redirect(url_for('availability.manage_availability'))


# =========================================================================
# Public routes — view teacher availability (estudiante / docente)
# =========================================================================


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
