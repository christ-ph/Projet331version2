import json
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid

from app import db
from app.models import Mission, Deliverable, DeliverableStatus, User, MissionStatus, PostulationStatus, Postulation, FreelanceProfile, ClientProfile
from app.utils import role_required

deliverables_bp = Blueprint('deliverables_bp', __name__)

# ============================
# CONFIGURATION UPLOAD
# ============================

ALLOWED_EXTENSIONS = {
    'pdf','doc','docx','txt','rtf','odt','pages','ppt','pptx','odp','key','xls','xlsx','ods','csv',
    'jpg','jpeg','png','gif','bmp','tiff','tif','svg','webp','ico','psd','ai','mp4','avi','mov','wmv','flv','mkv','webm','m4v','mpg','mpeg','3gp',
    'mp3','wav','aac','flac','ogg','m4a','wma','zip','rar','7z','tar','gz','bz2','html','css','js','py','java','cpp','c','cs','php','rb','go','rs','json','xml','yml','yaml','sql','psd','ai','xd','fig','sketch','indd'
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_folder():
    base_dir = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'uploads'))
    upload_folder = os.path.join(base_dir, 'deliverables')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def save_deliverable_file(file):
    if not file or file.filename == '':
        return None

    file_data = file.read()
    file_size = len(file_data)
    file.seek(0)

    if file_size == 0 or file_size > MAX_FILE_SIZE or not allowed_file(file.filename):
        return None

    original_filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{original_filename}"
    file_path = os.path.join(get_upload_folder(), unique_filename)

    try:
        file.save(file_path)
        return unique_filename
    except Exception as e:
        current_app.logger.error(f"Erreur sauvegarde fichier: {str(e)}")
        return None


def delete_physical_file(filename):
    if not filename:
        return False
    try:
        file_path = os.path.join(get_upload_folder(), filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        current_app.logger.error(f"Erreur suppression fichier: {str(e)}")
    return False


# ============================
# UTILITAIRES
# ============================

def get_current_user():
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(user_id)


def deliverable_to_dict(deliverable):
    if not deliverable:
        return None

    file_url = f"/api/deliverables/{deliverable.id}/download" if deliverable.file_url else None

    result = {
        'id': deliverable.id,
        'title': deliverable.title,
        'description': deliverable.description,
        'file_url': file_url,
        'status': deliverable.status.value if deliverable.status else None,
        'client_feedback': deliverable.client_feedback,
        'mission_id': deliverable.mission_id,
        'submitted_by': deliverable.submitted_by,
        'reviewed_by': deliverable.reviewed_by,
        'accepted_by': deliverable.accepted_by
    }

    for attr in ['created_at','submitted_at','reviewed_at','accepted_at']:
        if getattr(deliverable, attr):
            result[attr] = getattr(deliverable, attr).isoformat()

    if deliverable.mission:
        result['mission_title'] = deliverable.mission.title

    if deliverable.submitted_by:
        freelance_user = User.query.get(deliverable.submitted_by)
        if freelance_user and freelance_user.profile:
            if isinstance(freelance_user.profile, FreelanceProfile):
                result['freelance_name'] = freelance_user.profile.full_name
            elif hasattr(freelance_user.profile, 'fullname'):
                result['freelance_name'] = freelance_user.profile.fullname

    return result


def check_freelance_permission(deliverable, user):
    return deliverable and user and user.profile and getattr(user.profile, 'type', None) == 'freelance' and deliverable.submitted_by == user.id


def check_client_permission(deliverable, user):
    return deliverable and user and user.profile and getattr(user.profile, 'type', None) == 'client' and Mission.query.get(deliverable.mission_id).client_id == user.id


def is_user_assigned_to_mission(user, mission_id):
    if not user or not user.profile or getattr(user.profile, 'type', None) != 'freelance':
        return False
    return Postulation.query.filter_by(mission_id=mission_id, freelance_id=user.id, status=PostulationStatus.ACCEPTED).first() is not None

# ============================
# ROUTE CREATION LIVRABLE
# ============================

@deliverables_bp.route('', methods=['POST'])
@jwt_required()
@role_required('FREELANCE')
def create_deliverable():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401

    mission_id = request.form.get('mission_id', '').strip()
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()

    if not mission_id or not title:
        return jsonify({'error': 'Mission ID et titre requis'}), 422

    try:
        mission_id = int(mission_id)
    except ValueError:
        return jsonify({'error': 'Mission ID invalide'}), 422

    mission = Mission.query.get(mission_id)
    if not mission:
        return jsonify({'error': 'Mission non trouvée'}), 404

    if mission.status != MissionStatus.IN_PROGRESS:
        return jsonify({'error': f'Mission non en cours (statut: {mission.status.value})'}), 400

    if not is_user_assigned_to_mission(current_user, mission_id):
        return jsonify({'error': 'Vous n\'êtes pas assigné à cette mission'}), 403

    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'Fichier requis'}), 422

    filename = save_deliverable_file(file)
    if not filename:
        return jsonify({'error': 'Type de fichier non autorisé ou fichier trop volumineux (max 50MB)'}), 422

    try:
        deliverable = Deliverable(
            title=title,
            description=description,
            file_url=filename,
            mission_id=mission_id,
            submitted_by=current_user.id,
            status=DeliverableStatus.DRAFT,
            created_at=datetime.now()
        )
        db.session.add(deliverable)
        db.session.commit()

        return jsonify({'message': 'Livrable créé avec succès','deliverable': deliverable_to_dict(deliverable)}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur création livrable: {str(e)}")
        return jsonify({'error': 'Erreur lors de la création'}), 500

    

@deliverables_bp.route('/<int:deliverable_id>', methods=['PUT'])
@jwt_required()
@role_required('FREELANCE')
def update_deliverable(deliverable_id):
    """Modifier un livrable."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    deliverable = Deliverable.query.get_or_404(deliverable_id)
    
    if not check_freelance_permission(deliverable, current_user):
        return jsonify({'error': 'Non autorisé'}), 403
    
    if deliverable.status not in [DeliverableStatus.DRAFT, DeliverableStatus.NEEDS_REVISION]:
        return jsonify({'error': 'Seuls les brouillons ou livrables nécessitant révision peuvent être modifiés'}), 400
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        return jsonify({'error': 'Titre requis'}), 400
    
    deliverable.title = title
    deliverable.description = description
    
    file = request.files.get('file')
    if file and file.filename != '':
        if deliverable.file_url:
            delete_physical_file(deliverable.file_url)
        
        filename = save_deliverable_file(file)
        if not filename:
            return jsonify({'error': 'Type de fichier non autorisé ou fichier trop volumineux'}), 400
        
        deliverable.file_url = filename
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Livrable modifié',
            'deliverable': deliverable_to_dict(deliverable)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur modification'}), 500

@deliverables_bp.route('/<int:deliverable_id>', methods=['DELETE'])
@jwt_required()
@role_required('FREELANCE')
def delete_deliverable(deliverable_id):
    """Supprimer un livrable."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    deliverable = Deliverable.query.get_or_404(deliverable_id)
    
    if not check_freelance_permission(deliverable, current_user):
        return jsonify({'error': 'Non autorisé'}), 403
    
    if deliverable.status != DeliverableStatus.DRAFT:
        return jsonify({'error': 'Seuls les brouillons peuvent être supprimés'}), 400
    
    try:
        if deliverable.file_url:
            delete_physical_file(deliverable.file_url)
        
        db.session.delete(deliverable)
        db.session.commit()
        
        return jsonify({'message': 'Livrable supprimé'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur suppression'}), 500

@deliverables_bp.route('/<int:deliverable_id>/submit', methods=['POST'])
@jwt_required()
@role_required('FREELANCE')
def submit_deliverable(deliverable_id):
    """Soumettre un livrable."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    deliverable = Deliverable.query.get_or_404(deliverable_id)
    
    if not check_freelance_permission(deliverable, current_user):
        return jsonify({'error': 'Non autorisé'}), 403
    
    allowed = [DeliverableStatus.DRAFT, DeliverableStatus.NEEDS_REVISION]
    if deliverable.status not in allowed:
        return jsonify({'error': 'Statut invalide pour soumission'}), 400
    
    if not deliverable.file_url:
        return jsonify({'error': 'Aucun fichier attaché au livrable'}), 400
    
    file = request.files.get('file')
    if file and file.filename != '':
        if deliverable.file_url:
            delete_physical_file(deliverable.file_url)
        
        filename = save_deliverable_file(file)
        if not filename:
            return jsonify({'error': 'Fichier invalide'}), 400
        
        deliverable.file_url = filename
    
    deliverable.status = DeliverableStatus.SUBMITTED
    deliverable.submitted_at = datetime.now()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Livrable soumis',
            'deliverable': deliverable_to_dict(deliverable)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur soumission'}), 500

# ============================
# ROUTES CLIENT - VALIDATION
# ============================

@deliverables_bp.route('/<int:deliverable_id>/review', methods=['POST'])
@jwt_required()
@role_required('CLIENT')
def start_review_deliverable(deliverable_id):
    """Commencer la review."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    deliverable = Deliverable.query.get_or_404(deliverable_id)
    
    if not check_client_permission(deliverable, current_user):
        return jsonify({'error': 'Non autorisé'}), 403
    
    if deliverable.status != DeliverableStatus.SUBMITTED:
        return jsonify({'error': 'Seuls les livrables soumis peuvent être mis en review'}), 400
    
    deliverable.status = DeliverableStatus.UNDER_REVIEW
    deliverable.reviewed_by = current_user.id
    deliverable.reviewed_at = datetime.now()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Review démarrée',
            'deliverable': deliverable_to_dict(deliverable)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors du démarrage de la review'}), 500

@deliverables_bp.route('/<int:deliverable_id>/accept', methods=['POST'])
@jwt_required()
@role_required('CLIENT')
def accept_deliverable(deliverable_id):
    """Accepter un livrable."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    deliverable = Deliverable.query.get_or_404(deliverable_id)
    
    if not check_client_permission(deliverable, current_user):
        return jsonify({'error': 'Non autorisé'}), 403
    
    if deliverable.status != DeliverableStatus.UNDER_REVIEW:
        return jsonify({'error': 'Seuls les livrables en review peuvent être acceptés'}), 400
    
    deliverable.status = DeliverableStatus.ACCEPTED
    deliverable.accepted_by = current_user.id
    deliverable.accepted_at = datetime.now()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Livrable accepté',
            'deliverable': deliverable_to_dict(deliverable)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de l\'acceptation'}), 500

@deliverables_bp.route('/<int:deliverable_id>/reject', methods=['POST'])
@jwt_required()
@role_required('CLIENT')
def reject_deliverable(deliverable_id):
    """Rejeter un livrable."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    if not data or not data.get('feedback', '').strip():
        return jsonify({'error': 'Feedback requis'}), 400
    
    deliverable = Deliverable.query.get_or_404(deliverable_id)
    
    if not check_client_permission(deliverable, current_user):
        return jsonify({'error': 'Non autorisé'}), 403
    
    if deliverable.status != DeliverableStatus.UNDER_REVIEW:
        return jsonify({'error': 'Seuls les livrables en review peuvent être rejetés'}), 400
    
    deliverable.status = DeliverableStatus.REJECTED
    deliverable.client_feedback = data['feedback'].strip()
    deliverable.reviewed_by = current_user.id
    deliverable.reviewed_at = datetime.now()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Livrable rejeté',
            'deliverable': deliverable_to_dict(deliverable)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors du rejet'}), 500

@deliverables_bp.route('/<int:deliverable_id>/request-revision', methods=['POST'])
@jwt_required()
@role_required('CLIENT')
def request_revision_deliverable(deliverable_id):
    """Demander une révision."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    if not data or not data.get('feedback', '').strip():
        return jsonify({'error': 'Feedback requis'}), 400
    
    deliverable = Deliverable.query.get_or_404(deliverable_id)
    
    if not check_client_permission(deliverable, current_user):
        return jsonify({'error': 'Non autorisé'}), 403
    
    if deliverable.status != DeliverableStatus.UNDER_REVIEW:
        return jsonify({'error': 'Seuls les livrables en review peuvent demander une révision'}), 400
    
    deliverable.status = DeliverableStatus.NEEDS_REVISION
    deliverable.client_feedback = data['feedback'].strip()
    deliverable.reviewed_by = current_user.id
    deliverable.reviewed_at = datetime.now()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Révision demandée',
            'deliverable': deliverable_to_dict(deliverable)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la demande de révision'}), 500

# ============================
# ROUTES LECTURE
# ============================

@deliverables_bp.route('/mission/<int:mission_id>', methods=['GET'])
@jwt_required()
def get_mission_deliverables(mission_id):
    """Récupérer les livrables d'une mission."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    mission = Mission.query.get_or_404(mission_id)
    
    # Vérifier les permissions
    if not current_user.profile:
        return jsonify({'error': 'Profil non trouvé'}), 403
    
    profile_type = current_user.profile.type if hasattr(current_user.profile, 'type') else None
    
    has_access = False
    if profile_type == 'client':
        has_access = (mission.client_id == current_user.id)
    elif profile_type == 'freelance':
        has_access = is_user_assigned_to_mission(current_user, mission_id)
    
    if not has_access:
        return jsonify({'error': 'Non autorisé à voir les livrables de cette mission'}), 403
    
    query = Deliverable.query.filter_by(mission_id=mission_id)
    
    status = request.args.get('status')
    if status:
        try:
            query = query.filter_by(status=DeliverableStatus(status))
        except ValueError:
            return jsonify({'error': 'Statut invalide'}), 400
    
    deliverables = query.order_by(Deliverable.created_at.desc()).all()
    return jsonify([deliverable_to_dict(d) for d in deliverables]), 200

@deliverables_bp.route('/<int:deliverable_id>', methods=['GET'])
@jwt_required()
def get_deliverable(deliverable_id):
    """Récupérer un livrable."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    deliverable = Deliverable.query.get_or_404(deliverable_id)
    mission = Mission.query.get(deliverable.mission_id)
    
    if not mission:
        return jsonify({'error': 'Mission non trouvée'}), 404
    
    # Vérifier les permissions
    if not current_user.profile:
        return jsonify({'error': 'Profil non trouvé'}), 403
    
    profile_type = current_user.profile.type if hasattr(current_user.profile, 'type') else None
    
    has_access = False
    if profile_type == 'client':
        has_access = (mission.client_id == current_user.id)
    elif profile_type == 'freelance':
        has_access = (deliverable.submitted_by == current_user.id)
    
    if not has_access:
        return jsonify({'error': 'Non autorisé'}), 403
    
    return jsonify(deliverable_to_dict(deliverable)), 200

@deliverables_bp.route('/<int:deliverable_id>/download', methods=['GET'])
@jwt_required()
def download_deliverable(deliverable_id):
    """Télécharger un fichier."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    deliverable = Deliverable.query.get_or_404(deliverable_id)
    mission = Mission.query.get(deliverable.mission_id)
    
    if not mission:
        return jsonify({'error': 'Mission non trouvée'}), 404
    
    # Vérifier les permissions
    if not current_user.profile:
        return jsonify({'error': 'Profil non trouvé'}), 403
    
    profile_type = current_user.profile.type if hasattr(current_user.profile, 'type') else None
    
    has_access = False
    if profile_type == 'client':
        has_access = (mission.client_id == current_user.id)
    elif profile_type == 'freelance':
        has_access = (deliverable.submitted_by == current_user.id)
    
    if not has_access:
        return jsonify({'error': 'Non autorisé'}), 403
    
    if not deliverable.file_url:
        return jsonify({'error': 'Aucun fichier attaché'}), 404
    
    file_path = os.path.join(get_upload_folder(), deliverable.file_url)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Fichier introuvable sur le serveur'}), 404
    
    # Extraire le nom original du fichier
    parts = deliverable.file_url.split('_')
    original_name = '_'.join(parts[2:]) if len(parts) >= 3 else deliverable.file_url
    
    # Créer un nom de fichier sûr pour le téléchargement
    safe_title = deliverable.title.replace(' ', '_').replace('/', '_').replace('\\', '_')
    safe_filename = f"{safe_title}_{original_name}"
    
    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        current_app.logger.error(f"Erreur téléchargement fichier: {str(e)}")
        return jsonify({'error': 'Erreur lors du téléchargement du fichier'}), 500

@deliverables_bp.route('/my-deliverables', methods=['GET'])
@jwt_required()
def get_my_deliverables():
    """Mes livrables (freelance)."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    if not current_user.profile:
        return jsonify({'error': 'Profil non trouvé'}), 403
    
    if not hasattr(current_user.profile, 'type') or current_user.profile.type != 'freelance':
        return jsonify({'error': 'Réservé aux freelances'}), 403
    
    query = Deliverable.query.filter_by(submitted_by=current_user.id)
    
    status = request.args.get('status')
    if status:
        try:
            query = query.filter_by(status=DeliverableStatus(status))
        except ValueError:
            return jsonify({'error': 'Statut invalide'}), 400
    
    deliverables = query.order_by(Deliverable.created_at.desc()).all()
    return jsonify([deliverable_to_dict(d) for d in deliverables]), 200

@deliverables_bp.route('/client-deliverables', methods=['GET'])
@jwt_required()
def get_client_deliverables():
    """Livrables pour review (client)."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    if not current_user.profile:
        return jsonify({'error': 'Profil non trouvé'}), 403
    
    if not hasattr(current_user.profile, 'type') or current_user.profile.type != 'client':
        return jsonify({'error': 'Réservé aux clients'}), 403
    
    # Récupérer toutes les missions du client
    missions = Mission.query.filter_by(client_id=current_user.id).all()
    mission_ids = [m.id for m in missions]
    
    if not mission_ids:
        return jsonify([]), 200
    
    query = Deliverable.query.filter(Deliverable.mission_id.in_(mission_ids))
    
    status = request.args.get('status')
    if status:
        try:
            query = query.filter_by(status=DeliverableStatus(status))
        except ValueError:
            return jsonify({'error': 'Statut invalide'}), 400
    
    deliverables = query.order_by(Deliverable.created_at.desc()).all()
    return jsonify([deliverable_to_dict(d) for d in deliverables]), 200

# ============================
# ROUTE DE DEBUG
# ============================

@deliverables_bp.route('/debug-permissions', methods=['GET'])
@jwt_required()
def debug_permissions():
    """Endpoint de debug pour vérifier les permissions."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    mission_id = request.args.get('mission_id')
    
    result = {
        'user_id': current_user.id,
        'profile_exists': current_user.profile is not None
    }
    
    if current_user.profile:
        result['profile_type'] = current_user.profile.type if hasattr(current_user.profile, 'type') else 'unknown'
    
    if mission_id:
        try:
            mission_id_int = int(mission_id)
            mission = Mission.query.get(mission_id_int)
            
            if mission:
                result['mission'] = {
                    'id': mission.id,
                    'title': mission.title,
                    'status': mission.status.value if mission.status else None,
                    'client_id': mission.client_id
                }
                
                # Vérifier les postulations
                postulations = Postulation.query.filter_by(
                    mission_id=mission_id_int,
                    freelance_id=current_user.id
                ).all()
                
                result['postulations'] = [
                    {
                        'id': p.id,
                        'status': p.status.value if p.status else None
                    }
                    for p in postulations
                ]
                
                # Vérifier si l'utilisateur est assigné
                result['is_assigned'] = is_user_assigned_to_mission(current_user, mission_id_int)
            else:
                result['mission'] = 'not_found'
                
        except ValueError:
            result['mission_id_error'] = 'invalid_format'
    
    return jsonify(result), 200

# ============================
# TEST JWT (à utiliser temporairement pour déboguer)
# ============================

@deliverables_bp.route('/test-jwt', methods=['GET'])
def test_jwt():
    """Endpoint de test pour vérifier le JWT."""
    from flask_jwt_extended import get_jwt_identity
    
    print("\n" + "="*60)
    print("🔍 TEST JWT - DEBUG ENDPOINT")
    print("="*60)
    
    # 1️⃣ Afficher le header Authorization
    auth_header = request.headers.get('Authorization', 'ABSENT')
    print(f"\n1️⃣ Authorization Header:")
    print(f"   Valeur reçue: {auth_header[:50] if auth_header != 'ABSENT' else 'ABSENT'}...")
    print(f"   Commence par 'Bearer ': {auth_header.startswith('Bearer ')}")
    
    # 2️⃣ Afficher tous les headers
    print(f"\n2️⃣ Tous les Headers reçus:")
    for key, value in request.headers.items():
        if key.lower() in ['authorization', 'content-type', 'content-length']:
            print(f"   {key}: {str(value)[:50]}...")
    
    # 3️⃣ Vérifier si JWT est décodable
    try:
        user_id = get_jwt_identity()
        print(f"\n3️⃣ JWT valide:")
        print(f"   User ID: {user_id}")
        return jsonify({
            'status': '✅ JWT valide',
            'user_id': user_id,
            'auth_header_present': auth_header != 'ABSENT',
            'auth_header_valid': auth_header.startswith('Bearer ')
        }), 200
    except Exception as e:
        print(f"\n3️⃣ Erreur JWT:")
        print(f"   Exception: {str(e)}")
        return jsonify({
            'status': '❌ JWT invalide ou absent',
            'error': str(e),
            'auth_header_present': auth_header != 'ABSENT',
            'auth_header': auth_header[:30] if auth_header != 'ABSENT' else 'ABSENT'
        }), 401