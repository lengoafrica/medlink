from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from medlink.config import Config
from logging.handlers import SMTPHandler
import logging

mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
lm = LoginManager()
lm.login_view = 'doctors.login'
lm.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    from medlink.doctors.routes import doctors
    from medlink.appointments.routes import appointments

    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    lm.init_app(app)

    app.register_blueprint(doctors)
    app.register_blueprint(appointments)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=('no-reply@' + app.config['MAIL_SERVER']),
                toaddrs=app.config['ADMINS'], subject='Fourblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

    return(app)
