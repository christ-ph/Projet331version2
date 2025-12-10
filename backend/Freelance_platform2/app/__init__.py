from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_jwt_extended import JWT_Manager
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

# creation de l'objet db
db = SQLAlchemy()

# initialisation des composante de l'app
bcrypt = Bcrypt()
migrate = Migrate()
jwt = JWT_Manager()

# creation de l'app 
def create_app():
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	migrate.init_app(app)
	bcrypt.init_app(app)
	jwt.init_app(app)

	return app