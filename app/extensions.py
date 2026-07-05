"""Flask extensions — initialized here, bound to app in create_app()."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_talisman import Talisman

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
talisman = Talisman()  # No default CSP — configured in create_app() via app.config

# -- Login Manager defaults (applied before init_app takes config) --
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'
