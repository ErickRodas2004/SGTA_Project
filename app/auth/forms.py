"""WTForms for authentication — RegisterForm, LoginForm."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from app.models import User


class RegisterForm(FlaskForm):
    """User registration form."""

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
    confirm_password = PasswordField(
        'Confirmar contraseña',
        validators=[
            DataRequired(message='Debes confirmar la contraseña.'),
            EqualTo('password', message='Las contraseñas no coinciden.'),
        ],
        render_kw={'placeholder': 'Repite la contraseña'},
    )
    submit = SubmitField('Crear cuenta')

    # -- Custom validators --

    def validate_username(self, field):
        """Check username uniqueness."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Este nombre de usuario ya está registrado.')

    def validate_email(self, field):
        """Check email uniqueness."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este correo electrónico ya está registrado.')


class LoginForm(FlaskForm):
    """User login form."""

    username = StringField(
        'Usuario',
        validators=[DataRequired(message='Ingresa tu nombre de usuario.')],
        render_kw={'placeholder': 'Nombre de usuario', 'autofocus': True},
    )
    password = PasswordField(
        'Contraseña',
        validators=[DataRequired(message='Ingresa tu contraseña.')],
        render_kw={'placeholder': 'Contraseña'},
    )
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar sesión')
