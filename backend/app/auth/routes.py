from flask import Blueprint, jsonify, request 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity 
from app import db, mail # On importe db pour les sessions et les commits
from app.models import User, Role
from sqlalchemy import select # Import nécessaire pour la syntaxe moderne de requête
from app.utils import role_required
from datetime import datetime, timedelta
from flask_mail import Message
import random
import string

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ============================
# UTILS
# ============================

def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(email, code):
    msg = Message(
        subject="Votre code de vérification",
        recipients=[email],
        body=f"Votre code de vérification est : {code}"
    )
    mail.send(msg)


# ============================
# REGISTER
# ============================

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print(data)
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email et mot de passe requis."}), 400

    # Vérifier si l'utilisateur existe déjà
    stmt = select(User).filter_by(email=email)
    user = db.session.execute(stmt).scalars().first()
    if user and not user.is_verified and user.reset_token_expiration > datetime.utcnow():
        db.session.delete(user)
        db.session.commit()
    elif user:
        return jsonify({"msg": "L'utilisateur existe déjà."}), 409

    # Rôle par défaut
    default_role = db.session.execute(select(Role).filter_by(name='USER')).scalars().first()
    if not default_role:
        return jsonify({"msg": "Rôle 'USER' manquant. Initialisez la BDD."}), 500

    # Génération du code OTP AVANT création du user
    code = generate_verification_code()
    expiration = datetime.utcnow() + timedelta(minutes=10)

    # Tentative d'envoi de l'email AVANT création du compte
    try:
        send_verification_email(email, code)
    except Exception as e:
        return jsonify({"msg": "Erreur de connexion au serveur mail. Réessayez plus tard."}), 503

    # Création utilisateur SEULEMENT si email envoyé
    new_user = User(
        email=email,
        role_id=default_role.id,
        verification_token=code,
        reset_token_expiration=expiration
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Inscription réussie. Vérifiez votre email.", "user_id": new_user.id}), 201


# ============================
# VERIFY EMAIL
# ============================

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    user = db.session.execute(select(User).filter_by(email=email)).scalars().first()

    if not user:
        return jsonify({"msg": "Utilisateur introuvable."}), 404

    # Si le code a expiré → supprimer le compte
    if user.reset_token_expiration < datetime.utcnow():
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "Code expiré. Le compte a été supprimé. Veuillez vous réinscrire."}), 410

    if user.is_verified:
        return jsonify({"msg": "Email déjà vérifié."}), 400

    if user.verification_token != code:
        return jsonify({"msg": "Code incorrect."}), 400

    # Validation
    user.is_verified = True
    user.verification_token = None
    user.reset_token_expiration = None
    db.session.commit()

    return jsonify({"msg": "Email vérifié avec succès."}), 200


# ============================
# RESEND CODE
# ============================

@auth_bp.route('/resend-code', methods=['POST'])
def resend_code():
    data = request.get_json()
    email = data.get('email')

    user = db.session.execute(select(User).filter_by(email=email)).scalars().first()

    if not user:
        return jsonify({"msg": "Utilisateur introuvable."}), 404

    if user.is_verified:
        return jsonify({"msg": "Email déjà vérifié."}), 400

    # Nouveau code
    code = generate_verification_code()
    expiration = datetime.utcnow() + timedelta(minutes=10)

    # Tentative d'envoi
    try:
        send_verification_email(email, code)
    except Exception:
        return jsonify({"msg": "Erreur lors de l'envoi du mail."}), 503

    user.verification_token = code
    user.reset_token_expiration = expiration

    db.session.commit()

    return jsonify({"msg": "Nouveau code envoyé."}), 200


# ============================
# LOGIN
# ============================

@auth_bp.route('/login', methods=['POST'])

def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email et mot de passe requis."}), 400

    stmt = select(User).filter_by(email=email)
    user = db.session.execute(stmt).scalars().first()

    if not user or not user.check_password(password):
        return jsonify({"msg": "Email ou mot de passe invalide."}), 401

    if not user.is_verified:
        if user.reset_token_expiration < datetime.utcnow():
            db.session.delete(user)
            db.session.commit()
            return jsonify({"msg": "Compte non vérifié et code expiré. Le compte a été supprimé. Veuillez vous réinscrire."}), 410
        return jsonify({"msg": "Veuillez vérifier votre email avant de vous connecter."}), 403

    if not user.is_active:
        return jsonify({"msg": "Compte désactivé. Contactez l'administrateur."}), 403
    access_token = create_access_token(identity=str(user.id))

    user.last_connection_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role.name
        }
    }), 200

# ============================
# ROUTE PROTÉGÉE
# ============================

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return jsonify({"msg": "Utilisateur non trouvé."}), 404

    return jsonify({
        "msg": f"Accès autorisé pour l'utilisateur ID: {current_user_id}",
        "email": user.email,
        "role_id": user.role_id
    }), 200


# ============================
# ADMIN ONLY
# ============================

@auth_bp.route('/admin-only', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def admin_only_route():
    user_id = get_jwt_identity()
    return jsonify({
        "msg": f"Bienvenue Administrateur {user_id}",
        "resource": "Accès à la console d'administration."
    }), 200
