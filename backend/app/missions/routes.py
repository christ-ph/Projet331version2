# Vérifiez que vous avez ces imports en haut du fichier
from flask import Blueprint, Response, request, jsonify, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import or_, and_
import json

from app import db
from app.models import Deliverable, DeliverableStatus, FreelanceProfile, Mission, Postulation, MissionStatus, PostulationStatus, User, Profile
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
        
        # Filtrage par compétences
        skills = request.args.get('skills')
        if skills:
            try:
                skills_list = json.loads(skills) if skills.startswith('[') else [s.strip() for s in skills.split(',')]
                if hasattr(Mission, 'required_skills') and skills_list:
                    # Pour PostgreSQL avec JSONB
                    from sqlalchemy import text
                    query = query.filter(Mission.required_skills.contains(skills_list))
            except:
                pass
        
        missions = query.order_by(Mission.created_at.desc()).all()
        
        return jsonify([mission_to_dict(mission) for mission in missions]), 200
    
    except Exception as e:
        app.logger.error(f"❌ ERROR get_missions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>', methods=['GET'])
def get_mission(mission_id):
    """Récupère une mission spécifique"""
    try:
        mission = Mission.query.get_or_404(mission_id)
        return jsonify(mission_to_dict(mission)), 200
    except Exception as e:
        app.logger.error(f"❌ ERROR get_mission: {str(e)}")
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
        
        # Compétences requises
        if 'required_skills' in data:
            if data['required_skills'] is None or isinstance(data['required_skills'], list):
                mission.required_skills = data['required_skills']
            elif isinstance(data['required_skills'], str):
                # Convertir la string en liste
                mission.required_skills = [s.strip() for s in data['required_skills'].split(',')]
            else:
                return jsonify({'error': 'required_skills doit être une liste'}), 400
        
        db.session.add(mission)
        db.session.commit()
        
        return jsonify(mission_to_dict(mission)), 201
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"❌ ERROR create_mission: {str(e)}")
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
            elif isinstance(data['required_skills'], str):
                mission.required_skills = [s.strip() for s in data['required_skills'].split(',')]
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
        app.logger.error(f"❌ ERROR update_mission: {str(e)}")
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
        app.logger.error(f"❌ ERROR delete_mission: {str(e)}")
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
        app.logger.error(f"❌ ERROR get_my_missions: {str(e)}")
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
        
        # Filtrage par compétences
        skills = request.args.get('skills')
        if skills:
            try:
                skills_list = json.loads(skills) if skills.startswith('[') else [s.strip() for s in skills.split(',')]
                if hasattr(Mission, 'required_skills') and skills_list:
                    query = query.filter(Mission.required_skills.contains(skills_list))
            except:
                pass
        
        missions = query.order_by(Mission.created_at.desc()).all()
        
        return jsonify([mission_to_dict(mission) for mission in missions]), 200
    
    except Exception as e:
        app.logger.error(f"❌ ERROR get_available_missions: {str(e)}")
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
        app.logger.error(f"❌ ERROR publish_mission: {str(e)}")
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
        app.logger.error(f"❌ ERROR change_mission_status: {str(e)}")
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
            
            # Récupérer le profil
            freelance_profile = None
            if freelance:
                if hasattr(freelance, 'freelance_profile'):
                    freelance_profile = freelance.freelance_profile
                elif hasattr(freelance, 'profile'):
                    freelance_profile = freelance.profile
            
            postulations_data.append({
                'id': postulation.id,
                'postulation_id': postulation.id,  # Ajouté pour compatibilité avec Pinia
                'freelance_id': postulation.freelance_id,
                'freelance_name': freelance_profile.full_name if freelance_profile and hasattr(freelance_profile, 'full_name') else 'Inconnu',
                'status': postulation.status.value,
                'created_at': postulation.created_at.isoformat() if postulation.created_at else None,
                'profile_title': freelance_profile.title if freelance_profile and hasattr(freelance_profile, 'title') else None,
                'rating': freelance_profile.rating if freelance_profile and hasattr(freelance_profile, 'rating') else 0,
                'completed_projects': freelance_profile.completed_projects if freelance_profile and hasattr(freelance_profile, 'completed_projects') else 0
            })
        
        return jsonify(postulations_data), 200
    
    except Exception as e:
        app.logger.error(f"❌ ERROR get_mission_postulations: {str(e)}")
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
        app.logger.error(f"❌ ERROR apply_to_mission: {str(e)}")
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
        if skills:
            try:
                skills_list = json.loads(skills) if skills.startswith('[') else [s.strip() for s in skills.split(',')]
                if hasattr(Mission, 'required_skills') and skills_list:
                    query = query.filter(Mission.required_skills.contains(skills_list))
            except:
                pass
        
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
        app.logger.error(f"❌ ERROR search_missions: {str(e)}")
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
                
            # Format de réponse compatible avec Pinia
            application = {
                'id': postulation.id,
                'postulation_id': postulation.id,  # Alias pour compatibilité
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
                }
            
            applications_data.append(application)
        
        return jsonify(applications_data), 200
    
    except Exception as e:
        app.logger.error(f"❌ ERROR get_my_applications: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================
# NOUVELLES ROUTES COMPATIBLES AVEC PINIA STORE
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
            mission.updated_at = datetime.utcnow()
        
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
        app.logger.error(f"❌ ERROR update_application_status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>/complete', methods=['PUT'])
@jwt_required()
@role_required(['CLIENT'])
def complete_mission(mission_id):
    """
    Marquer une mission comme complétée et évaluer le freelance
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
        
        # Récupérer les données de la requête
        data = request.get_json() or {}
        
        # Validation des données optionnelles
        feedback = data.get('feedback', '').strip()
        rating = data.get('rating')
        
        if rating is not None:
            if not isinstance(rating, (int, float)) or rating < 0 or rating > 5:
                return jsonify({'error': 'La note doit être un nombre entre 0 et 5'}), 400
        
        # Récupérer le profil du freelance
        freelance_user = accepted_application.freelance
        freelance_profile = FreelanceProfile.query.filter_by(user_id=freelance_user.id).first()
        
        if not freelance_profile:
            return jsonify({'error': 'Profil freelance non trouvé'}), 404
        
        # Mettre à jour les statistiques du freelance si une note est fournie
        if rating is not None:
            # Calculer la nouvelle note moyenne
            if freelance_profile.completed_projects > 0:
                # Calculer la nouvelle moyenne
                total_rating = freelance_profile.rating * freelance_profile.completed_projects
                total_rating += rating
                freelance_profile.completed_projects += 1
                freelance_profile.rating = total_rating / freelance_profile.completed_projects
            else:
                # Premier projet
                freelance_profile.completed_projects = 1
                freelance_profile.rating = rating
        else:
            # Pas de note, mais on incrémente quand même le nombre de projets
            freelance_profile.completed_projects += 1
        
        # Stocker le feedback dans le champ description (optionnel)
        if feedback:
            # Ajouter le feedback à la description existante (limité)
            current_desc = freelance_profile.description or ""
            feedback_entry = f"\n\n[Feedback Mission #{mission_id}]: {feedback}"
            new_desc = current_desc + feedback_entry
            
            # Limiter à 500 caractères
            if len(new_desc) > 500:
                # Conserver les derniers 500 caractères
                new_desc = new_desc[-500:]
            
            freelance_profile.description = new_desc
        
        # Mettre à jour la mission
        mission.status = MissionStatus.COMPLETED
        mission.updated_at = datetime.utcnow()
        
        # Stocker l'évaluation dans la postulation pour référence
        if rating is not None:
            accepted_application.client_rating = rating
        if feedback:
            accepted_application.client_feedback = feedback
        
        db.session.commit()
        
        return jsonify({
            'message': 'Mission marquée comme complétée avec succès',
            'mission_id': mission.id,
            'status': mission.status.value,
            'freelance_updated': {
                'id': freelance_user.id,
                'new_rating': freelance_profile.rating,
                'completed_projects': freelance_profile.completed_projects
            },
            'feedback_added': bool(feedback),
            'rating_added': rating if rating is not None else None
        }), 200
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"❌ ERROR complete_mission: {str(e)}")
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
        mission.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Mission annulée',
            'mission_id': mission.id,
            'status': mission.status.value
        }), 200
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"❌ ERROR cancel_mission: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================
# ROUTES AJOUTÉES POUR PINIA STORE
# ============================

@missions_bp.route('/<int:mission_id>/completion', methods=['GET'])
@jwt_required()
@role_required(['CLIENT'])
def get_mission_completion_details(mission_id):
    """Récupérer les détails d'une mission complétée"""
    try:
        current_user_id = get_current_user_id()
        
        # Vérifier la mission
        mission = Mission.query.get_or_404(mission_id)
        if mission.client_id != current_user_id:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Vérifier que la mission est complétée
        if mission.status != MissionStatus.COMPLETED:
            return jsonify({'error': 'Cette mission n\'est pas encore complétée'}), 400
        
        # Récupérer la candidature acceptée
        accepted_application = Postulation.query.filter(
            and_(
                Postulation.mission_id == mission_id,
                Postulation.status == PostulationStatus.ACCEPTED
            )
        ).first()
        
        freelance_data = {}
        if accepted_application and accepted_application.freelance:
            freelance_profile = FreelanceProfile.query.filter_by(
                user_id=accepted_application.freelance_id
            ).first()
            if freelance_profile:
                freelance_data = {
                    'id': freelance_profile.user_id,
                    'full_name': freelance_profile.full_name,
                    'title': freelance_profile.title,
                    'rating': freelance_profile.rating,
                    'completed_projects': freelance_profile.completed_projects,
                    'description': freelance_profile.description
                }
        
        # Récupérer les livrables acceptés
        deliverables = Deliverable.query.filter(
            Deliverable.mission_id == mission_id,
            Deliverable.status == DeliverableStatus.ACCEPTED
        ).all() if hasattr(Deliverable, 'mission_id') else []
        
        # Calculer la durée
        duration = 0
        if mission.created_at and mission.updated_at:
            delta = mission.updated_at - mission.created_at
            duration = delta.days
        
        # Récupérer l'évaluation si elle existe
        rating = accepted_application.client_rating if accepted_application and hasattr(accepted_application, 'client_rating') else None
        feedback = accepted_application.client_feedback if accepted_application and hasattr(accepted_application, 'client_feedback') else None
        
        return jsonify({
            'mission': {
                'id': mission.id,
                'title': mission.title,
                'description': mission.description,
                'budget': mission.budget,
                'status': mission.status.value,
                'created_at': mission.created_at.isoformat() if mission.created_at else None,
                'completed_at': mission.updated_at.isoformat() if mission.updated_at else None,
                'duration': duration,
                'rating': rating,
                'feedback': feedback,
                'deadline': mission.deadline.isoformat() if mission.deadline else None,
                'required_skills': mission.required_skills or []
            },
            'freelance': freelance_data,
            'deliverables': [{
                'id': d.id,
                'title': d.title,
                'description': d.description,
                'file_url': d.file_url,
                'accepted_at': d.accepted_at.isoformat() if hasattr(d, 'accepted_at') and d.accepted_at else None,
                'created_at': d.created_at.isoformat() if d.created_at else None
            } for d in deliverables]
        }), 200
        
    except Exception as e:
        app.logger.error(f"❌ ERROR get_mission_completion_details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_mission_stats():
    """Récupérer les statistiques des missions d'un client"""
    try:
        current_user_id = get_current_user_id()
        
        missions = Mission.query.filter_by(client_id=current_user_id).all()
        
        # Compter les candidatures totales
        total_applications = 0
        for mission in missions:
            total_applications += mission.postulations.count() if hasattr(mission, 'postulations') else 0
        
        stats = {
            'total': len(missions),
            'draft': len([m for m in missions if m.status == MissionStatus.DRAFT]),
            'open': len([m for m in missions if m.status == MissionStatus.OPEN]),
            'in_progress': len([m for m in missions if m.status == MissionStatus.IN_PROGRESS]),
            'completed': len([m for m in missions if m.status == MissionStatus.COMPLETED]),
            'cancelled': len([m for m in missions if m.status == MissionStatus.CANCELLED]),
            'total_budget': sum(m.budget or 0 for m in missions),
            'average_budget': sum(m.budget or 0 for m in missions) / len(missions) if missions else 0,
            'total_applications': total_applications
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        app.logger.error(f"❌ ERROR get_mission_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================
# ROUTES D'EXPORT
# ============================

@missions_bp.route('/export', methods=['GET'])
@jwt_required()
@role_required(['CLIENT'])
def export_missions():
    """Exporter les missions au format CSV, Excel ou PDF"""
    try:
        current_user_id = get_current_user_id()
        format_type = request.args.get('format', 'csv').lower()
        mission_id = request.args.get('mission_id')
        
        # Base query
        query = Mission.query.filter_by(client_id=current_user_id)
        
        # Filtrer par mission spécifique si fourni
        if mission_id:
            query = query.filter_by(id=mission_id)
            if query.first() is None:
                return jsonify({'error': 'Mission non trouvée ou non autorisée'}), 404
        
        missions = query.order_by(Mission.created_at.desc()).all()
        
        if not missions:
            return jsonify({'error': 'Aucune mission à exporter'}), 404
        
        if format_type == 'csv':
            return export_to_csv(missions)
        elif format_type == 'excel':
            return export_to_excel(missions)
        elif format_type == 'pdf':
            return export_to_pdf(missions)
        else:
            return jsonify({'error': 'Format non supporté. Utilisez csv, excel ou pdf'}), 400
        
    except Exception as e:
        app.logger.error(f"Erreur export missions: {str(e)}")
        return jsonify({'error': str(e)}), 500


def export_to_csv(missions):
    """Exporter les missions en CSV"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)
    
    # En-têtes
    writer.writerow([
        'ID', 'Titre', 'Description', 'Statut', 'Budget (€)', 
        'Date création', 'Deadline', 'Compétences requises',
        'Client ID', 'Candidatures totales', 'Candidatures en attente'
    ])
    
    # Données
    for mission in missions:
        # Compétences formatées
        skills = ', '.join(mission.required_skills) if mission.required_skills else ''
        
        writer.writerow([
            mission.id,
            mission.title or '',
            (mission.description or '')[:500],
            mission.status.value,
            f"{mission.budget:.2f}" if mission.budget else '0.00',
            mission.created_at.strftime('%d/%m/%Y %H:%M') if mission.created_at else '',
            mission.deadline.strftime('%d/%m/%Y') if mission.deadline else '',
            skills,
            mission.client_id,
            mission.postulations.count() if hasattr(mission, 'postulations') else 0,
            len([p for p in mission.postulations.all() if p.status == PostulationStatus.PENDING]) if hasattr(mission, 'postulations') else 0
        ])
    
    # Convertir en bytes pour le téléchargement
    csv_bytes = output.getvalue().encode('utf-8-sig')  # BOM pour Excel
    
    return Response(
        csv_bytes,
        mimetype='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': f'attachment; filename="missions_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'}
    )


def export_to_excel(missions):
    """Exporter les missions en Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        
        # Préparer les données
        data = []
        for mission in missions:
            # Compétences formatées
            skills = ', '.join(mission.required_skills) if mission.required_skills else ''
            
            data.append({
                'ID': mission.id,
                'Titre': mission.title or '',
                'Description': mission.description or '',
                'Statut': mission.status.value,
                'Budget (€)': float(mission.budget) if mission.budget else 0.0,
                'Date création': mission.created_at.strftime('%d/%m/%Y %H:%M') if mission.created_at else '',
                'Deadline': mission.deadline.strftime('%d/%m/%Y') if mission.deadline else '',
                'Compétences requises': skills,
                'Client ID': mission.client_id,
                'Candidatures totales': mission.postulations.count() if hasattr(mission, 'postulations') else 0,
                'Candidatures en attente': len([p for p in mission.postulations.all() if p.status == PostulationStatus.PENDING]) if hasattr(mission, 'postulations') else 0
            })
        
        # Créer un DataFrame pandas
        df = pd.DataFrame(data)
        
        # Créer un writer Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Onglet principal
            df.to_excel(writer, sheet_name='Missions', index=False)
            
            # Onglet statistiques
            stats_data = {
                'Statistique': [
                    'Total missions',
                    'Budget total',
                    'Budget moyen',
                    'Missions en brouillon',
                    'Missions publiées',
                    'Missions en cours',
                    'Missions terminées',
                    'Missions annulées',
                    'Candidatures totales'
                ],
                'Valeur': [
                    len(missions),
                    f"{sum(m.budget or 0 for m in missions):.2f} €",
                    f"{(sum(m.budget or 0 for m in missions) / len(missions)) if missions else 0:.2f} €",
                    len([m for m in missions if m.status == MissionStatus.DRAFT]),
                    len([m for m in missions if m.status == MissionStatus.OPEN]),
                    len([m for m in missions if m.status == MissionStatus.IN_PROGRESS]),
                    len([m for m in missions if m.status == MissionStatus.COMPLETED]),
                    len([m for m in missions if m.status == MissionStatus.CANCELLED]),
                    sum(m.postulations.count() if hasattr(m, 'postulations') else 0 for m in missions)
                ]
            }
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
            
            # Ajuster la largeur des colonnes
            for sheet in writer.sheets:
                worksheet = writer.sheets[sheet]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        return Response(
            output.read(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="missions_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'}
        )
        
    except ImportError:
        return jsonify({'error': 'Bibliothèque pandas ou openpyxl manquante. Installez avec: pip install pandas openpyxl'}), 500
    except Exception as e:
        app.logger.error(f"Erreur export Excel: {str(e)}")
        return jsonify({'error': f'Erreur lors de la génération Excel: {str(e)}'}), 500


def export_to_pdf(missions):
    """Exporter les missions en PDF"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        import io
        
        # Créer le buffer pour le PDF
        buffer = io.BytesIO()
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Contenu du PDF
        story = []
        
        # Titre
        story.append(Paragraph("Rapport des Missions", title_style))
        story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Statistiques
        stats_data = [
            ['Statistiques Générales', ''],
            ['Total des missions', str(len(missions))],
            ['Budget total', f"{sum(m.budget or 0 for m in missions):.2f} €"],
            ['Budget moyen', f"{(sum(m.budget or 0 for m in missions) / len(missions)) if missions else 0:.2f} €"],
            ['Missions en brouillon', str(len([m for m in missions if m.status == MissionStatus.DRAFT]))],
            ['Missions publiées', str(len([m for m in missions if m.status == MissionStatus.OPEN]))],
            ['Missions en cours', str(len([m for m in missions if m.status == MissionStatus.IN_PROGRESS]))],
            ['Missions terminées', str(len([m for m in missions if m.status == MissionStatus.COMPLETED]))],
            ['Missions annulées', str(len([m for m in missions if m.status == MissionStatus.CANCELLED]))]
        ]
        
        stats_table = Table(stats_data, colWidths=[200, 100])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 30))
        
        # Tableau détaillé des missions
        if missions:
            # En-têtes
            table_data = [['ID', 'Titre', 'Statut', 'Budget', 'Date création', 'Deadline', 'Candidatures']]
            
            # Données
            for mission in missions:
                # Titre tronqué
                title = mission.title or ''
                if len(title) > 20:
                    title = title[:20] + '...'
                
                table_data.append([
                    str(mission.id),
                    title,
                    str(mission.status.value).replace('_', ' ').title(),
                    f"{mission.budget:.0f}€" if mission.budget else '0€',
                    mission.created_at.strftime('%d/%m/%y') if mission.created_at else '',
                    mission.deadline.strftime('%d/%m/%y') if mission.deadline else '',
                    str(mission.postulations.count() if hasattr(mission, 'postulations') else 0)
                ])
            
            # Créer le tableau
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))
            
            # Ajuster la largeur des colonnes
            col_widths = [30, 80, 50, 40, 50, 50, 50]
            table._argW = col_widths
            
            story.append(table)
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return Response(
            buffer.read(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="missions_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'}
        )
        
    except ImportError:
        return jsonify({'error': 'Bibliothèque reportlab manquante. Installez avec: pip install reportlab'}), 500
    except Exception as e:
        app.logger.error(f"Erreur export PDF: {str(e)}")
        return jsonify({'error': f'Erreur lors de la génération PDF: {str(e)}'}), 500


# Route spécifique pour l'export d'une mission unique
@missions_bp.route('/<int:mission_id>/export', methods=['GET'])
@jwt_required()
@role_required(['CLIENT'])
def export_single_mission(mission_id):
    """Exporter une mission spécifique"""
    try:
        current_user_id = get_current_user_id()
        format_type = request.args.get('format', 'pdf').lower()
        
        mission = Mission.query.filter_by(id=mission_id, client_id=current_user_id).first()
        if not mission:
            return jsonify({'error': 'Mission non trouvée ou non autorisée'}), 404
        
        # Rediriger vers la fonction principale avec l'ID de mission
        request.args = request.args.copy()
        request.args['mission_id'] = mission_id
        return export_missions()
        
    except Exception as e:
        app.logger.error(f"Erreur export mission {mission_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================
# NOUVELLES ROUTES POUR COMPATIBILITÉ PINIA
# ============================

@missions_bp.route('/<int:mission_id>/applications/accepted', methods=['GET'])
@jwt_required()
def get_accepted_freelance(mission_id):
    """Récupérer le freelance accepté pour une mission"""
    try:
        mission = Mission.query.get_or_404(mission_id)
        current_user_id = get_current_user_id()
        
        # Vérifier les permissions (client ou freelance concerné)
        if mission.client_id != current_user_id:
            # Vérifier si c'est le freelance assigné
            accepted_postulation = Postulation.query.filter_by(
                mission_id=mission_id,
                status=PostulationStatus.ACCEPTED
            ).first()
            
            if not accepted_postulation or accepted_postulation.freelance_id != current_user_id:
                return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Récupérer la postulation acceptée
        accepted_postulation = Postulation.query.filter_by(
            mission_id=mission_id,
            status=PostulationStatus.ACCEPTED
        ).first()
        
        if not accepted_postulation:
            return jsonify({'error': 'Aucun freelance accepté pour cette mission'}), 404
        
        freelance = User.query.get(accepted_postulation.freelance_id)
        freelance_profile = FreelanceProfile.query.filter_by(user_id=freelance.id).first()
        
        freelance_data = {
            'id': freelance.id,
            'email': freelance.email,
            'full_name': freelance_profile.full_name if freelance_profile else 'Inconnu',
            'title': freelance_profile.title if freelance_profile else '',
            'rating': freelance_profile.rating if freelance_profile else 0,
            'completed_projects': freelance_profile.completed_projects if freelance_profile else 0,
            'description': freelance_profile.description if freelance_profile else ''
        }
        
        return jsonify({
            'freelance': freelance_data,
            'postulation_id': accepted_postulation.id,
            'accepted_at': accepted_postulation.created_at.isoformat() if accepted_postulation.created_at else None
        }), 200
        
    except Exception as e:
        app.logger.error(f"❌ ERROR get_accepted_freelance: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================
# ROUTES POUR FREELANCE DASHBOARD
# ============================

@missions_bp.route('/saved', methods=['GET'])
@jwt_required()
@role_required(['FREELANCE'])
def get_saved_missions():
    """Récupérer les missions sauvegardées par le freelance"""
    try:
        current_user_id = get_current_user_id()
        user = User.query.get(current_user_id)
        
        if not user or not hasattr(user, 'saved_missions') or not user.saved_missions:
            return jsonify([]), 200
        
        # Récupérer les missions sauvegardées
        missions = Mission.query.filter(
            Mission.id.in_(user.saved_missions),
            Mission.status == MissionStatus.OPEN
        ).all()
        
        return jsonify([mission_to_dict(mission) for mission in missions]), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ ERROR get_saved_missions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/<int:mission_id>/save', methods=['POST'])
@jwt_required()
@role_required(['FREELANCE'])
def save_mission(mission_id):
    """Sauvegarder ou retirer une mission des favoris"""
    try:
        current_user_id = get_current_user_id()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Vérifier que la mission existe
        mission = Mission.query.get_or_404(mission_id)
        
        # Initialiser saved_missions si nécessaire
        if not hasattr(user, 'saved_missions'):
            user.saved_missions = []
        
        saved_missions = user.saved_missions or []
        
        if mission_id in saved_missions:
            # Retirer de la liste
            saved_missions = [mid for mid in saved_missions if mid != mission_id]
            message = 'Mission retirée des favoris'
        else:
            # Ajouter à la liste
            saved_missions.append(mission_id)
            message = 'Mission sauvegardée'
        
        user.saved_missions = saved_missions
        db.session.commit()
        
        return jsonify({
            'message': message,
            'mission_id': mission_id,
            'saved': mission_id in saved_missions,
            'saved_count': len(saved_missions)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ ERROR save_mission: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/profile/freelance/skills', methods=['GET'])
@jwt_required()
@role_required(['FREELANCE'])
def get_freelance_skills():
    """Récupérer les compétences du freelance"""
    try:
        current_user_id = get_current_user_id()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'skills': []}), 200
        
        # Récupérer les compétences
        skills = []
        
        # Depuis le champ skills de User
        if hasattr(user, 'skills') and user.skills:
            if isinstance(user.skills, list):
                skills = user.skills
            elif isinstance(user.skills, str):
                skills = [s.strip() for s in user.skills.split(',')]
        
        # Si vide, ajoutez des compétences par défaut
        if not skills:
            skills = ['JavaScript', 'Vue.js', 'React', 'Node.js', 'API REST', 'MongoDB']
        
        return jsonify({'skills': skills}), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ ERROR get_freelance_skills: {str(e)}")
        return jsonify({'error': str(e)}), 500

@missions_bp.route('/freelance/stats', methods=['GET'])
@jwt_required()
@role_required(['FREELANCE'])
def get_freelance_stats():
    """Récupérer les statistiques du freelance"""
    try:
        current_user_id = get_current_user_id()
        
        # Missions correspondant aux compétences
        user = User.query.get(current_user_id)
        user_skills = user.skills if hasattr(user, 'skills') and user.skills else []
        
        matching_missions = 0
        if user_skills:
            open_missions = Mission.query.filter_by(status=MissionStatus.OPEN).all()
            for mission in open_missions:
                if mission.required_skills and any(
                    skill in user_skills for skill in mission.required_skills
                ):
                    matching_missions += 1
        
        # Missions sauvegardées
        saved_count = len(user.saved_missions) if hasattr(user, 'saved_missions') and user.saved_missions else 0
        
        # Postulations
        applications = Postulation.query.filter_by(freelance_id=current_user_id).count()
        
        return jsonify({
            'matching_missions': matching_missions,
            'saved_missions': saved_count,
            'applications': applications,
            'user_skills': user_skills
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ ERROR get_freelance_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500