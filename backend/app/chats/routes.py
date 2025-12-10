from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Message, Mission, User
from sqlalchemy import select

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


# ---------------------------------------------------------
# ✅ Vérifier si l'utilisateur peut accéder au chat
# ---------------------------------------------------------
def user_can_access_chat(user_id, mission):
    """Retourne True si l'utilisateur est le client ou le freelance assigné."""
    return (
        mission.client_id == user_id or
        mission.assigned_freelance_id == user_id
    )


# ---------------------------------------------------------
# ✅ 1. Récupérer les messages d'une mission
# ---------------------------------------------------------
@chat_bp.route('/<int:mission_id>', methods=['GET'])
@jwt_required()
def get_messages(mission_id):
    user_id = int(get_jwt_identity())

    mission = db.session.get(Mission, mission_id)
    if not mission:
        return jsonify({"msg": "Mission introuvable"}), 404

    # Vérification des permissions
    if not user_can_access_chat(user_id, mission):
        return jsonify({"msg": "Accès refusé : vous n'êtes pas autorisé à voir ce chat"}), 403

    messages = db.session.execute(
        select(Message)
        .filter_by(mission_id=mission_id)
        .order_by(Message.timestamp.asc())
    ).scalars().all()

    return jsonify([m.to_dict() for m in messages]), 200


# ---------------------------------------------------------
# ✅ 2. Envoyer un message
# ---------------------------------------------------------
@chat_bp.route('/<int:mission_id>', methods=['POST'])
@jwt_required()
def send_message(mission_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    content = data.get("content")
    if not content:
        return jsonify({"msg": "Le message ne peut pas être vide"}), 400

    mission = db.session.get(Mission, mission_id)
    if not mission:
        return jsonify({"msg": "Mission introuvable"}), 404

    # Vérification des permissions
    if not user_can_access_chat(user_id, mission):
        return jsonify({"msg": "Accès refusé : vous n'êtes pas autorisé à envoyer un message"}), 403

    message = Message(
        mission_id=mission_id,
        sender_id=user_id,
        content=content
    )

    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict()), 201
