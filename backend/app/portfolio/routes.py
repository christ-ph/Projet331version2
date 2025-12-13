from app import db
from app.models import Portfolio, Profile
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select

portfolio_bp = Blueprint('portfolio', __name__)

# ============================
# UTILS
# ============================

def get_user_profile():
    user_id = int(get_jwt_identity())
    profile = db.session.execute(
        select(Profile).filter_by(user_id=user_id)
    ).scalars().first()
    return profile



# ============================
# PORTFOLIO ROUTES
# ============================

@portfolio_bp.get('/')
@jwt_required()
def get_portfolios():
    profile = get_user_profile()
    if not profile:
        return jsonify({"msg": "Profil introuvable"}), 404

    portfolios = profile.portfolios.all()

    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "url": p.url,
            "image_url": p.image_url,
            "created_at": p.created_at
        }
        for p in portfolios
    ]), 200



# ============================
# CREATE PORTFOLIO ITEM
# ============================

@portfolio_bp.post('/')
@jwt_required()
def create_portfolio():
    profile = get_user_profile()
    if not profile:
        return jsonify({"msg": "Profil introuvable"}), 404

    data = request.json

    new_item = Portfolio(
        title=data.get("title"),
        description=data.get("description"),
        url=data.get("url"),
        image_url=data.get("image_url"),
        profile_id=profile.id
    )

    db.session.add(new_item)
    db.session.commit()

    return jsonify({
        "msg": "Portfolio ajouté",
        "portfolio": {
            "id": new_item.id,
            "title": new_item.title,
            "description": new_item.description,
            "url": new_item.url,
            "image_url": new_item.image_url
        }
    }), 201


# ============================
# update_portfolio
# ============================

@portfolio_bp.put('/<int:portfolio_id>')
@jwt_required()
def update_portfolio(portfolio_id):
    profile = get_user_profile()
    if not profile:
        return jsonify({"msg": "Profil introuvable"}), 404

    item = db.session.execute(
        select(Portfolio).filter_by(id=portfolio_id, profile_id=profile.id)
    ).scalars().first()

    if not item:
        return jsonify({"msg": "Élément introuvable"}), 404

    data = request.json

    item.title = data.get("title", item.title)
    item.description = data.get("description", item.description)
    item.url = data.get("url", item.url)
    item.image_url = data.get("image_url", item.image_url)

    db.session.commit()

    return jsonify({"msg": "Portfolio mis à jour"}), 200


# ============================
# delete_portfolio
# ============================
@portfolio_bp.delete('/<int:portfolio_id>')
@jwt_required()
def delete_portfolio(portfolio_id):
    profile = get_user_profile()
    if not profile:
        return jsonify({"msg": "Profil introuvable"}), 404

    item = db.session.execute(
        select(Portfolio).filter_by(id=portfolio_id, profile_id=profile.id)
    ).scalars().first()

    if not item:
        return jsonify({"msg": "Élément introuvable"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({"msg": "Portfolio supprimé"}), 200