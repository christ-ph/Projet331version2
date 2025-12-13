from flask import Blueprint, request, jsonify
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    Profile,
    FreelanceProfile,
    ClientProfile,
    Portfolio,
    Role,
    User
)
from sqlalchemy import select

profile_bp = Blueprint('profiles', __name__)


# ============================================================
# ✅ A. CRÉATION / MISE À JOUR DU PROFIL (Freelance ou Client)
# ============================================================

@profile_bp.route('/', methods=['POST', 'PUT'])
@jwt_required()
def manage_profile():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "Utilisateur introuvable"}), 404

    profile = user.profile  # relation OneToOne

    profile_type = data.get("type")  # "freelance" ou "client"
    if profile_type not in ["freelance", "client"]:
        return jsonify({"msg": "Type de profil invalide"}), 400

    # ✅ MISE À JOUR
    if profile:
        if profile_type == "freelance":
            if not isinstance(profile, FreelanceProfile):
                return jsonify({"msg": "Impossible de changer le type d'un profil existant"}), 400

            profile.full_name = data.get("full_name")
            profile.title = data.get("title")
            profile.description = data.get("description")
            profile.skills = data.get("skills")
            profile.languages = data.get("languages")
            profile.hourly_rate = data.get("hourly_rate")
            profile.experience_years = data.get("experience_years")
            profile.availability = data.get("availability")

        else:  # client
            if not isinstance(profile, ClientProfile):
                return jsonify({"msg": "Impossible de changer le type d'un profil existant"}), 400

            profile.client_type = data.get("client_type")
            profile.fullname = data.get("fullname")
            profile.company_name = data.get("company_name")
            profile.company_website = data.get("company_website")
            profile.industry = data.get("industry")

        db.session.commit()
        return jsonify({"msg": "Profil mis à jour"}), 200

    # ✅ CRÉATION
    if profile_type == "freelance":
        new_profile = FreelanceProfile(
            user_id=user_id,
            full_name=data.get("full_name"),
            title=data.get("title"),
            description=data.get("description"),
            skills=data.get("skills"),
            languages=data.get("languages"),
            hourly_rate=data.get("hourly_rate"),
            experience_years=data.get("experience_years"),
            availability=data.get("availability")
        )
        role = db.session.execute(select(Role).filter_by(name="FREELANCE")).scalars().first()

    else:  # client
        new_profile = ClientProfile(
            user_id=user_id,
            client_type=data.get("client_type"),
            fullname=data.get("fullname"),
            company_name=data.get("company_name"),
            company_website=data.get("company_website"),
            industry=data.get("industry")
        )
        role = db.session.execute(select(Role).filter_by(name="CLIENT")).scalars().first()

    user.role = role
    db.session.add(new_profile)
    db.session.commit()

    return jsonify({"msg": "Profil créé"}), 201


# ============================================================
# ✅ B. CONSULTER UN PROFIL
# ============================================================

@profile_bp.route('/<int:profile_id>', methods=['GET'])
@jwt_required()
def get_profile(profile_id):
    profile = db.session.get(Profile, profile_id)
    if not profile:
        return jsonify({"msg": "Profil introuvable"}), 404

    base = {
        "id": profile.id,
        "user_id": profile.user_id,
        "email": profile.user.email,
        "phone": profile.phone,
        "country": profile.country,
        "city": profile.city,
        "address": profile.address,
        "bio": profile.bio,
        "url_photo": profile.url_photo,
        "type": profile.type,
        "portfolio": [p.to_dict() for p in profile.portfolios]
    }

    if profile.type == "freelance":
        base.update({
            "full_name": profile.full_name,
            "title": profile.title,
            "description": profile.description,
            "skills": profile.skills,
            "languages": profile.languages,
            "hourly_rate": profile.hourly_rate,
            "experience_years": profile.experience_years,
            "availability": profile.availability,
            "rating": profile.rating,
            "completed_projects": profile.completed_projects
        })

    else:
        base.update({
            "client_type": profile.client_type,
            "fullname": profile.fullname,
            "company_name": profile.company_name,
            "company_website": profile.company_website,
            "industry": profile.industry
        })

    return jsonify(base), 200


# ============================================================
# ✅ C. LISTE DES FREELANCES (pour recherche)
# ============================================================

@profile_bp.route('/', methods=['GET'])
def list_all_profiles():
    profiles = db.session.execute(select(FreelanceProfile)).scalars().all()

    return jsonify([
        {
            "id": p.id,
            "full_name": p.full_name,
            "title": p.title,
            "skills": p.skills,
            "rating": p.rating
        }
        for p in profiles
    ]), 200


# ============================================================
# ✅ D. PORTFOLIO — LISTE + AJOUT
# ============================================================

@profile_bp.route('/<int:profile_id>/portfolio', methods=['GET', 'POST'])
@jwt_required()
def manage_portfolio_list(profile_id):
    user_id = int(get_jwt_identity())
    profile = db.session.get(Profile, profile_id)

    if not profile or profile.user_id != user_id:
        return jsonify({"msg": "Accès refusé ou Profil non trouvé."}), 403

    if request.method == 'GET':
        items = db.session.execute(
            select(Portfolio).filter_by(profile_id=profile_id)
        ).scalars().all()

        return jsonify([item.to_dict() for item in items]), 200

    data = request.get_json()
    title = data.get("title")

    if not title:
        return jsonify({"msg": "Le titre est requis."}), 400

    new_item = Portfolio(
        profile_id=profile_id,
        title=title,
        description=data.get("description"),
        url=data.get("url"),
        image_url=data.get("image_url")
    )

    db.session.add(new_item)
    db.session.commit()

    return jsonify({"msg": "Élément ajouté.", "item": new_item.to_dict()}), 201


# ============================================================
# ✅ E. PORTFOLIO — GET / UPDATE / DELETE
# ============================================================

@profile_bp.route('/<int:profile_id>/portfolio/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_portfolio_item(profile_id, item_id):
    user_id = int(get_jwt_identity())

    item = db.session.execute(
        select(Portfolio).filter_by(id=item_id, profile_id=profile_id)
    ).scalars().first()

    if not item:
        return jsonify({"msg": "Élément introuvable."}), 404

    if item.profile.user_id != user_id:
        return jsonify({"msg": "Accès refusé."}), 403

    if request.method == 'GET':
        return jsonify(item.to_dict()), 200

    if request.method == 'PUT':
        data = request.get_json()
        item.title = data.get("title", item.title)
        item.description = data.get("description", item.description)
        item.url = data.get("url", item.url)
        item.image_url = data.get("image_url", item.image_url)

        db.session.commit()
        return jsonify({"msg": "Élément mis à jour.", "item": item.to_dict()}), 200

    db.session.delete(item)
    db.session.commit()
    return jsonify({"msg": "Élément supprimé."}), 200


@profile_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    user_id = int(get_jwt_identity())
    profile = db.session.execute(
        select(Profile).filter_by(user_id=user_id)
    ).scalars().first()

    if not profile:
        return jsonify({"msg": "Profil introuvable"}), 404

    return get_profile(profile.id)  # ✅ Réutilise la logique existante
