from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_mail import Mail
from config import config
import logging


db = SQLAlchemy()

bootstrap = Bootstrap()

mail = Mail()

admin = Admin(name="User management")


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Configure logging
    handler = logging.FileHandler(app.config['LOGGING_LOCATION'])
    handler.setLevel(app.config['LOGGING_LEVEL'])
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    admin.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .userManagement import userMngmt as userMngmt_blueprint
    app.register_blueprint(userMngmt_blueprint, url_prefix='/userManagement')

    return app
