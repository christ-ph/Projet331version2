# app/missions/routes.py - CORRIGÉ
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import or_, and_
import json

from app import db
from app.models import Mission, Postulation, MissionStatus, PostulationStatus, User, Profile
from app.utils import role_required

# Création du blueprint avec le nom spécifique
missions_bp = Blueprint('missions_bp', __name__)

# ============================
# UTILITAIRES
# ============================

def mission_to_dict(mission):
    """Convertit une mission en dictionnaire pour la réponse JSON"""
    # Compter les postulations par statut
    postulations = mission.postulations.all() if hasattr(mission, 'postulations') else []
    postulations_total = len(postulations)
    postulations_pending = len([p for p in postulations if p.status == PostulationStatus.PENDING])
    
    return {
        'id': mission.id,
        'title': mission.title,
        'description': mission.description,
        'budget': mission.budget,
        'deadline': mission.deadline.isoformat() if mission.deadline else None,
        'status': mission.status.value,
        'client_id': mission.client_id,
        'created_at': mission.created_at.isoformat() if mission.created_at else None,
        'updated_at': mission.updated_at.isoformat() if mission.updated_at else None,
        'postulations_total': postulations_total,
        'postulations_pending': postulations_pending,
        'required_skills': mission.required_skills if hasattr(mission, 'required_skills') else []
    }

def get_current_user_id():
    """Récupère l'ID de l'utilisateur courant depuis g ou JWT"""
    # Vérifier si l'utilisateur est déjà dans g (depuis role_required)
    if hasattr(g, 'current_user') and g.current_user:
        return g.current_user.id
    
    # Sinon, récupérer depuis le JWT
    current_user_id = get_jwt_identity()
    
    # Convertir en int
    try:
        return int(current_user_id)
    except (ValueError, TypeError):
        return None

def check_client_permission(mission):
    """Vérifie si l'utilisateur courant est le client propriétaire de la mission"""
    current_user_id = get_current_user_id()
    
    if not current_user_id or mission.client_id != current_user_id:
        return False, jsonify({'error': 'Accès non autorisé à cette mission'}), 403
    return True, None, None

# ============================
# ROUTES CRUD
# ============================

@missions_bp.route('', methods=['GET'])
def get_missions():
    """Récupère toutes les missions avec filtres optionnels"""
    try:
        query = Mission.query
        
        # Filtrage par statut
        status_param = request.args.get('status')
        if status_param:
            try:
                query = query.filter(Mission.status == MissionStatus(status_param))
            except ValueError:
                return jsonify({'error': 'Statut invalide'}), 400
        
        # Filtrage par budget maximum
        max_budget = request.args.get('max_budget')
        if max_budget:
            try:
                query = query.filter(Mission.budget <= float(max_budget))
            except ValueError:
                pass
        
        # Filtrage par compétences (CORRECTION: utilisation correcte de JSON array)
        skills = request.args.get('skills')
        if skills and hasattr(Mission, 'required_skills'):
            skills_list = [s.strip() for s in skills.split(',')]
            # Pour PostgreSQL avec JSONB, utiliser @> (contains)
            from sqlalchemy import text
            query = query.filter(Mission.required_skills.contains(skills_list))
        
        missions = query.order_by(Mission.created_at.desc()).all()
        
        return jsonify([mission_to_dict(mission) for mission in missions]), 200
    
    except Exception as e:
        print(f"❌ ERROR get_missions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>', methods=['GET'])
def get_mission(mission_id):
    """Récupère une mission spécifique"""
    try:
        mission = Mission.query.get_or_404(mission_id)
        return jsonify(mission_to_dict(mission)), 200
    except Exception as e:
        print(f"❌ ERROR get_mission: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('', methods=['POST'])
@jwt_required()
@role_required(['CLIENT'])
def create_mission():
    """Crée une nouvelle mission (par défaut en DRAFT)"""
    try:
        current_user_id = get_current_user_id()
        
        # Récupérer les données
        data = request.get_json()
        
        # Validation des champs obligatoires
        if not data.get('title'):
            return jsonify({'error': 'Le titre est requis'}), 400
        if not data.get('description'):
            return jsonify({'error': 'La description est requise'}), 400
        
        # CORRECTION: MissionStatus.DRAFT
        initial_status = MissionStatus.DRAFT
        
        if 'status' in data:
            try:
                # Convertir le string en MissionStatus
                initial_status = MissionStatus(data['status'].upper())
            except (KeyError, ValueError):
                return jsonify({'error': f'Statut invalide: {data["status"]}'}), 400
        
        # Créer la mission
        mission = Mission(
            title=data['title'],
            description=data['description'],
            client_id=current_user_id,
            status=initial_status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Champs optionnels
        if 'budget' in data and data['budget'] is not None:
            try:
                mission.budget = float(data['budget'])
            except (ValueError, TypeError):
                return jsonify({'error': 'Budget invalide'}), 400
        
        if 'deadline' in data and data['deadline']:
            try:
                mission.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                return jsonify({'error': 'Format de date invalide'}), 400
        
        # Compétences requises (OPTIONNEL)
        if 'required_skills' in data:
            if data['required_skills'] is None or isinstance(data['required_skills'], list):
                mission.required_skills = data['required_skills']
            else:
                return jsonify({'error': 'required_skills doit être une liste'}), 400
        
        db.session.add(mission)
        db.session.commit()
        
        return jsonify(mission_to_dict(mission)), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR create_mission: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>', methods=['PUT'])
@jwt_required()
@role_required(['CLIENT'])
def update_mission(mission_id):
    """Met à jour une mission"""
    try:
        mission = Mission.query.get_or_404(mission_id)
        
        # Vérifier les permissions
        permission_ok, error_response, status_code = check_client_permission(mission)
        if not permission_ok:
            return error_response, status_code
        
        # Vérifier que la mission peut être modifiée
        if mission.status not in [MissionStatus.DRAFT, MissionStatus.OPEN]:
            return jsonify({'error': 'Impossible de modifier cette mission'}), 400
        
        data = request.get_json()
        
        # Mise à jour des champs
        if 'title' in data:
            mission.title = data['title']
        
        if 'description' in data:
            mission.description = data['description']
        
        if 'budget' in data:
            try:
                mission.budget = float(data['budget']) if data['budget'] is not None else None
            except (ValueError, TypeError):
                return jsonify({'error': 'Budget invalide'}), 400
        
        if 'deadline' in data:
            try:
                mission.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00')) if data['deadline'] else None
            except (ValueError, TypeError):
                return jsonify({'error': 'Format de date invalide'}), 400
        
        # Mise à jour des compétences
        if 'required_skills' in data:
            if data['required_skills'] is None or isinstance(data['required_skills'], list):
                mission.required_skills = data['required_skills']
            else:
                return jsonify({'error': 'required_skills doit être une liste ou null'}), 400
        
        # Mettre à jour la date de modification
        mission.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Mission mise à jour',
            'mission': mission_to_dict(mission)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR update_mission: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>', methods=['DELETE'])
@jwt_required()
@role_required(['CLIENT'])
def delete_mission(mission_id):
    """Supprime une mission"""
    try:
        mission = Mission.query.get_or_404(mission_id)
        
        # Vérifier les permissions
        permission_ok, error_response, status_code = check_client_permission(mission)
        if not permission_ok:
            return error_response, status_code
        
        # Vérifier que la mission peut être supprimée
        if mission.status == MissionStatus.IN_PROGRESS:
            return jsonify({'error': 'Impossible de supprimer une mission en cours'}), 400
        
        # Vérifier si mission publiée avec des candidatures
        if mission.status == MissionStatus.OPEN and mission.postulations.count() > 0:
            return jsonify({
                'error': 'Impossible de supprimer une mission publiée avec des candidatures'
            }), 400
        
        # Supprimer les postulations associées
        postulations_supprimees = Postulation.query.filter_by(mission_id=mission_id).delete()
        
        # Supprimer la mission
        db.session.delete(mission)
        db.session.commit()
        
        return jsonify({
            'message': 'Mission supprimée avec succès',
            'postulations_supprimees': postulations_supprimees
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR delete_mission: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================
# ROUTES SPÉCIFIQUES
# ============================

@missions_bp.route('/my-missions', methods=['GET'])
@jwt_required()
@role_required(['CLIENT'])
def get_my_missions():
    """Récupère les missions de l'utilisateur connecté (client)"""
    try:
        current_user_id = get_current_user_id()
        
        # Filtrage par statut
        status_param = request.args.get('status')
        query = Mission.query.filter_by(client_id=current_user_id)
        
        if status_param:
            try:
                query = query.filter(Mission.status == MissionStatus(status_param))
            except ValueError:
                return jsonify({'error': 'Statut invalide'}), 400
        
        missions = query.order_by(Mission.created_at.desc()).all()
        
        return jsonify([mission_to_dict(mission) for mission in missions]), 200
    
    except Exception as e:
        print(f"❌ ERROR get_my_missions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/available', methods=['GET'])
@jwt_required()
@role_required(['FREELANCE'])
def get_available_missions():
    """Récupère les missions disponibles pour le freelance connecté"""
    try:
        current_user_id = get_current_user_id()
        
        # Récupérer les missions ouvertes (OPEN)
        query = Mission.query.filter_by(status=MissionStatus.OPEN)
        
        # Exclure les missions où le freelance a déjà postulé
        postulated_missions_query = db.session.query(Postulation.mission_id)\
            .filter(Postulation.freelance_id == current_user_id)\
            .subquery()
        
        query = query.filter(Mission.id.notin_(postulated_missions_query))
        
        # Filtres optionnels
        min_budget = request.args.get('min_budget')
        if min_budget:
            try:
                query = query.filter(Mission.budget >= float(min_budget))
            except ValueError:
                pass
        
        max_budget = request.args.get('max_budget')
        if max_budget:
            try:
                query = query.filter(Mission.budget <= float(max_budget))
            except ValueError:
                pass
        
        # Filtrage par compétences (si supported)
        skills = request.args.get('skills')
        if skills and hasattr(Mission, 'required_skills'):
            skills_list = [s.strip() for s in skills.split(',')]
            # Utiliser .contains() pour PostgreSQL JSONB
            query = query.filter(Mission.required_skills.contains(skills_list))
        
        missions = query.order_by(Mission.created_at.desc()).all()
        
        return jsonify([mission_to_dict(mission) for mission in missions]), 200
    
    except Exception as e:
        print(f"❌ ERROR get_available_missions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>/publish', methods=['POST'])
@jwt_required()
@role_required(['CLIENT'])
def publish_mission(mission_id):
    """Publie une mission (passe de DRAFT à OPEN)"""
    try:
        mission = Mission.query.get_or_404(mission_id)
        
        # Vérifier les permissions
        permission_ok, error_response, status_code = check_client_permission(mission)
        if not permission_ok:
            return error_response, status_code
        
        # Vérifier que la mission est en brouillon
        if mission.status != MissionStatus.DRAFT:
            return jsonify({
                'error': f'Impossible de publier une mission avec le statut {mission.status.value}'
            }), 400
        
        # Changer le statut
        mission.status = MissionStatus.OPEN
        mission.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Mission publiée avec succès',
            'mission': mission_to_dict(mission)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR publish_mission: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>/status', methods=['PATCH'])
@jwt_required()
@role_required(['CLIENT'])
def change_mission_status(mission_id):
    """Change le statut d'une mission"""
    try:
        mission = Mission.query.get_or_404(mission_id)
        
        # Vérifier les permissions
        permission_ok, error_response, status_code = check_client_permission(mission)
        if not permission_ok:
            return error_response, status_code
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Statut requis'}), 400
        
        try:
            new_status = MissionStatus(data['status'].upper())
        except ValueError:
            return jsonify({'error': f'Statut invalide: {data["status"]}'}), 400
        
        current_status = mission.status
        
        # Vérifier les transitions valides
        valid_transitions = {
            MissionStatus.DRAFT: [MissionStatus.OPEN, MissionStatus.CANCELLED],
            MissionStatus.OPEN: [MissionStatus.IN_PROGRESS, MissionStatus.CANCELLED],
            MissionStatus.IN_PROGRESS: [MissionStatus.COMPLETED, MissionStatus.CANCELLED],
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            return jsonify({
                'error': f'Transition de {current_status.value} à {new_status.value} non autorisée'
            }), 400
        
        # Si passage en IN_PROGRESS, vérifier qu'il y a une postulation acceptée
        if new_status == MissionStatus.IN_PROGRESS:
            accepted_postulation = Postulation.query.filter_by(
                mission_id=mission_id,
                status=PostulationStatus.ACCEPTED
            ).first()
            
            if not accepted_postulation:
                return jsonify({
                    'error': 'Aucun freelance accepté pour cette mission'
                }), 400
        
        mission.status = new_status
        mission.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': f'Statut mis à jour: {new_status.value}',
            'mission': mission_to_dict(mission)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR change_mission_status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>/postulations', methods=['GET'])
@jwt_required()
@role_required(['CLIENT'])
def get_mission_postulations(mission_id):
    """Récupère les postulations pour une mission (client seulement)"""
    try:
        mission = Mission.query.get_or_404(mission_id)
        
        # Vérifier les permissions
        permission_ok, error_response, status_code = check_client_permission(mission)
        if not permission_ok:
            return error_response, status_code
        
        postulations = Postulation.query.filter_by(mission_id=mission_id)\
            .order_by(Postulation.created_at.desc())\
            .all()
        
        postulations_data = []
        for postulation in postulations:
            freelance = User.query.get(postulation.freelance_id)
            
            # Récupérer le profil via la relation (si elle existe)
            freelance_profile = None
            if freelance:
                # Essayer différentes méthodes d'accès au profil
                if hasattr(freelance, 'profile') and freelance.profile:
                    freelance_profile = freelance.profile
                elif hasattr(freelance, 'get_profile'):
                    freelance_profile = freelance.get_profile()
            
            postulations_data.append({
                'id': postulation.id,
                'freelance_id': postulation.freelance_id,
                'freelance_name': freelance_profile.full_name if freelance_profile and hasattr(freelance_profile, 'full_name') else 'Inconnu',
                'status': postulation.status.value,
                'created_at': postulation.created_at.isoformat(),
                'profile_title': freelance_profile.title if freelance_profile and hasattr(freelance_profile, 'title') else None,
                'rating': freelance_profile.rating if freelance_profile and hasattr(freelance_profile, 'rating') else 0,
                'completed_projects': freelance_profile.completed_projects if freelance_profile and hasattr(freelance_profile, 'completed_projects') else 0
            })
        
        return jsonify(postulations_data), 200
    
    except Exception as e:
        print(f"❌ ERROR get_mission_postulations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>/apply', methods=['POST'])
@jwt_required()
@role_required(['FREELANCE'])
def apply_to_mission(mission_id):
    """Permet à un freelance de postuler à une mission"""
    try:
        current_user_id = get_current_user_id()
        
        # Vérifier que la mission existe et est ouverte
        mission = Mission.query.get_or_404(mission_id)
        if mission.status != MissionStatus.OPEN:
            return jsonify({'error': 'Cette mission n\'est plus ouverte aux candidatures'}), 400
        
        # Vérifier que le freelance n'a pas déjà postulé
        existing_postulation = Postulation.query.filter_by(
            mission_id=mission_id,
            freelance_id=current_user_id
        ).first()
        
        if existing_postulation:
            return jsonify({'error': 'Vous avez déjà postulé à cette mission'}), 400
        
        # Créer la postulation
        postulation = Postulation(
            mission_id=mission_id,
            freelance_id=current_user_id,
            status=PostulationStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        db.session.add(postulation)
        db.session.commit()
        
        return jsonify({
            'message': 'Candidature envoyée avec succès',
            'postulation_id': postulation.id,
            'status': postulation.status.value
        }), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR apply_to_mission: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/search', methods=['GET'])
def search_missions():
    """Recherche de missions avec plusieurs critères"""
    try:
        # Par défaut, seulement les missions OPEN
        query = Mission.query.filter_by(status=MissionStatus.OPEN)
        
        # Filtre par mots-clés dans titre/description
        keywords = request.args.get('q')
        if keywords:
            search = f"%{keywords}%"
            query = query.filter(
                or_(
                    Mission.title.ilike(search),
                    Mission.description.ilike(search)
                )
            )
        
        # Filtre par budget range
        min_budget = request.args.get('min_budget')
        max_budget = request.args.get('max_budget')
        
        if min_budget:
            try:
                query = query.filter(Mission.budget >= float(min_budget))
            except ValueError:
                pass
        
        if max_budget:
            try:
                query = query.filter(Mission.budget <= float(max_budget))
            except ValueError:
                pass
        
        # Filtre par deadline
        deadline_before = request.args.get('deadline_before')
        if deadline_before:
            try:
                deadline_date = datetime.fromisoformat(deadline_before.replace('Z', '+00:00'))
                query = query.filter(Mission.deadline <= deadline_date)
            except (ValueError, TypeError):
                pass
        
        # Filtre par compétences
        skills = request.args.get('skills')
        if skills and hasattr(Mission, 'required_skills'):
            skills_list = [s.strip() for s in skills.split(',')]
            query = query.filter(Mission.required_skills.contains(skills_list))
        
        # Tri
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')
        
        if sort_by == 'budget':
            if order == 'asc':
                query = query.order_by(Mission.budget.asc())
            else:
                query = query.order_by(Mission.budget.desc())
        elif sort_by == 'deadline':
            if order == 'asc':
                query = query.order_by(Mission.deadline.asc())
            else:
                query = query.order_by(Mission.deadline.desc())
        else:  # created_at par défaut
            if order == 'asc':
                query = query.order_by(Mission.created_at.asc())
            else:
                query = query.order_by(Mission.created_at.desc())
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        missions_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        missions_data = [mission_to_dict(mission) for mission in missions_paginated.items]
        
        return jsonify({
            'missions': missions_data,
            'total': missions_paginated.total,
            'page': missions_paginated.page,
            'per_page': missions_paginated.per_page,
            'pages': missions_paginated.pages
        }), 200
    
    except Exception as e:
        print(f"❌ ERROR search_missions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/my-applications', methods=['GET'])
@jwt_required()
@role_required(['FREELANCE'])
def get_my_applications():
    """Récupère toutes les postulations du freelance connecté"""
    try:
        current_user_id = get_current_user_id()
        
        if not current_user_id:
            return jsonify({'error': 'Utilisateur non authentifié'}), 401
        
        # Récupérer toutes les postulations du freelance
        postulations = Postulation.query\
            .filter_by(freelance_id=current_user_id)\
            .order_by(Postulation.created_at.desc())\
            .all()
        
        applications_data = []
        for postulation in postulations:
            mission = Mission.query.get(postulation.mission_id)
            
            if not mission:
                continue  # Skip si la mission n'existe plus
                
            # Format de réponse
            application = {
                'id': postulation.id,
                'postulation_id': postulation.id,
                'status': postulation.status.value,
                'created_at': postulation.created_at.isoformat() if postulation.created_at else None,
                'mission_id': mission.id,
                'mission': {
                    'id': mission.id,
                    'title': mission.title,
                    'description': mission.description,
                    'budget': mission.budget,
                    'deadline': mission.deadline.isoformat() if mission.deadline else None,
                    'status': mission.status.value,
                    'created_at': mission.created_at.isoformat() if mission.created_at else None,
                    'required_skills': mission.required_skills if hasattr(mission, 'required_skills') else []
                }
            }
            
            # Ajouter info client si disponible
            client = User.query.get(mission.client_id)
            if client:
                application['client'] = {
                    'id': client.id,
                    'email': client.email
                    # Ajouter d'autres infos si disponibles
                }
            
            applications_data.append(application)
        
        return jsonify(applications_data), 200
    
    except Exception as e:
        print(f"❌ ERROR get_my_applications: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================
# ROUTES ESSENTIELLES - GESTION CANDIDATURES
# ============================

@missions_bp.route('/<int:mission_id>/applications/<int:application_id>/status', methods=['PUT'])
@jwt_required()
@role_required(['CLIENT'])
def update_application_status(mission_id, application_id):
    """
    Accepter ou refuser une candidature
    Body: {"status": "accepted" | "rejected"}
    """
    try:
        current_user_id = get_current_user_id()
        
        # Vérifier la mission
        mission = Mission.query.get_or_404(mission_id)
        if mission.client_id != current_user_id:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Vérifier la candidature
        application = Postulation.query.get_or_404(application_id)
        if application.mission_id != mission.id:
            return jsonify({'error': 'Cette candidature n\'appartient pas à cette mission'}), 400
        
        # Récupérer le nouveau statut
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Statut manquant'}), 400
        
        # Valider le statut
        new_status = data['status'].lower()
        if new_status not in ['accepted', 'rejected']:
            return jsonify({'error': 'Statut invalide. Utilisez "accepted" ou "rejected"'}), 400
        
        # Convertir en enum
        status_enum = PostulationStatus.ACCEPTED if new_status == 'accepted' else PostulationStatus.REJECTED
        
        # Si on accepte, vérifier qu'il n'y a pas déjà une candidature acceptée
        if status_enum == PostulationStatus.ACCEPTED:
            existing_accepted = Postulation.query.filter(
                and_(
                    Postulation.mission_id == mission.id,
                    Postulation.status == PostulationStatus.ACCEPTED,
                    Postulation.id != application_id
                )
            ).first()
            
            if existing_accepted:
                return jsonify({'error': 'Une candidature est déjà acceptée pour cette mission'}), 400
            
            # Refuser les autres candidatures
            Postulation.query.filter(
                and_(
                    Postulation.mission_id == mission.id,
                    Postulation.status == PostulationStatus.PENDING,
                    Postulation.id != application_id
                )
            ).update({'status': PostulationStatus.REJECTED})
            
            # Mettre la mission en IN_PROGRESS
            mission.status = MissionStatus.IN_PROGRESS
        
        # Mettre à jour la candidature
        application.status = status_enum
        db.session.commit()
        
        return jsonify({
            'message': f'Candidature {new_status}',
            'application_id': application.id,
            'status': application.status.value
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR update_application_status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>/complete', methods=['PUT'])
@jwt_required()
@role_required(['CLIENT'])
def complete_mission(mission_id):
    """
    Marquer une mission comme complétée
    """
    try:
        current_user_id = get_current_user_id()
        
        # Vérifier la mission
        mission = Mission.query.get_or_404(mission_id)
        if mission.client_id != current_user_id:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Vérifier que la mission est en cours
        if mission.status != MissionStatus.IN_PROGRESS:
            return jsonify({'error': 'Seules les missions en cours peuvent être complétées'}), 400
        
        # Vérifier qu'il y a une candidature acceptée
        accepted_application = Postulation.query.filter(
            and_(
                Postulation.mission_id == mission.id,
                Postulation.status == PostulationStatus.ACCEPTED
            )
        ).first()
        
        if not accepted_application:
            return jsonify({'error': 'Aucun freelance accepté pour cette mission'}), 400
        
        # Marquer comme complétée
        mission.status = MissionStatus.COMPLETED
        db.session.commit()
        
        return jsonify({
            'message': 'Mission marquée comme complétée',
            'mission_id': mission.id,
            'status': mission.status.value
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR complete_mission: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>/cancel', methods=['PUT'])
@jwt_required()
@role_required(['CLIENT'])
def cancel_mission(mission_id):
    """
    Annuler une mission
    """
    try:
        current_user_id = get_current_user_id()
        
        # Vérifier la mission
        mission = Mission.query.get_or_404(mission_id)
        if mission.client_id != current_user_id:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Vérifier que la mission n'est pas déjà complétée ou annulée
        if mission.status in [MissionStatus.COMPLETED, MissionStatus.CANCELLED]:
            return jsonify({'error': f'Impossible d\'annuler une mission déjà {mission.status.value}'}), 400
        
        # Annuler toutes les candidatures
        Postulation.query.filter(
            Postulation.mission_id == mission.id
        ).update({'status': PostulationStatus.CANCELLED})
        
        # Annuler la mission
        mission.status = MissionStatus.CANCELLED
        db.session.commit()
        
        return jsonify({
            'message': 'Mission annulée',
            'mission_id': mission.id,
            'status': mission.status.value
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR cancel_mission: {str(e)}")
        return jsonify({'error': str(e)}), 500