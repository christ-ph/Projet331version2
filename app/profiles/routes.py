from flask import Blueprint, request, jsonify
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Profile, Role, User, PortfolioItem
from app.utils import role_required
from sqlalchemy import select


# definition du blue print
# (Le préfixe '/api/profiles' est défini dans app/__init__.py)
profile_bp = Blueprint('profiles', __name__)

# ----------------------------------------------------
# A. LOGIQUE EXISTANTE : Création/Mise à jour de Profile et Consultation
# ----------------------------------------------------

# Création/Mise à jour du profile (votre code existant)
@profile_bp.route('/', methods=['POST', 'PUT'])
@jwt_required()
def manage_profile():
    user_id = get_jwt_identity()
    data = request.get_json()

    # ... [Votre logique de manage_profile() est conservée ici] ...
    # Votre logique de mise à jour/création est correcte.

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    bio = data.get('bio')
    skills = data.get('skills')
    is_freelancer = data.get('is_freelancer', False)


    # chercher un profile existant 
    profile = db.session.execute(
        select(Profile).filter_by(user_id=user_id)
    ).scalars().first()

    if profile:
        # mise a jour
        profile.first_name = first_name
        profile.last_name = last_name
        profile.full_name = f"{first_name} {last_name}"
        profile.bio = bio
        profile.skills = skills
        profile.is_freelancer = is_freelancer
        db.session.commit()
        return jsonify({'msg': 'Profile updated successfully'}), 200
    else:
        # creation
        if not first_name:
            return jsonify({'msg': 'First name is required for profile creation'}), 400
        new_profile = Profile(
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            skills=skills,
            is_freelancer=is_freelancer,
        )
        role_name = "FREELANCE" if is_freelancer else "CLIENT"

        role = db.session.execute(
            select(Role).filter_by(name=role_name)
        ).scalars().first()

        
        user = db.session.get(User, user_id)
        new_profile.user = user
        user.role = role
        db.session.add(new_profile)
        db.session.commit()
        return jsonify({'msg': 'Profile created successfully'}), 201


# Consultation d'un profile spécifique (votre code existant)
@profile_bp.route('/<int:profile_id>', methods=['GET'])
@jwt_required()
def get_profile(profile_id):
    profile = db.session.get(Profile, profile_id)
    if not profile:
        return jsonify({'msg': 'Profile not found'}), 404

    # Sérialisation du profil (à compléter si nécessaire)
    profile_data = {
        'id_profile': profile.id,
        'user_id': profile.user_id,
        'email': profile.user.email,
        'first_name': profile.first_name,
        'last_name': profile.last_name,
        'bio': profile.bio,
        'skills': profile.skills,
        'is_freelancer': profile.is_freelancer,
        'portfolio': [item.to_dict() for item in profile.portfolio_items] # Inclure le portfolio
    }
    return jsonify(profile_data), 200

# ----------------------------------------------------
# B. NOUVELLE LOGIQUE : Lister tous les profils (Ancienne FreelanceListResource)
# ----------------------------------------------------

@profile_bp.route('/', methods=['GET'])
def list_all_profiles():
    """Lister tous les profils (pour la recherche)"""
    # On peut limiter à is_freelancer=True pour l'affichage de la liste des talents
    profiles = db.session.execute(
        select(Profile).filter_by(is_freelancer=True)
    ).scalars().all()
    
    profiles_data = []
    for profile in profiles:
        profiles_data.append({
            'id_profile': profile.id,
            'user_id': profile.user_id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'skills': profile.skills,
            # Ajoutez ici les champs pertinents pour la liste
        })
    return jsonify(profiles_data), 200

# ----------------------------------------------------
# C. NOUVELLE LOGIQUE : Gestion du Portfolio (Ancienne PortfolioListResource)
# ----------------------------------------------------

@profile_bp.route('/<int:profile_id>/portfolio', methods=['GET', 'POST'])
@jwt_required()
def manage_portfolio_list(profile_id):
    """Gérer la liste du portfolio (GET: liste, POST: ajout)"""
    user_id = get_jwt_identity()
    profile = db.session.get(Profile, profile_id)
    
    # Vérification de sécurité: l'utilisateur doit être propriétaire du profil
    if not profile or str(profile.user_id) != user_id:
        return jsonify({"msg": "Accès refusé ou Profil non trouvé."}), 403
    
    if request.method == 'GET':
        # Lister le portfolio
        portfolio_items = db.session.execute(
            select(PortfolioItem).filter_by(profile_id=profile_id)
        ).scalars().all()
        
        items_data = [item.to_dict() for item in portfolio_items]
        return jsonify(items_data), 200

    elif request.method == 'POST':
        # Ajouter un élément au portfolio
        data = request.get_json()
        title = data.get('title')
        # ... validation des données (omise pour concision)
        
        if not title:
            return jsonify({"msg": "Le titre est requis pour un élément du portfolio."}), 400
        
        new_item = PortfolioItem(
            profile_id=profile_id,
            title=title,
            description=data.get('description'),
            project_url=data.get('project_url'),
            image_url=data.get('image_url')
        )
        db.session.add(new_item)
        db.session.commit()
        
        return jsonify({"msg": "Élément de portfolio créé.", "item": new_item.to_dict()}), 201

# ----------------------------------------------------
# D. NOUVELLE LOGIQUE : Gestion d'un Élément de Portfolio Spécifique (Ancienne PortfolioItemResource)
# ----------------------------------------------------

@profile_bp.route('/<int:profile_id>/portfolio/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_portfolio_item(profile_id, item_id):
    """Gérer un élément spécifique du portfolio (GET, PUT, DELETE)"""
    user_id = get_jwt_identity()
    
    # Trouver l'élément et s'assurer qu'il appartient bien au profil
    item = db.session.execute(
        select(PortfolioItem)
        .filter_by(id=item_id, profile_id=profile_id)
    ).scalars().first()

    if not item:
        return jsonify({"msg": "Élément de portfolio non trouvé."}), 404

    # Sécurité: S'assurer que le propriétaire du profil est l'utilisateur authentifié
    if str(item.profile.user_id) != user_id:
        return jsonify({"msg": "Accès refusé: Vous n'êtes pas le propriétaire."}), 403
    
    if request.method == 'GET':
        return jsonify(item.to_dict()), 200

    elif request.method == 'PUT':
        data = request.get_json()
        item.title = data.get('title', item.title)
        item.description = data.get('description', item.description)
        item.project_url = data.get('project_url', item.project_url)
        item.image_url = data.get('image_url', item.image_url)
        
        db.session.commit()
        return jsonify({"msg": "Élément de portfolio mis à jour.", "item": item.to_dict()}), 200

    elif request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify({"msg": "Élément de portfolio supprimé."}), 200