from app import db, bcrypt
from enum import Enum
from datetime import datetime


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    
    def set_password(self, password):
        hashed = bcrypt.generate_password_hash(password)
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    full_name = db.Column(db.String(80), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.String(255), nullable=True)
    is_freelancer = db.Column(db.Boolean, default=False)

    # cle etrangere vers user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # relation Bidirectionnel 
    user = db.relationship('User',backref=db.backref('profile', uselist=False))

    portfolio_items = db.relationship('PortfolioItem', backref='profile', lazy=True)

    def __repr__(self):
        return f'<Profile {self.full_name}>'


class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    project_url = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    
    # Clé étrangère vers le Profile
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)

    def to_dict(self):
        # Fonction utilitaire pour sérialiser l'objet
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'title': self.title,
            'description': self.description,
            'project_url': self.project_url,
            'image_url': self.image_url
        }



class MissionStatus(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"


class ApplicationStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    budget = db.Column(db.Float, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    required_skills = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum(MissionStatus), default=MissionStatus.DRAFT, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='mission', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'title': self.title,
            'description': self.description,
            'budget': self.budget,
            'duration': self.duration,
            'required_skills': self.required_skills,
            'status': self.status.name if isinstance(self.status, Enum) else str(self.status),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), nullable=False)
    freelance_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    proposal = db.Column(db.Text, nullable=True)
    proposed_budget = db.Column(db.Float, nullable=True)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'mission_id': self.mission_id,
            'freelance_id': self.freelance_id,
            'proposal': self.proposal,
            'proposed_budget': self.proposed_budget,
            'status': self.status.name if isinstance(self.status, Enum) else str(self.status),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }