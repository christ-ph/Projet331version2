# app/routes/freelancers.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from datetime import datetime

from app import db
from app.models import User, Role, FreelanceProfile, Profile, Mission, Postulation, PostulationStatus
from app.utils import role_required

freelancers_bp = Blueprint('freelancers_bp', __name__)

def freelance_to_dict(freelancer, include_details=False):
    """Convertit un freelance en dictionnaire pour la réponse JSON"""
    user = freelancer.user
    profile = freelancer
    
    base_data = {
        'id': user.id,
        'email': user.email,
        'full_name': profile.full_name,
        'title': profile.title,
        'rating': profile.rating or 0,
        'completed_projects': profile.completed_projects or 0,
        'hourly_rate': profile.hourly_rate,
        'experience_years': profile.experience_years,
        'availability': profile.availability,
        'skills': profile.skills or [],
        'languages': profile.languages or [],
        'description': profile.description,
        'bio': freelancer.bio if hasattr(freelancer, 'bio') else None,
        'country': freelancer.country,
        'city': freelancer.city,
        'url_photo': freelancer.url_photo
    }
    
    if include_details:
        # Calculer le taux de réussite
        accepted_postulations = Postulation.query.filter_by(
            freelance_id=user.id,
            status=PostulationStatus.ACCEPTED
        ).count()
        
        total_postulations = Postulation.query.filter_by(
            freelance_id=user.id
        ).count()
        
        success_rate = (accepted_postulations / total_postulations * 100) if total_postulations > 0 else 0
        
        base_data.update({
            'phone': freelancer.phone,
            'address': freelancer.address,
            'success_rate': round(success_rate, 1),
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_connection': user.last_connection_at.isoformat() if user.last_connection_at else None
        })
    
    return base_data

@freelancers_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_freelancers():
    """Récupère tous les freelances de la plateforme"""
    try:
        # Vérifier que l'utilisateur est authentifié
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Utilisateur non authentifié'}), 401
        
        # Récupérer tous les utilisateurs avec le rôle FREELANCE
        freelance_role = Role.query.filter_by(name='FREELANCE').first()
        if not freelance_role:
            return jsonify({'error': 'Rôle FREELANCE non trouvé'}), 404
        
        # Récupérer tous les freelances avec leurs profils
        freelancers = User.query.filter_by(role_id=freelance_role.id, is_active=True).all()
        
        freelancers_data = []
        for freelancer in freelancers:
            freelance_profile = FreelanceProfile.query.filter_by(user_id=freelancer.id).first()
            if freelance_profile:
                freelancers_data.append(freelance_to_dict(freelance_profile))
        
        # Tri par défaut : meilleure note d'abord
        freelancers_data.sort(key=lambda x: x['rating'], reverse=True)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        start = (page - 1) * per_page
        end = start + per_page
        paginated_freelancers = freelancers_data[start:end]
        
        return jsonify({
            'freelancers': paginated_freelancers,
            'total': len(freelancers_data),
            'page': page,
            'per_page': per_page,
            'pages': (len(freelancers_data) + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ ERROR get_all_freelancers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@freelancers_bp.route('/<int:freelancer_id>', methods=['GET'])
@jwt_required()
def get_freelancer(freelancer_id):
    """Récupère les détails d'un freelance spécifique"""
    try:
        # Vérifier que l'utilisateur est authentifié
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Utilisateur non authentifié'}), 401
        
        # Récupérer le freelance
        freelancer = User.query.get_or_404(freelancer_id)
        
        # Vérifier que c'est bien un freelance
        if freelancer.role.name != 'FREELANCE':
            return jsonify({'error': 'Utilisateur n\'est pas un freelance'}), 400
        
        # Récupérer le profil freelance
        freelance_profile = FreelanceProfile.query.filter_by(user_id=freelancer_id).first()
        if not freelance_profile:
            return jsonify({'error': 'Profil freelance non trouvé'}), 404
        
        # Récupérer les missions acceptées
        accepted_missions = Postulation.query.filter_by(
            freelance_id=freelancer_id,
            status=PostulationStatus.ACCEPTED
        ).all()
        
        missions_data = []
        for postulation in accepted_missions:
            mission = postulation.mission
            if mission:
                missions_data.append({
                    'id': mission.id,
                    'title': mission.title,
                    'budget': mission.budget,
                    'status': mission.status.value,
                    'completed_at': mission.updated_at.isoformat() if mission.status.value == 'completed' else None
                })
        
        freelance_data = freelance_to_dict(freelance_profile, include_details=True)
        freelance_data['accepted_missions'] = missions_data
        
        return jsonify(freelance_data), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ ERROR get_freelancer: {str(e)}")
        return jsonify({'error': str(e)}), 500

@freelancers_bp.route('/search', methods=['GET'])
@jwt_required()
def search_freelancers():
    """Recherche de freelances avec filtres"""
    try:
        # Vérifier que l'utilisateur est authentifié
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Utilisateur non authentifié'}), 401
        
        # Récupérer le rôle FREELANCE
        freelance_role = Role.query.filter_by(name='FREELANCE').first()
        if not freelance_role:
            return jsonify({'error': 'Rôle FREELANCE non trouvé'}), 404
        
        # Requête de base
        query = User.query.filter_by(role_id=freelance_role.id, is_active=True)
        
        # Filtrage par compétences
        skills = request.args.get('skills')
        if skills:
            try:
                skills_list = [s.strip().lower() for s in skills.split(',')]
                # Joindre avec le profil freelance
                from sqlalchemy.orm import aliased
                freelance_profile_alias = aliased(FreelanceProfile)
                
                query = query.join(freelance_profile_alias, User.id == freelance_profile_alias.user_id)
                
                # Rechercher dans les compétences
                conditions = []
                for skill in skills_list:
                    conditions.append(freelance_profile_alias.skills.contains([skill]))
                
                if conditions:
                    query = query.filter(or_(*conditions))
            except:
                pass
        
        # Filtrage par taux horaire
        min_rate = request.args.get('min_rate')
        if min_rate:
            try:
                from sqlalchemy.orm import aliased
                freelance_profile_alias = aliased(FreelanceProfile)
                query = query.join(freelance_profile_alias, User.id == freelance_profile_alias.user_id)
                query = query.filter(freelance_profile_alias.hourly_rate >= float(min_rate))
            except:
                pass
        
        max_rate = request.args.get('max_rate')
        if max_rate:
            try:
                from sqlalchemy.orm import aliased
                freelance_profile_alias = aliased(FreelanceProfile)
                query = query.join(freelance_profile_alias, User.id == freelance_profile_alias.user_id)
                query = query.filter(freelance_profile_alias.hourly_rate <= float(max_rate))
            except:
                pass
        
        # Filtrage par note minimale
        min_rating = request.args.get('min_rating')
        if min_rating:
            try:
                from sqlalchemy.orm import aliased
                freelance_profile_alias = aliased(FreelanceProfile)
                query = query.join(freelance_profile_alias, User.id == freelance_profile_alias.user_id)
                query = query.filter(freelance_profile_alias.rating >= float(min_rating))
            except:
                pass
        
        # Filtrage par expérience minimale
        min_experience = request.args.get('min_experience')
        if min_experience:
            try:
                from sqlalchemy.orm import aliased
                freelance_profile_alias = aliased(FreelanceProfile)
                query = query.join(freelance_profile_alias, User.id == freelance_profile_alias.user_id)
                query = query.filter(freelance_profile_alias.experience_years >= int(min_experience))
            except:
                pass
        
        # Filtrage par disponibilité
        availability = request.args.get('availability')
        if availability:
            try:
                from sqlalchemy.orm import aliased
                freelance_profile_alias = aliased(FreelanceProfile)
                query = query.join(freelance_profile_alias, User.id == freelance_profile_alias.user_id)
                query = query.filter(freelance_profile_alias.availability.ilike(f'%{availability}%'))
            except:
                pass
        
        # Filtrage par mots-clés
        keywords = request.args.get('q')
        if keywords:
            search = f"%{keywords}%"
            from sqlalchemy.orm import aliased
            freelance_profile_alias = aliased(FreelanceProfile)
            query = query.join(freelance_profile_alias, User.id == freelance_profile_alias.user_id)
            query = query.filter(
                or_(
                    freelance_profile_alias.full_name.ilike(search),
                    freelance_profile_alias.title.ilike(search),
                    freelance_profile_alias.description.ilike(search)
                )
            )
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        freelancers_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Transformer les résultats
        freelancers_data = []
        for freelancer in freelancers_paginated.items:
            freelance_profile = FreelanceProfile.query.filter_by(user_id=freelancer.id).first()
            if freelance_profile:
                freelancers_data.append(freelance_to_dict(freelance_profile))
        
        return jsonify({
            'freelancers': freelancers_data,
            'total': freelancers_paginated.total,
            'page': freelancers_paginated.page,
            'per_page': freelancers_paginated.per_page,
            'pages': freelancers_paginated.pages
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ ERROR search_freelancers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@freelancers_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_freelancers_stats():
    """Récupérer les statistiques générales des freelances"""
    try:
        # Vérifier que l'utilisateur est authentifié
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Utilisateur non authentifié'}), 401
        
        # Récupérer le rôle FREELANCE
        freelance_role = Role.query.filter_by(name='FREELANCE').first()
        if not freelance_role:
            return jsonify({'error': 'Rôle FREELANCE non trouvé'}), 404
        
        # Compter les freelances actifs
        total_freelancers = User.query.filter_by(role_id=freelance_role.id, is_active=True).count()
        
        # Récupérer les profils freelance pour les statistiques
        freelance_profiles = FreelanceProfile.query.all()
        
        # Calculer les statistiques
        if freelance_profiles:
            total_completed_projects = sum(fp.completed_projects or 0 for fp in freelance_profiles)
            average_rating = sum(fp.rating or 0 for fp in freelance_profiles) / len(freelance_profiles) if freelance_profiles else 0
            average_hourly_rate = sum(fp.hourly_rate or 0 for fp in freelance_profiles if fp.hourly_rate) / len([fp for fp in freelance_profiles if fp.hourly_rate]) if [fp for fp in freelance_profiles if fp.hourly_rate] else 0
            average_experience = sum(fp.experience_years or 0 for fp in freelance_profiles) / len(freelance_profiles) if freelance_profiles else 0
        else:
            total_completed_projects = 0
            average_rating = 0
            average_hourly_rate = 0
            average_experience = 0
        
        # Compter par disponibilité
        availability_counts = {}
        for fp in freelance_profiles:
            if fp.availability:
                avail = fp.availability.lower()
                availability_counts[avail] = availability_counts.get(avail, 0) + 1
        
        # Top compétences
        all_skills = []
        for fp in freelance_profiles:
            if fp.skills and isinstance(fp.skills, list):
                all_skills.extend(fp.skills)
        
        from collections import Counter
        skill_counts = Counter(all_skills)
        top_skills = [{'skill': skill, 'count': count} for skill, count in skill_counts.most_common(10)]
        
        stats = {
            'total_freelancers': total_freelancers,
            'total_completed_projects': total_completed_projects,
            'average_rating': round(average_rating, 1),
            'average_hourly_rate': round(average_hourly_rate, 2),
            'average_experience_years': round(average_experience, 1),
            'availability_distribution': availability_counts,
            'top_skills': top_skills
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ ERROR get_freelancers_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@freelancers_bp.route('/recommended', methods=['GET'])
@jwt_required()
@role_required(['CLIENT'])
def get_recommended_freelancers():
    """Récupérer les freelances recommandés pour un client"""
    try:
        current_user_id = get_jwt_identity()
        
        # Récupérer les compétences des missions du client
        client_missions = Mission.query.filter_by(client_id=current_user_id).all()
        
        # Extraire toutes les compétences requises
        all_required_skills = []
        for mission in client_missions:
            if mission.required_skills and isinstance(mission.required_skills, list):
                all_required_skills.extend([skill.lower() for skill in mission.required_skills])
        
        # Récupérer le rôle FREELANCE
        freelance_role = Role.query.filter_by(name='FREELANCE').first()
        if not freelance_role:
            return jsonify({'error': 'Rôle FREELANCE non trouvé'}), 404
        
        # Récupérer tous les freelances actifs
        freelancers = User.query.filter_by(role_id=freelance_role.id, is_active=True).all()
        
        freelancers_with_match = []
        for freelancer in freelancers:
            freelance_profile = FreelanceProfile.query.filter_by(user_id=freelancer.id).first()
            if freelance_profile:
                # Calculer le score de correspondance
                match_score = 0
                if freelance_profile.skills and isinstance(freelance_profile.skills, list):
                    freelance_skills = [skill.lower() for skill in freelance_profile.skills]
                    
                    # Compter les correspondances
                    matching_skills = set(all_required_skills) & set(freelance_skills)
                    match_score = len(matching_skills) * 10
                    
                    # Bonus pour la note
                    match_score += (freelance_profile.rating or 0) * 2
                    
                    # Bonus pour l'expérience
                    match_score += (freelance_profile.experience_years or 0) * 1
                
                freelancers_with_match.append({
                    'freelancer': freelance_to_dict(freelance_profile),
                    'match_score': match_score
                })
        
        # Trier par score de correspondance
        freelancers_with_match.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Ne prendre que les 10 meilleurs
        recommended = freelancers_with_match[:10]
        
        return jsonify([item['freelancer'] for item in recommended]), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ ERROR get_recommended_freelancers: {str(e)}")
        return jsonify({'error': str(e)}), 500