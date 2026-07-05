"""Users routes — admin CRUD for user management."""

from flask import redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required

from app.extensions import db
from app.models import User
from app.decorators import roles_required
from app.log_audit import log_audit
from app.users import users_bp
from app.users.forms import UserForm, EditUserForm


@users_bp.route('/usuarios')
@login_required
@roles_required('administrador')
def list_users():
    """Paginated list of all users."""
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False,
    )
    users = pagination.items
    return render_template(
        'users/list.html',
        users=users,
        pagination=pagination,
    )


@users_bp.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
@roles_required('administrador')
def create_user():
    """Create a new user with any role."""
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        log_audit(
            'CREATE_USER', 'users',
            record_id=user.id,
            details={'role': form.role.data, 'username': form.username.data},
        )

        flash(f'Usuario "{user.username}" creado correctamente.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('users/create.html', form=form)


@users_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@roles_required('administrador')
def edit_user(id):
    """Edit an existing user's profile, role, or credentials."""
    user = User.query.get_or_404(id)

    form = EditUserForm(
        original_username=user.username,
        original_email=user.email,
        obj=user,
    )

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        db.session.commit()

        log_audit(
            'UPDATE_USER', 'users',
            record_id=user.id,
            details={
                'username': user.username,
                'role': user.role,
            },
        )

        flash(f'Usuario "{user.username}" actualizado correctamente.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('users/edit.html', form=form, user=user)


@users_bp.route('/usuarios/<int:id>/baja', methods=['POST'])
@login_required
@roles_required('administrador')
def deactivate_user(id):
    """Soft-delete a user by setting is_active=False."""
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'danger')
        return redirect(url_for('users.list_users'))

    if not user.is_active:
        flash(f'El usuario "{user.username}" ya está desactivado.', 'warning')
        return redirect(url_for('users.list_users'))

    user.is_active = False
    db.session.commit()

    log_audit(
        'DEACTIVATE_USER', 'users',
        record_id=user.id,
        details={'username': user.username},
    )

    flash(f'Usuario "{user.username}" desactivado correctamente.', 'success')
    return redirect(url_for('users.list_users'))
