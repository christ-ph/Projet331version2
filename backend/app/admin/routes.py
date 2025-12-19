from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.models import (
    db, User, Role, ActionAccount, AdminAction, 
    ComplaintStatus, AdminActionType
)
from app.utils import role_required
from datetime import datetime
from sqlalchemy import or_

admin_bp = Blueprint('admin', __name__)

# ============================
# GESTION DES ADMINS
# ============================

@admin_bp.route('/register', methods=['POST'])
def register_admin():
    """Créer un compte admin (à protéger en production)"""
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"msg": "Email et mot de passe requis"}), 400
    
    # Vérifier si l'utilisateur existe déjà
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Cet email est déjà utilisé"}), 409
    
    # Récupérer le rôle ADMIN
    admin_role = Role.query.filter_by(name='ADMIN').first()
    if not admin_role:
        return jsonify({"msg": "Rôle ADMIN non trouvé. Initialisez la base de données."}), 500
    
    # Créer l'admin
    new_admin = User(
        email=email,
        role_id=admin_role.id,
        is_verified=True,  # Admin vérifié par défaut
        is_active=True
    )
    new_admin.set_password(password)
    
    db.session.add(new_admin)
    db.session.commit()
    
    return jsonify({
        "msg": "Admin créé avec succès",
        "admin": {
            "id": new_admin.id,
            "email": new_admin.email,
            "role": admin_role.name
        }
    }), 201

@admin_bp.route('/login', methods=['POST'])
def login_admin():
    """Connexion admin"""
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"msg": "Email et mot de passe requis"}), 400
    
    # Trouver l'utilisateur
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({"msg": "Email ou mot de passe incorrect"}), 401
    
    # Vérifier le rôle ADMIN
    if user.role.name != 'ADMIN':
        return jsonify({"msg": "Accès réservé aux administrateurs"}), 403
    
    # Créer le token
    access_token = create_access_token(identity=str(user.id))
    
    # Mettre à jour last_connection_at
    user.last_connection_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        "msg": "Connexion réussie",
        "access_token": access_token,
        "admin": {
            "id": user.id,
            "email": user.email,
            "role": user.role.name
        }
    }), 200

# ============================
# ROUTES POUR FORMULER DES PLAINTES (CLIENT/FREELANCE)
# ============================

@admin_bp.route('/complaint', methods=['POST'])
@jwt_required()
@role_required(['CLIENT', 'FREELANCE','USER'])
def create_complaint():
    """Créer une plainte"""
    data = request.get_json()
    
    reported_email = data.get('reported_email')
    reason = data.get('reason')
    
    if not reported_email or not reason:
        return jsonify({"msg": "Email signalé et motif requis"}), 400
    
    # Vérifier que l'email signalé existe
    reported_user = User.query.filter_by(email=reported_email).first()
    if not reported_user:
        return jsonify({"msg": "L'email signalé n'existe pas dans notre système"}), 404
    
    # Vérifier qu'on ne se signale pas soi-même
    current_user = g.current_user
    if current_user.email == reported_email:
        return jsonify({"msg": "Vous ne pouvez pas vous signaler vous-même"}), 400
    
    # Créer la plainte
    complaint = ActionAccount(
        plaintiff_id=current_user.id,
        reported_email=reported_email,
        reason=reason,
        status=ComplaintStatus.PENDING
    )
    
    db.session.add(complaint)
    db.session.commit()
    
    return jsonify({
        "msg": "Plainte enregistrée avec succès. Notre équipe va l'examiner.",
        "complaint": complaint.to_dict()
    }), 201

@admin_bp.route('/my-complaints', methods=['GET'])
@jwt_required()
@role_required(['CLIENT', 'FREELANCE'])
def get_my_complaints():
    """Récupérer mes plaintes"""
    current_user = g.current_user
    
    complaints = ActionAccount.query.filter_by(plaintiff_id=current_user.id).order_by(
        ActionAccount.created_at.desc()
    ).all()
    
    return jsonify({
        "complaints": [c.to_dict() for c in complaints],
        "total": len(complaints)
    }), 200

# ============================
# ROUTES ADMIN POUR GÉRER LES PLAINTES
# ============================

@admin_bp.route('/complaints', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def get_all_complaints():
    """Récupérer toutes les plaintes (avec filtre optionnel)"""
    status_filter = request.args.get('status')  # pending, approved, rejected
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = ActionAccount.query
    
    # Filtrer par status si fourni
    if status_filter:
        try:
            status_enum = ComplaintStatus[status_filter.upper()]
            query = query.filter_by(status=status_enum)
        except KeyError:
            return jsonify({"msg": "Status invalide"}), 400
    
    # Pagination
    paginated = query.order_by(ActionAccount.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        "complaints": [c.to_dict() for c in paginated.items],
        "total": paginated.total,
        "page": page,
        "per_page": per_page,
        "pages": paginated.pages
    }), 200

@admin_bp.route('/complaints/<int:complaint_id>/approve', methods=['POST'])
@jwt_required()
@role_required('ADMIN')
def approve_complaint(complaint_id):
    """Approuver une plainte et bloquer l'utilisateur signalé"""
    complaint = db.session.get(ActionAccount, complaint_id)
    
    if not complaint:
        return jsonify({"msg": "Plainte non trouvée"}), 404
    
    if complaint.status != ComplaintStatus.PENDING:
        return jsonify({"msg": "Cette plainte a déjà été traitée"}), 400
    
    # Trouver l'utilisateur signalé
    reported_user = User.query.filter_by(email=complaint.reported_email).first()
    if not reported_user:
        return jsonify({"msg": "Utilisateur signalé non trouvé"}), 404
    
    # Bloquer l'utilisateur
    reported_user.is_active = False
    db.session.commit()
    # Mettre à jour la plainte
    current_admin = g.current_user
    complaint.status = ComplaintStatus.APPROVED
    complaint.reviewed_by = current_admin.id
    complaint.reviewed_at = datetime.utcnow()
    
    # Créer l'historique admin (approuver plainte)
    action_approve = AdminAction(
        admin_id=current_admin.id,
        action_type=AdminActionType.APPROVE_COMPLAINT,
        target_user_id=reported_user.id,
        action_account_id=complaint.id,
        notes=f"Plainte approuvée. Utilisateur {reported_user.email} bloqué."
    )
    
    # Créer l'historique admin (bloquer utilisateur)
    action_block = AdminAction(
        admin_id=current_admin.id,
        action_type=AdminActionType.BLOCK_USER,
        target_user_id=reported_user.id,
        action_account_id=complaint.id,
        notes=f"Compte bloqué suite à la plainte #{complaint.id}"
    )
    
    db.session.add(action_approve)
    db.session.add(action_block)
    db.session.commit()
    
    return jsonify({
        "msg": f"Plainte approuvée. L'utilisateur {reported_user.email} a été bloqué.",
        "complaint": complaint.to_dict(),
        "blocked_user": {
            "id": reported_user.id,
            "email": reported_user.email,
            "is_active": reported_user.is_active
        }
    }), 200

@admin_bp.route('/complaints/<int:complaint_id>/reject', methods=['POST'])
@jwt_required()
@role_required('ADMIN')
def reject_complaint(complaint_id):
    """Rejeter une plainte"""
    data = request.get_json() or {}
    notes = data.get('notes', 'Plainte rejetée par l\'administrateur')
    
    complaint = db.session.get(ActionAccount, complaint_id)
    
    if not complaint:
        return jsonify({"msg": "Plainte non trouvée"}), 404
    
    if complaint.status != ComplaintStatus.PENDING:
        return jsonify({"msg": "Cette plainte a déjà été traitée"}), 400
    
    # Mettre à jour la plainte
    current_admin = g.current_user
    complaint.status = ComplaintStatus.REJECTED
    complaint.reviewed_by = current_admin.id
    complaint.reviewed_at = datetime.utcnow()
    
    # Créer l'historique admin
    action = AdminAction(
        admin_id=current_admin.id,
        action_type=AdminActionType.REJECT_COMPLAINT,
        action_account_id=complaint.id,
        notes=notes
    )
    
    db.session.add(action)
    db.session.commit()
    
    return jsonify({
        "msg": "Plainte rejetée",
        "complaint": complaint.to_dict()
    }), 200

@admin_bp.route('/complaints/<int:complaint_id>', methods=['DELETE'])
@jwt_required()
@role_required('ADMIN')
def delete_complaint(complaint_id):
    """Supprimer une plainte"""
    complaint = db.session.get(ActionAccount, complaint_id)
    
    if not complaint:
        return jsonify({"msg": "Plainte non trouvée"}), 404
    
    db.session.delete(complaint)
    db.session.commit()
    
    return jsonify({"msg": "Plainte supprimée avec succès"}), 200

# ============================
# GESTION DES COMPTES BLOQUÉS
# ============================

@admin_bp.route('/blocked-accounts', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def get_blocked_accounts():
    """Récupérer tous les comptes bloqués"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    blocked_users = User.query.filter_by(is_active=False).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users_data = []
    for user in blocked_users.items:
        users_data.append({
            'id': user.id,
            'email': user.email,
            'role': user.role.name,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'is_active': user.is_active
        })
    
    return jsonify({
        "blocked_accounts": users_data,
        "total": blocked_users.total,
        "page": page,
        "per_page": per_page,
        "pages": blocked_users.pages
    }), 200

@admin_bp.route('/unblock/<int:user_id>', methods=['POST'])
@jwt_required()
@role_required('ADMIN')
def unblock_user(user_id):
    """Débloquer un compte utilisateur"""
    data = request.get_json() or {}
    notes = data.get('notes', 'Compte débloqué par l\'administrateur')
    
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404
    
    if user.is_active:
        return jsonify({"msg": "Ce compte n'est pas bloqué"}), 400
    
    # Débloquer l'utilisateur
    user.is_active = True
    
    # Créer l'historique admin
    current_admin = g.current_user
    action = AdminAction(
        admin_id=current_admin.id,
        action_type=AdminActionType.UNBLOCK_USER,
        target_user_id=user.id,
        notes=notes
    )
    
    db.session.add(action)
    db.session.commit()
    
    return jsonify({
        "msg": f"Compte {user.email} débloqué avec succès",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active
        }
    }), 200

# ============================
# HISTORIQUE DES ACTIONS ADMIN
# ============================

@admin_bp.route('/actions', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def get_all_admin_actions():
    """Récupérer toutes les actions admin (avec filtres optionnels)"""
    admin_id_filter = request.args.get('admin_id', type=int)
    action_type_filter = request.args.get('action_type')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    query = AdminAction.query
    
    # Filtrer par admin_id si fourni
    if admin_id_filter:
        query = query.filter_by(admin_id=admin_id_filter)
    
    # Filtrer par action_type si fourni
    if action_type_filter:
        try:
            action_enum = AdminActionType[action_type_filter.upper()]
            query = query.filter_by(action_type=action_enum)
        except KeyError:
            return jsonify({"msg": "Type d'action invalide"}), 400
    
    # Pagination
    paginated = query.order_by(AdminAction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        "actions": [a.to_dict() for a in paginated.items],
        "total": paginated.total,
        "page": page,
        "per_page": per_page,
        "pages": paginated.pages
    }), 200

@admin_bp.route('/actions/me', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def get_my_admin_actions():
    """Récupérer mes actions admin"""
    current_admin = g.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    paginated = AdminAction.query.filter_by(admin_id=current_admin.id).order_by(
        AdminAction.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "actions": [a.to_dict() for a in paginated.items],
        "total": paginated.total,
        "page": page,
        "per_page": per_page,
        "pages": paginated.pages
    }), 200