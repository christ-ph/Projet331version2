from datetime import datetime
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

class DeliverableStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

# ============================
# NOUVEAU : ENUM pour ChatType
# ============================

class ChatType(enum.Enum):
    MISSION = "mission"
    SUPPORT = "support"

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
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender')
    chats_as_user1 = db.relationship('Chat', foreign_keys='Chat.user1_id', backref='user1')
    chats_as_user2 = db.relationship('Chat', foreign_keys='Chat.user2_id', backref='user2')

    def set_password(self, password):
        hashed = bcrypt.generate_password_hash(password)
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    



# Ajouter ces Enums avec les autres au début du fichier
class ComplaintStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AdminActionType(enum.Enum):
    APPROVE_COMPLAINT = "approve_complaint"
    REJECT_COMPLAINT = "reject_complaint"
    BLOCK_USER = "block_user"
    UNBLOCK_USER = "unblock_user"

# ============================
# ACTION ACCOUNT (Plainte)
# ============================

class ActionAccount(db.Model):
    __tablename__ = 'action_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    plaintiff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_email = db.Column(db.String(120), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(ComplaintStatus), default=ComplaintStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relations
    plaintiff = db.relationship('User', foreign_keys=[plaintiff_id], backref='filed_complaints')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_complaints')
    
    def to_dict(self):
        return {
            'id': self.id,
            'plaintiff_id': self.plaintiff_id,
            'plaintiff_email': self.plaintiff.email if self.plaintiff else None,
            'reported_email': self.reported_email,
            'reason': self.reason,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewed_by': self.reviewed_by
        }

# ============================
# ADMIN ACTION (Historique)
# ============================

class AdminAction(db.Model):
    __tablename__ = 'admin_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action_type = db.Column(db.Enum(AdminActionType), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action_account_id = db.Column(db.Integer, db.ForeignKey('action_accounts.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Relations
    admin = db.relationship('User', foreign_keys=[admin_id], backref='admin_actions')
    target_user = db.relationship('User', foreign_keys=[target_user_id], backref='actions_received')
    action_account = db.relationship('ActionAccount', backref='admin_actions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_email': self.admin.email if self.admin else None,
            'action_type': self.action_type.value,
            'target_user_id': self.target_user_id,
            'target_user_email': self.target_user.email if self.target_user else None,
            'action_account_id': self.action_account_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============================
# CHAT (Ajouté)
# ============================

class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Type de chat : "mission" (client<->freelance) ou "support" (user<->admin)
    chat_type = db.Column(db.Enum(ChatType), nullable=False)  # "mission" ou "support"
    
    # Participants
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Null si support (admin multiple)
    
    # Relation avec mission (optionnel, seulement pour chat type "mission")
    mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), nullable=True)
    
    # Compteurs de notifications (système de polling)
    notification_user1 = db.Column(db.Integer, default=0)  # Compteur pour user1
    notification_user2 = db.Column(db.Integer, default=0)  # Compteur pour user2
    notification_admin = db.Column(db.Integer, default=0)  # Compteur pour admin (support uniquement)
    
    # Dates
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # Relations
    mission = db.relationship('Mission', backref='chat')
    messages = db.relationship('Message', backref='chat', lazy='dynamic', cascade='all, delete-orphan')
    
    def increment_notification(self, recipient_role):
        """Incrémente le compteur selon le destinataire"""
        if recipient_role == 'CLIENT':
            self.notification_user1 += 1
        elif recipient_role == 'FREELANCE':
            self.notification_user2 += 1
        elif recipient_role == 'ADMIN':
            self.notification_admin += 1
        db.session.commit()
    
    def decrement_notification(self, user_role):
        """Décrémente le compteur quand l'utilisateur consulte"""
        if user_role == 'CLIENT':
            self.notification_user1 = 0
        elif user_role == 'FREELANCE':
            self.notification_user2 = 0
        elif user_role == 'ADMIN':
            self.notification_admin = 0
        db.session.commit()
    
    def get_notification_count(self, user_id, user_role):
        """Retourne le compteur de notifications pour cet utilisateur"""
        if user_role == 'ADMIN':
            return self.notification_admin
        elif self.user1_id == user_id:
            return self.notification_user1
        elif self.user2_id == user_id:
            return self.notification_user2
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'chat_type': self.chat_type.value,
            'user1_id': self.user1_id,
            'user2_id': self.user2_id,
            'mission_id': self.mission_id,
            'notification_user1': self.notification_user1,
            'notification_user2': self.notification_user2,
            'notification_admin': self.notification_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ============================
# MESSAGE (Ajouté)
# ============================

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Contenu
    content = db.Column(db.Text, nullable=False)
    
    # Fichiers joints (optionnel)
    file_url = db.Column(db.String(500), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    
    # Statut de lecture
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relations
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Dates
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def mark_as_read(self):
        """Marque le message comme lu"""
        self.is_read = True
        self.read_at = datetime.now()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'file_url': self.file_url,
            'file_name': self.file_name,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'chat_id': self.chat_id,
            'sender_id': self.sender_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

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
# MISSION (Corrigé - ajout assigned_freelance_id)
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

    # Relation avec le client
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client = db.relationship('User', foreign_keys=[client_id], backref=db.backref('missions', lazy='dynamic'))
    
    # AJOUT : Freelance assigné (quand mission acceptée)
    assigned_freelance_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    assigned_freelance = db.relationship('User', foreign_keys=[assigned_freelance_id], backref='assigned_missions')

    # Relation avec les postulations
    postulations = db.relationship('Postulation', backref='mission', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'budget': self.budget,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'required_skills': self.required_skills,
            'status': self.status.value,
            'client_id': self.client_id,
            'assigned_freelance_id': self.assigned_freelance_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ============================
# POSTULATION
# ============================

class Postulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.Enum(PostulationStatus), default=PostulationStatus.PENDING, nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), nullable=False)
    freelance_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    freelance = db.relationship('User', backref=db.backref('postulations', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('mission_id', 'freelance_id', name='uq_postulation_mission_freelance'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'mission_id': self.mission_id,
            'freelance_id': self.freelance_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============================
# DELIVERABLE (Livrable)
# ============================

class Deliverable(db.Model):
    __tablename__ = 'deliverables'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    submitted_at = db.Column(db.DateTime, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(DeliverableStatus), default=DeliverableStatus.DRAFT, nullable=False)
    client_feedback = db.Column(db.Text, nullable=True)
    mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), nullable=False)
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    accepted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    mission = db.relationship('Mission', backref=db.backref('deliverables', lazy='dynamic'))
    submitter = db.relationship('User', foreign_keys=[submitted_by], backref='submitted_deliverables')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_deliverables')
    accepter = db.relationship('User', foreign_keys=[accepted_by], backref='accepted_deliverables')
    
    def submit(self, freelance_user):
        self.submitted_by = freelance_user.id
        self.status = DeliverableStatus.SUBMITTED
        self.submitted_at = datetime.now()
    
    def accept(self, client_user):
        self.status = DeliverableStatus.ACCEPTED
        self.accepted_by = client_user.id
        self.accepted_at = datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'file_url': self.file_url,
            'status': self.status.value,
            'client_feedback': self.client_feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'mission_id': self.mission_id,
            'submitted_by': self.submitted_by,
            'reviewed_by': self.reviewed_by,
            'accepted_by': self.accepted_by
        }