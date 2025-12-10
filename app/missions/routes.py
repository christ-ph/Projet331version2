from flask import Blueprint, request, jsonify
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Mission, Application, MissionStatus, User, ApplicationStatus, Profile
from app.utils import role_required
from sqlalchemy import select, and_

missions_bp = Blueprint('missions', __name__, url_prefix='/api/missions')


# ---------------------------------------------------------
# ✅ 1. CLIENT — Créer une mission
# ---------------------------------------------------------
@missions_bp.route('', methods=['POST'])
@jwt_required()
@role_required(['CLIENT'])
def create_mission():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    budget = data.get('budget')
    duration = data.get('duration')
    required_skills = data.get('required_skills')

    if not title:
        return jsonify({"msg": "Le titre est obligatoire"}), 400

    mission = Mission(
        client_id=user_id,
        title=title,
        description=description,
        budget=budget,
        duration=duration,
        required_skills=required_skills,
        status=MissionStatus.PUBLISHED
    )

    db.session.add(mission)
    db.session.commit()

    return jsonify({"msg": "Mission créée", "mission": mission.to_dict()}), 201


# ---------------------------------------------------------
# ✅ 2. CLIENT — Modifier une mission
# ---------------------------------------------------------
@missions_bp.route('/<int:mission_id>', methods=['PUT'])
@jwt_required()
@role_required(['CLIENT'])
def update_mission(mission_id):
    user_id = int(get_jwt_identity())
    mission = db.session.get(Mission, mission_id)

    if not mission:
        return jsonify({"msg": "Mission introuvable"}), 404

    if mission.client_id != user_id:
        return jsonify({"msg": "Accès refusé"}), 403

    data = request.get_json()

    mission.title = data.get('title', mission.title)
    mission.description = data.get('description', mission.description)
    mission.budget = data.get('budget', mission.budget)
    mission.duration = data.get('duration', mission.duration)
    mission.required_skills = data.get('required_skills', mission.required_skills)

    db.session.commit()

    return jsonify({"msg": "Mission mise à jour", "mission": mission.to_dict()}), 200


# ---------------------------------------------------------
# ✅ 3. CLIENT — Supprimer une mission
# ---------------------------------------------------------
@missions_bp.route('/<int:mission_id>', methods=['DELETE'])
@jwt_required()
@role_required(['CLIENT'])
def delete_mission(mission_id):
    user_id = int(get_jwt_identity())
    mission = db.session.get(Mission, mission_id)

    if not mission:
        return jsonify({"msg": "Mission introuvable"}), 404

    if mission.client_id != user_id:
        return jsonify({"msg": "Accès refusé"}), 403

    # On peut empêcher la suppression si une candidature ACCEPTÉE existe
    accepted = db.session.execute(
        select(Application).filter_by(mission_id=mission_id, status=ApplicationStatus.ACCEPTED)
    ).scalars().first()

    if accepted:
        return jsonify({"msg": "Impossible de supprimer : une candidature a été acceptée"}), 400

    db.session.delete(mission)
    db.session.commit()

    return jsonify({"msg": "Mission supprimée"}), 200


# ---------------------------------------------------------
# ✅ 4. CLIENT — Voir ses missions
# ---------------------------------------------------------
@missions_bp.route('/my', methods=['GET'])
@jwt_required()
@role_required(['CLIENT'])
def get_my_missions():
    user_id = int(get_jwt_identity())

    missions = db.session.execute(
        select(Mission).filter_by(client_id=user_id)
    ).scalars().all()

    return jsonify([m.to_dict() for m in missions]), 200


# ---------------------------------------------------------
# ✅ 5. FREELANCE — Voir les missions disponibles
# ---------------------------------------------------------
@missions_bp.route('/available', methods=['GET'])
@jwt_required()
@role_required(['FREELANCE'])
def get_available_missions():
    skills_filter = request.args.get('skills')

    stmt = select(Mission).filter(Mission.status == MissionStatus.PUBLISHED)

    if skills_filter:
        stmt = stmt.filter(Mission.required_skills.ilike(f"%{skills_filter}%"))

    missions = db.session.execute(stmt).scalars().all()

    return jsonify([m.to_dict() for m in missions]), 200


# ---------------------------------------------------------
# ✅ 6. FREELANCE — Détails d’une mission
# ---------------------------------------------------------
@missions_bp.route('/<int:mission_id>', methods=['GET'])
@jwt_required()
def get_mission_details(mission_id):
    mission = db.session.get(Mission, mission_id)

    if not mission:
        return jsonify({"msg": "Mission introuvable"}), 404

    return jsonify(mission.to_dict()), 200


# ---------------------------------------------------------
# ✅ 7. FREELANCE — Postuler à une mission
# ---------------------------------------------------------
@missions_bp.route('/apply', methods=['POST'])
@jwt_required()
@role_required(['FREELANCE'])
def apply_to_mission():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    mission_id = data.get('mission_id')
    proposal = data.get('proposal')
    proposed_budget = data.get('proposed_budget')

    mission = db.session.get(Mission, mission_id)

    if not mission:
        return jsonify({"msg": "Mission introuvable"}), 404

    # Vérifier si déjà postulé
    existing = db.session.execute(
        select(Application).filter_by(mission_id=mission_id, freelance_id=user_id)
    ).scalars().first()

    if existing:
        return jsonify({"msg": "Vous avez déjà postulé à cette mission"}), 400

    application = Application(
        mission_id=mission_id,
        freelance_id=user_id,
        proposal=proposal,
        proposed_budget=proposed_budget,
        status=ApplicationStatus.PENDING
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({"msg": "Candidature envoyée"}), 201


# ---------------------------------------------------------
# ✅ 8. FREELANCE — Voir ses candidatures
# ---------------------------------------------------------
@missions_bp.route('/applications/my', methods=['GET'])
@jwt_required()
@role_required(['FREELANCE'])
def get_my_applications():
    user_id = int(get_jwt_identity())

    apps = db.session.execute(
        select(Application).filter_by(freelance_id=user_id)
    ).scalars().all()

    return jsonify([a.to_dict() for a in apps]), 200


# ---------------------------------------------------------
# ✅ 9. CLIENT — Voir les candidatures reçues pour une mission
# ---------------------------------------------------------
@missions_bp.route('/<int:mission_id>/applications', methods=['GET'])
@jwt_required()
@role_required(['CLIENT'])
def get_mission_applications(mission_id):
    user_id = int(get_jwt_identity())
    mission = db.session.get(Mission, mission_id)

    if not mission:
        return jsonify({"msg": "Mission introuvable"}), 404

    if mission.client_id != user_id:
        return jsonify({"msg": "Accès refusé"}), 403

    apps = db.session.execute(
        select(Application).filter_by(mission_id=mission_id)
    ).scalars().all()

    return jsonify([a.to_dict() for a in apps]), 200


# ---------------------------------------------------------
# ✅ 10. CLIENT — Accepter une candidature
# ---------------------------------------------------------
@missions_bp.route('/applications/<int:app_id>/accept', methods=['PUT'])
@jwt_required()
@role_required(['CLIENT'])
def accept_application(app_id):
    user_id = int(get_jwt_identity())
    app = db.session.get(Application, app_id)

    if not app:
        return jsonify({"msg": "Candidature introuvable"}), 404

    mission = app.mission

    if mission.client_id != user_id:
        return jsonify({"msg": "Accès refusé"}), 403

    app.status = ApplicationStatus.ACCEPTED
    mission.status = MissionStatus.CLOSED

    db.session.commit()

    return jsonify({"msg": "Candidature acceptée"}), 200


# ---------------------------------------------------------
# ✅ 11. CLIENT — Refuser une candidature
# ---------------------------------------------------------
@missions_bp.route('/applications/<int:app_id>/reject', methods=['PUT'])
@jwt_required()
@role_required(['CLIENT'])
def reject_application(app_id):
    user_id = int(get_jwt_identity())
    app = db.session.get(Application, app_id)

    if not app:
        return jsonify({"msg": "Candidature introuvable"}), 404

    mission = app.mission

    if mission.client_id != user_id:
        return jsonify({"msg": "Accès refusé"}), 403

    app.status = ApplicationStatus.REJECTED

    db.session.commit()

    return jsonify({"msg": "Candidature rejetée"}), 200
