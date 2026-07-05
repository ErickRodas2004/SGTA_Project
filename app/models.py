"""SQLAlchemy models — User, Appointment, Availability, AuditLog."""

from datetime import datetime, timezone

from flask_login import UserMixin

from app.extensions import db, bcrypt


class User(UserMixin, db.Model):
    """Platform user — estudiante, docente, or administrador."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # estudiante | docente | administrador
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # -- Relationships --
    appointments_as_student = db.relationship(
        'Appointment', foreign_keys='Appointment.student_id',
        backref='student', lazy='dynamic',
    )
    appointments_as_teacher = db.relationship(
        'Appointment', foreign_keys='Appointment.teacher_id',
        backref='teacher', lazy='dynamic',
    )
    availability_slots = db.relationship(
        'Availability', backref='teacher', lazy='dynamic',
    )
    audit_logs = db.relationship(
        'AuditLog', backref='user', lazy='dynamic',
    )

    # -- Flask-Login integration --
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active_user(self):
        """Return True if the account is active AND authenticated."""
        return self.is_active

    # -- Password methods --
    def set_password(self, password: str) -> None:
        """Hash and store the password using bcrypt."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored bcrypt hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    # -- Role helpers --
    def has_role(self, role: str) -> bool:
        """Check if the user has the given role."""
        return self.role == role

    def __repr__(self):
        return f'<User {self.id}:{self.username} [{self.role}]>'


class Appointment(db.Model):
    """Tutoring session request between a student and a teacher."""

    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.String(20),
        default='pending',
        nullable=False,
    )  # pending | accepted | completed | cancelled
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f'<Appointment {self.id}: {self.subject} [{self.status}]>'


class Availability(db.Model):
    """Teacher availability time slot."""

    __tablename__ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday … 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return (
            f'<Availability {self.id}: '
            f'Day {self.day_of_week} {self.start_time}-{self.end_time}>'
        )


class AuditLog(db.Model):
    """Immutable audit trail for sensitive operations."""

    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    username = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(100), nullable=False, index=True)
    table_affected = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON-encoded extra context
    ip_address = db.Column(db.String(45), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} on {self.table_affected}>'
