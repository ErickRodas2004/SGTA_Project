"""Availability routes — docente CRUD for time slots."""

from flask import redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Availability
from app.decorators import roles_required
from app.availability import availability_bp
from app.availability.forms import AvailabilityForm, DAY_CHOICES


# Build a reverse lookup: int → Spanish day name
DAY_MAP = dict(DAY_CHOICES)


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
