from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail
from peter.config import Config

db=SQLAlchemy()
login_manager=LoginManager()
login_manager.login_view='users.login'
login_manager.login_message_category='info'


mail=Mail()


def create_app(config_class=Config):
	app=Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	from peter.users.routes import users
	from peter.posts.routes import posts
	from peter.main.routes import main
	from peter.errors.handlers import errors
	app.register_blueprint(users)
	
	app.register_blueprint(posts)
	app.register_blueprint(main)
	app.register_blueprint(errors)
	return app