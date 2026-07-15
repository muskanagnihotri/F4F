import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, flash, redirect, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import config_by_name


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


@login_manager.user_loader
def load_user(user_id):
    from app.models import User

    return User.query.get(user_id)


login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)

    if not os.path.exists(app.config["LOG_FILE"].parent):
        os.makedirs(app.config["LOG_FILE"].parent)

    handler = RotatingFileHandler(app.config["LOG_FILE"], maxBytes=2 * 1024 * 1024, backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.farmers.routes import farmers_bp
    from app.implementations.routes import implementations_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(farmers_bp)
    app.register_blueprint(implementations_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_user():
        return {"current_user": current_user}

    @app.errorhandler(403)
    def forbidden_error(error):
        flash("You do not have permission to access that resource.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    return app
