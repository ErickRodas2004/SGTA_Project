"""Flask CLI commands — seed, maintenance, and dev utilities."""

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import User
from app.log_audit import log_audit


@click.command('seed')
@with_appcontext
def seed_command():
    """Seed the database with initial users (admin + docente).

    Safe to run multiple times — skips existing usernames.
    """
    from flask import current_app

    seed_users = [
        {
            'username': 'admin',
            'email': 'admin@sgta.com',
            'password': '12345678',
            'role': 'administrador',
        },
        {
            'username': 'docente',
            'email': 'docente@sgta.com',
            'password': '12345678',
            'role': 'docente',
        },
    ]

    created = 0
    skipped = 0

    for data in seed_users:
        existing = User.query.filter_by(username=data['username']).first()
        if existing:
            click.echo(f'  > {data["username"]} ya existe — omitido')
            skipped += 1
            continue

        user = User(
            username=data['username'],
            email=data['email'],
            role=data['role'],
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()  # flush to get user.id before commit

        log_audit(
            'CREATE_USER', 'users',
            record_id=user.id,
            details={
                'username': user.username,
                'role': user.role,
                'source': 'seed-command',
            },
        )
        click.echo(f'  + {data["username"]} ({data["role"]}) creado')
        created += 1

    db.session.commit()
    click.echo(f'\nResumen: {created} creado(s), {skipped} omitido(s).')


def init_app(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(seed_command)
