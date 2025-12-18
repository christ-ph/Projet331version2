from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import config
from flask_mail import Mail

# initialisation des extention
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # initialisation eds extension avec l'app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    # Enregistrement de Blue Sprints
    from app.auth.routes import auth_bp
    from app.portfolio.routes import portfolio_bp
    app.register_blueprint(auth_bp, url_prefix='/auth') # J'ajoute /auth ici pour la clarté
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    from app.profiles.routes import profile_bp
    from app.missions.routes import missions_bp
    from app.livrable.routes import deliverables_bp
    from app.chats.routes import chat_bp
    from app.admin.routes import admin_bp
    app.register_blueprint(chat_bp, url_prefix='/api/chats')
    app.register_blueprint(deliverables_bp, url_prefix='/api/deliverables')
    app.register_blueprint(profile_bp, url_prefix='/api/profiles')
    app.register_blueprint(missions_bp , url_prefix='/api/missions')
    app.register_blueprint(admin_bp , url_prefix='/api/admin')

    # from app.chats.routes import chat_bp
    # app.register_blueprint(chat_bp) 
    
    return app
    
