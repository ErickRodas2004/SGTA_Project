"""WTForms for appointments — AppointmentForm, FeedbackForm."""

from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, TextAreaField, TimeField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import User


class AppointmentForm(FlaskForm):
    """Form for a student to request a tutoring session."""

    teacher = SelectField(
        'Docente',
        coerce=int,
        validators=[DataRequired(message='Selecciona un docente.')],
    )
    subject = StringField(
        'Materia / Tema',
        validators=[
            DataRequired(message='La materia o tema es obligatorio.'),
            Length(min=3, max=200, message='El tema debe tener entre 3 y 200 caracteres.'),
        ],
        render_kw={'placeholder': 'Ej: Álgebra lineal, Programación en Python', 'autofocus': True},
    )
    description = TextAreaField(
        'Descripción (opcional)',
        validators=[Length(max=2000, message='La descripción no debe exceder 2000 caracteres.')],
        render_kw={
            'placeholder': 'Describe brevemente lo que necesitas tratar en la tutoría...',
            'rows': 4,
        },
    )
    scheduled_date = DateField(
        'Fecha',
        validators=[DataRequired(message='Selecciona una fecha para la tutoría.')],
        render_kw={'type': 'date'},
    )
    scheduled_time = TimeField(
        'Hora',
        validators=[DataRequired(message='Selecciona una hora para la tutoría.')],
        render_kw={'type': 'time'},
    )
    submit = SubmitField('Solicitar tutoría')

    def __init__(self, *args, **kwargs):
        """Load docente choices dynamically."""
        super().__init__(*args, **kwargs)
        docentes = User.query.filter_by(role='docente', is_active=True).order_by(User.username).all()
        self.teacher.choices = [
            (d.id, f'{d.username} — {d.email}') for d in docentes
        ]

    def validate_scheduled_date(self, field):
        """Reject past dates."""
        if field.data and field.data <= date.today():
            raise ValidationError('La fecha debe ser posterior a hoy.')


class FeedbackForm(FlaskForm):
    """Form for a docente to record feedback after a tutoring session."""

    feedback = TextAreaField(
        'Comentarios / Retroalimentación',
        validators=[
            DataRequired(message='Los comentarios son obligatorios.'),
            Length(min=10, max=2000, message='La retroalimentación debe tener entre 10 y 2000 caracteres.'),
        ],
        render_kw={
            'placeholder': 'Describe cómo fue la tutoría, temas cubiertos, recomendaciones...',
            'rows': 6,
            'autofocus': True,
        },
    )
    submit = SubmitField('Guardar y completar tutoría')
