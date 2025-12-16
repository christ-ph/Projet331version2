from app import db
from flask_bcrypt import Bcrypt
import enum

bcrypt = Bcrypt()

# ============================
# ENUMS
# ============================

class MissionStatus(enum.Enum):
    DRAFT = "draft"         
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PostulationStatus(enum.Enum):
    PENDING = "pending"     
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


# ============================
# ROLE
# ============================

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    users = db.relationship('User', backref='role', lazy='select')


# ============================
# USER
# ============================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.now())
    last_connection_at = db.Column(db.DateTime, default=db.func.now())

    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    verification_token = db.Column(db.String(255), nullable=True)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    profile = db.relationship('Profile', backref='user', uselist=False)

    def set_password(self, password):
        hashed = bcrypt.generate_password_hash(password)
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


# ============================
# PROFILE (classe mère polymorphique)
# ============================

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    phone = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(255), nullable=True)

    bio = db.Column(db.String(500), nullable=True)
    url_photo = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    portfolios = db.relationship('Portfolio', backref='profile', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'profile'
    }


# ============================
# FREELANCE PROFILE
# ============================

class FreelanceProfile(Profile):
    id = db.Column(db.Integer, db.ForeignKey('profile.id'), primary_key=True)

    full_name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(500), nullable=True)

    skills = db.Column(db.JSON, nullable=True)
    languages = db.Column(db.JSON, nullable=True)

    hourly_rate = db.Column(db.Float, nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    availability = db.Column(db.String(100), nullable=True)

    rating = db.Column(db.Float, default=0.0)
    completed_projects = db.Column(db.Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 'freelance'
    }


# ============================
# CLIENT PROFILE
# ============================

class ClientProfile(Profile):
    id = db.Column(db.Integer, db.ForeignKey('profile.id'), primary_key=True)

    client_type = db.Column(db.String(50), nullable=False)  # particulier / entreprise / agence / boutique

    fullname = db.Column(db.String(255), nullable=True)  # particulier
    company_name = db.Column(db.String(255), nullable=True)  # entreprise
    company_website = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(255), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'client'
    }


# ============================
# PORTFOLIO
# ============================

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=db.func.now())

    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================
# MISSION
# ============================

class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    budget = db.Column(db.Float, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    required_skills = db.Column(db.JSON, nullable=True) 

    status = db.Column(db.Enum(MissionStatus), default=MissionStatus.OPEN, nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relation avec le client (User qui a role = client)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client = db.relationship(
        'User',
        foreign_keys=[client_id],
        backref=db.backref('missions', lazy='dynamic')
    )

    # Relation avec les postulations (freelances qui postulent)
    postulations = db.relationship(
        'Postulation',
        backref='mission',
        lazy='dynamic',
        cascade="all, delete-orphan"
    )


# ============================
# POSTULATION
# ============================

class Postulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.Enum(PostulationStatus), default=PostulationStatus.PENDING, nullable=False)

    # Relation vers la mission
    mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), nullable=False)

    # Relation vers le freelance (User avec role = freelance)
    freelance_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    freelance = db.relationship(
        'User',
        backref=db.backref('postulations', lazy='dynamic')
    )

    __table_args__ = (
        db.UniqueConstraint('mission_id', 'freelance_id', name='uq_postulation_mission_freelance'),
    )
