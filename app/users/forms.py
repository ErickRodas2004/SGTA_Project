"""WTForms for admin user management — UserForm, EditUserForm."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from app.models import User


class UserForm(FlaskForm):
    """Create a new user — includes password field."""

    username = StringField(
        'Usuario',
        validators=[
            DataRequired(message='El nombre de usuario es obligatorio.'),
            Length(min=3, max=80, message='El usuario debe tener entre 3 y 80 caracteres.'),
        ],
        render_kw={'placeholder': 'Nombre de usuario', 'autofocus': True},
    )
    email = StringField(
        'Correo electrónico',
        validators=[
            DataRequired(message='El correo electrónico es obligatorio.'),
            Email(message='Ingresa un correo electrónico válido.'),
            Length(max=120),
        ],
        render_kw={'placeholder': 'correo@ejemplo.com'},
    )
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria.'),
            Length(min=8, message='La contraseña debe tener al menos 8 caracteres.'),
        ],
        render_kw={'placeholder': 'Mínimo 8 caracteres'},
    )
    role = SelectField(
        'Rol',
        choices=[
            ('estudiante', 'Estudiante'),
            ('docente', 'Docente'),
            ('administrador', 'Administrador'),
        ],
        validators=[DataRequired(message='Selecciona un rol.')],
        default='estudiante',
    )
    submit = SubmitField('Crear usuario')

    def validate_username(self, field):
        """Check username uniqueness."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Este nombre de usuario ya está registrado.')

    def validate_email(self, field):
        """Check email uniqueness."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este correo electrónico ya está registrado.')


class EditUserForm(FlaskForm):
    """Edit an existing user — no password field."""

    username = StringField(
        'Usuario',
        validators=[
            DataRequired(message='El nombre de usuario es obligatorio.'),
            Length(min=3, max=80, message='El usuario debe tener entre 3 y 80 caracteres.'),
        ],
        render_kw={'placeholder': 'Nombre de usuario', 'autofocus': True},
    )
    email = StringField(
        'Correo electrónico',
        validators=[
            DataRequired(message='El correo electrónico es obligatorio.'),
            Email(message='Ingresa un correo electrónico válido.'),
            Length(max=120),
        ],
        render_kw={'placeholder': 'correo@ejemplo.com'},
    )
    role = SelectField(
        'Rol',
        choices=[
            ('estudiante', 'Estudiante'),
            ('docente', 'Docente'),
            ('administrador', 'Administrador'),
        ],
        validators=[DataRequired(message='Selecciona un rol.')],
    )
    submit = SubmitField('Guardar cambios')

    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        """Store original values for uniqueness checks."""
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, field):
        """Check username uniqueness — skip if unchanged."""
        if field.data != self.original_username:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError('Este nombre de usuario ya está registrado.')

    def validate_email(self, field):
        """Check email uniqueness — skip if unchanged."""
        if field.data != self.original_email:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('Este correo electrónico ya está registrado.')
