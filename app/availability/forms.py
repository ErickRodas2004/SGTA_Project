"""WTForms for availability — AvailabilityForm."""

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TimeField
from wtforms.validators import DataRequired, ValidationError


# Mapping integer day → Spanish display name
DAY_CHOICES = [
    (0, 'Lunes'),
    (1, 'Martes'),
    (2, 'Miércoles'),
    (3, 'Jueves'),
    (4, 'Viernes'),
    (5, 'Sábado'),
    (6, 'Domingo'),
]


class AvailabilityForm(FlaskForm):
    """Form for a docente to create an availability slot."""

    day_of_week = SelectField(
        'Día de la semana',
        coerce=int,
        choices=DAY_CHOICES,
        validators=[DataRequired(message='Selecciona un día.')],
    )
    start_time = TimeField(
        'Hora de inicio',
        validators=[DataRequired(message='Indica la hora de inicio.')],
        render_kw={'type': 'time'},
    )
    end_time = TimeField(
        'Hora de fin',
        validators=[DataRequired(message='Indica la hora de fin.')],
        render_kw={'type': 'time'},
    )
    submit = SubmitField('Agregar bloque')

    def validate_end_time(self, field):
        """Ensure start_time < end_time."""
        if self.start_time.data and field.data and self.start_time.data >= field.data:
            raise ValidationError(
                'La hora de fin debe ser posterior a la hora de inicio.',
            )
