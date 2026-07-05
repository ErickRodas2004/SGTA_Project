"""Appointments routes — student request/list/cancel + docente accept/feedback."""

from datetime import date, datetime, timedelta, time

from flask import redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Appointment, User, Availability
from app.decorators import roles_required
from app.log_audit import log_audit
from app.appointments import appointments_bp
from app.appointments.forms import AppointmentForm, FeedbackForm


def _next_weekday(target_dow: int, at_time: time | None = None) -> date:
    """Return the next occurrence of `target_dow` (0=Monday) from today.
    
    If `at_time` is given and target_dow is today, returns today only
    if the time hasn't passed yet. Otherwise jumps to next week.
    """
    today = date.today()
    today_dow = today.weekday()
    days_ahead = target_dow - today_dow
    if days_ahead < 0 or (days_ahead == 0 and at_time and datetime.now().time() >= at_time):
        days_ahead += 7
    return today + timedelta(days=days_ahead)


# =========================================================================
# Student routes
# =========================================================================


@appointments_bp.route('/solicitar', methods=['GET', 'POST'])
@login_required
@roles_required('estudiante')
def request_tutoria():
    """Request a new tutoring session (status='pending')."""
    form = AppointmentForm()

    # Pre-seleccionar docente y fecha/hora si vienen por query string (desde horarios disponibles)
    teacher_id = request.args.get('teacher_id', type=int)
    if teacher_id and request.method == 'GET':
        teacher = User.query.get(teacher_id)
        if teacher and teacher.role == 'docente':
            form.teacher.data = teacher_id

        # Pre-fill date and time from slot (day=0-6, time=HH:MM)
        slot_day = request.args.get('day', type=int)
        slot_time = request.args.get('time')
        if slot_day is not None and slot_time:
            try:
                hour, minute = map(int, slot_time.split(':'))
                proposed_time = time(hour, minute)
                proposed_date = _next_weekday(slot_day, proposed_time)
                form.scheduled_date.data = proposed_date
                form.scheduled_time.data = proposed_time
            except (ValueError, TypeError):
                pass

    if form.validate_on_submit():
        # Validar disponibilidad del docente para la fecha/hora seleccionada
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

        appointment = Appointment(
            student_id=current_user.id,
            teacher_id=form.teacher.data,
            subject=form.subject.data,
            description=form.description.data,
            scheduled_date=form.scheduled_date.data,
            scheduled_time=form.scheduled_time.data,
            status='pending',
        )
        db.session.add(appointment)
        db.session.commit()

        log_audit(
            'REQUEST_TUTORIA', 'appointments',
            record_id=appointment.id,
            details={
                'teacher_id': form.teacher.data,
                'subject': form.subject.data,
                'date': str(form.scheduled_date.data),
            },
        )

        flash('Tutoría solicitada correctamente.', 'success')
        return redirect(url_for('appointments.my_tutorias'))

    return render_template('appointments/request.html', form=form)


@appointments_bp.route('/mis-tutorias')
@login_required
@roles_required('estudiante')
def my_tutorias():
    """List the current student's appointments, filterable by status."""
    status_filter = request.args.get('status', '').strip()

    query = Appointment.query.filter_by(student_id=current_user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    appointments = query.order_by(Appointment.scheduled_date.desc()).all()

    return render_template(
        'appointments/my_list.html',
        appointments=appointments,
        current_status=status_filter,
    )


@appointments_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
@roles_required('estudiante')
def cancel_tutoria(id):
    """Cancel an appointment — only own pending/accepted appointments."""
    appointment = Appointment.query.get_or_404(id)

    # Guard: can only cancel own appointment
    if appointment.student_id != current_user.id:
        flash('No puedes cancelar una tutoría que no te pertenece.', 'danger')
        return redirect(url_for('appointments.my_tutorias'))

    # Guard: cannot cancel completed appointments
    if appointment.status == 'completed':
        flash('No se puede cancelar una tutoría ya completada.', 'danger')
        return redirect(url_for('appointments.my_tutorias'))

    # Guard: already cancelled
    if appointment.status == 'cancelled':
        flash('Esta tutoría ya está cancelada.', 'warning')
        return redirect(url_for('appointments.my_tutorias'))

    appointment.status = 'cancelled'
    db.session.commit()

    log_audit(
        'CANCEL_TUTORIA', 'appointments',
        record_id=appointment.id,
        details={
            'previous_status': appointment.status,
            'subject': appointment.subject,
        },
    )

    flash('Tutoría cancelada correctamente.', 'success')
    return redirect(url_for('appointments.my_tutorias'))


# =========================================================================
# Docente routes
# =========================================================================


@appointments_bp.route('/docente/agendados')
@login_required
@roles_required('docente')
def assigned_students():
    """List appointments assigned to the current docente, grouped by status."""
    appointments = (
        Appointment.query
        .filter_by(teacher_id=current_user.id)
        .order_by(Appointment.scheduled_date.desc())
        .all()
    )

    # Group by status for display
    grouped = {
        'pending': [a for a in appointments if a.status == 'pending'],
        'accepted': [a for a in appointments if a.status == 'accepted'],
        'completed': [a for a in appointments if a.status == 'completed'],
        'cancelled': [a for a in appointments if a.status == 'cancelled'],
    }

    return render_template('appointments/assigned_list.html', grouped=grouped)


@appointments_bp.route('/<int:id>/aceptar', methods=['POST'])
@login_required
@roles_required('docente')
def accept_tutoria(id):
    """Accept a pending tutoring request."""
    appointment = Appointment.query.get_or_404(id)

    # Guard: only assigned teacher can accept
    if appointment.teacher_id != current_user.id:
        flash('No puedes aceptar una tutoría que no te fue asignada.', 'danger')
        return redirect(url_for('appointments.assigned_students'))

    # Guard: only pending appointments can be accepted
    if appointment.status != 'pending':
        flash('Solo se pueden aceptar tutorías en estado pendiente.', 'warning')
        return redirect(url_for('appointments.assigned_students'))

    appointment.status = 'accepted'
    db.session.commit()

    log_audit(
        'ACCEPT_TUTORIA', 'appointments',
        record_id=appointment.id,
        details={
            'student_id': appointment.student_id,
            'subject': appointment.subject,
        },
    )

    flash(f'Tutoría "{appointment.subject}" aceptada correctamente.', 'success')
    return redirect(url_for('appointments.assigned_students'))


@appointments_bp.route('/<int:id>/feedback', methods=['GET', 'POST'])
@login_required
@roles_required('docente')
def feedback_form(id):
    """Record feedback for a completed tutoring session."""
    appointment = Appointment.query.get_or_404(id)

    # Guard: only assigned teacher can provide feedback
    if appointment.teacher_id != current_user.id:
        flash('No puedes dar feedback de una tutoría que no te pertenece.', 'danger')
        return redirect(url_for('appointments.assigned_students'))

    # Guard: feedback only allowed for accepted appointments (marks them completed)
    if appointment.status != 'accepted':
        if appointment.status == 'completed':
            flash('Esta tutoría ya fue completada y tiene feedback registrado.', 'info')
            return redirect(url_for('appointments.assigned_students'))
        flash('Solo se puede añadir feedback a tutorías en estado aceptado.', 'warning')
        return redirect(url_for('appointments.assigned_students'))

    form = FeedbackForm()
    if form.validate_on_submit():
        appointment.feedback = form.feedback.data
        appointment.status = 'completed'
        db.session.commit()

        log_audit(
            'COMPLETE_TUTORIA', 'appointments',
            record_id=appointment.id,
            details={
                'student_id': appointment.student_id,
                'subject': appointment.subject,
            },
        )

        flash('Feedback registrado y tutoría completada correctamente.', 'success')
        return redirect(url_for('appointments.assigned_students'))

    return render_template(
        'appointments/feedback.html',
        form=form,
        appointment=appointment,
    )
