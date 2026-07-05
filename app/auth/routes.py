"""Auth routes — register, login, logout."""

from flask import redirect, render_template, request, url_for, flash
from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.models import User
from app.log_audit import log_audit
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Create a new user account with role='estudiante'."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='estudiante',
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        log_audit('REGISTER_USER', 'users', record_id=user.id)

        flash('Cuenta creada correctamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate user and redirect to role-specific dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Credenciales inválidas. Verifica tu usuario y contraseña.', 'danger')
            return render_template('auth/login.html', form=form)

        if not user.is_active:
            flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
            return render_template('auth/login.html', form=form)

        login_user(user, remember=form.remember_me.data)
        log_audit('LOGIN', 'users', record_id=user.id)

        # Redirect to role-specific dashboard
        role_routes = {
            'estudiante': 'main.dashboard',
            'docente': 'main.dashboard',
            'administrador': 'main.dashboard',
        }
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        return redirect(url_for(role_routes.get(user.role, 'main.dashboard')))

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """Log out the current user and redirect to login."""
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))
