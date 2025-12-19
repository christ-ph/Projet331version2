from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import Chat, Message, User, Mission, ChatType
from sqlalchemy import select, or_, and_
from datetime import datetime

chat_bp = Blueprint('chat_bp', __name__)

# ============================
# 1. CRÉER OU RÉCUPÉRER UN CHAT DE MISSION
# ============================

from sqlalchemy import select
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from app.models import db, User, Mission, Chat, ChatType, Postulation, PostulationStatus

@chat_bp.route('/mission/<int:mission_id>', methods=['GET'])
@jwt_required()
def get_or_create_mission_chat(mission_id):
    """Récupère ou crée un chat pour une mission"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        
        # Récupérer la mission
        mission = db.session.get(Mission, mission_id)
        if not mission:
            return jsonify({"error": "Mission introuvable"}), 404
        
        # VÉRIFICATION SIMPLIFIÉE DES PERMISSIONS
        can_access = False
        user_role = user.role.name
        
        if user_role == 'CLIENT' and mission.client_id == user_id:
            can_access = True
        elif user_role == 'FREELANCE':
            # Vérifier si le freelance est assigné
            if mission.assigned_freelance_id == user_id:
                can_access = True
            else:
                # Vérifier les candidatures acceptées
                accepted_application = db.session.execute(
                    select(Postulation).filter(
                        Postulation.mission_id == mission_id,
                        Postulation.freelance_id == user_id,
                        Postulation.status == PostulationStatus.ACCEPTED
                    )
                ).scalars().first()
                
                if accepted_application:
                    can_access = True
                    # CORRECTION IMPORTANTE : Mettre à jour le freelance assigné
                    mission.assigned_freelance_id = user_id
                    db.session.commit()
        elif user_role == 'ADMIN':
            can_access = True
        
        if not can_access:
            return jsonify({
                "error": "Accès non autorisé à cette mission."
            }), 403
        
        # Chercher ou créer le chat
        chat = db.session.execute(
            select(Chat).filter_by(
                mission_id=mission_id, 
                chat_type=ChatType.MISSION
            )
        ).scalars().first()
        
        if not chat:
            # Créer le chat
            chat = Chat(
                chat_type=ChatType.MISSION,
                user1_id=mission.client_id,
                user2_id=mission.assigned_freelance_id,  # Peut être NULL
                mission_id=mission_id
            )
            db.session.add(chat)
            db.session.commit()
        else:
            # CORRECTION : Mettre à jour le user2_id si un freelance a été assigné
            if chat.user2_id != mission.assigned_freelance_id:
                chat.user2_id = mission.assigned_freelance_id
                db.session.commit()
        
        # Version simplifiée sans profils
        chat_data = chat.to_dict()
        chat_data['mission'] = {
            'id': mission.id,
            'title': mission.title,
            'status': mission.status.value,
            'assigned_freelance_id': mission.assigned_freelance_id
        }
        
        # Déterminer l'autre participant
        if user_role == 'CLIENT' and chat.user2_id:
            other_user = db.session.get(User, chat.user2_id)
            chat_data['other_participant'] = {
                'id': other_user.id,
                'email': other_user.email,
                'role': other_user.role.name
            }
        elif user_role == 'FREELANCE' and chat.user1_id:
            other_user = db.session.get(User, chat.user1_id)
            chat_data['other_participant'] = {
                'id': other_user.id,
                'email': other_user.email,
                'role': other_user.role.name
            }
        else:
            chat_data['other_participant'] = None
        
        chat_data['unread_count'] = chat.get_notification_count(user_id, user_role)
        
        return jsonify({"chat": chat_data}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur get_or_create_mission_chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500
# ============================
# 2. GÉRER LE CHAT DE SUPPORT
# ============================

@chat_bp.route('/support', methods=['GET', 'POST'])
@jwt_required()
def manage_support_chat():
    """Gère le chat de support (GET: récupérer, POST: créer)"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        
        if request.method == 'GET':
            # Récupérer le chat de support existant
            chat = db.session.execute(
                select(Chat).filter_by(
                    user1_id=user_id,
                    chat_type=ChatType.SUPPORT
                )
            ).scalars().first()
            
            if not chat:
                return jsonify({"chat": None}), 200
            
            # Récupérer les messages
            messages = db.session.execute(
                select(Message)
                .filter_by(chat_id=chat.id)
                .order_by(Message.created_at.asc())
            ).scalars().all()
            
            chat_data = chat.to_dict()
            chat_data['messages'] = [msg.to_dict() for msg in messages]
            chat_data['unread_count'] = chat.get_notification_count(user_id, user.role.name)
            
            return jsonify({"chat": chat_data}), 200
        
        elif request.method == 'POST':
            # Créer un nouveau chat de support
            data = request.get_json()
            subject = data.get('subject', 'Support')
            
            # Vérifier si un chat existe déjà
            existing_chat = db.session.execute(
                select(Chat).filter_by(
                    user1_id=user_id,
                    chat_type=ChatType.SUPPORT
                )
            ).scalars().first()
            
            if existing_chat:
                return jsonify({
                    "error": "Vous avez déjà un chat de support ouvert",
                    "chat_id": existing_chat.id
                }), 400
            
            # Créer le chat
            chat = Chat(
                chat_type=ChatType.SUPPORT,
                user1_id=user_id,
                user2_id=None,  # Admin assigné plus tard
                mission_id=None
            )
            db.session.add(chat)
            db.session.commit()
            
            return jsonify({
                "message": "Chat de support créé",
                "chat": chat.to_dict()
            }), 201
            
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

# ============================
# 3. ENVOYER UN MESSAGE
# ============================

@chat_bp.route('/<int:chat_id>/messages', methods=['POST'])
@jwt_required()
def send_message(chat_id):
    """Envoie un message dans un chat"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        
        chat = db.session.get(Chat, chat_id)
        if not chat:
            return jsonify({"error": "Chat introuvable"}), 404
        
        # Vérifier que l'utilisateur est participant du chat
        if chat.chat_type == ChatType.MISSION:
            if user_id not in [chat.user1_id, chat.user2_id]:
                return jsonify({"error": "Accès refusé"}), 403
        elif chat.chat_type == ChatType.SUPPORT:
            if user_id != chat.user1_id and user.role.name != 'ADMIN':
                return jsonify({"error": "Accès refusé"}), 403
        
        data = request.get_json()
        content = data.get('content')
        
        if not content or content.strip() == '':
            return jsonify({"error": "Le message ne peut pas être vide"}), 400
        
        # Créer le message
        message = Message(
            content=content.strip(),
            chat_id=chat_id,
            sender_id=user_id
        )
        db.session.add(message)
        
        # Mettre à jour la date du chat
        chat.updated_at = datetime.now()
        
        # Incrémenter le compteur du destinataire
        if chat.chat_type == ChatType.MISSION:
            # Détermine le destinataire
            recipient_id = chat.user2_id if user_id == chat.user1_id else chat.user1_id
            if recipient_id:
                recipient = db.session.get(User, recipient_id)
                if recipient:
                    chat.increment_notification(recipient.role.name)
        
        elif chat.chat_type == ChatType.SUPPORT:
            # Si c'est un user, notifier admin
            if user.role.name != 'ADMIN':
                chat.increment_notification('ADMIN')
            else:
                # Si c'est admin, notifier le user
                recipient = db.session.get(User, chat.user1_id)
                if recipient:
                    chat.increment_notification(recipient.role.name)
        
        db.session.commit()
        
        return jsonify({
            "message": "Message envoyé",
            "data": message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

# ============================
# 4. RÉCUPÉRER LES MESSAGES D'UN CHAT
# ============================

@chat_bp.route('/<int:chat_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(chat_id):
    """Récupère les messages d'un chat"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        
        chat = db.session.get(Chat, chat_id)
        if not chat:
            return jsonify({"error": "Chat introuvable"}), 404
        
        # Vérifier accès - CORRIGÉ POUR GÉRER LES NULL
        if chat.chat_type == ChatType.MISSION:
            # CORRECTION : Vérifier les IDs non-nulls uniquement
            participant_ids = []
            if chat.user1_id:
                participant_ids.append(chat.user1_id)
            if chat.user2_id:
                participant_ids.append(chat.user2_id)
            
            if user_id not in participant_ids:
                # Admins peuvent aussi voir les chats mission
                if user.role.name != 'ADMIN':
                    return jsonify({"error": "Accès refusé"}), 403
        
        elif chat.chat_type == ChatType.SUPPORT:
            if user_id != chat.user1_id and user.role.name != 'ADMIN':
                return jsonify({"error": "Accès refusé"}), 403
        
        # Récupérer les messages
        messages = db.session.execute(
            select(Message)
            .filter_by(chat_id=chat_id)
            .order_by(Message.created_at.asc())
        ).scalars().all()
        
        # Marquer les messages non lus comme lus
        unread_messages = db.session.execute(
            select(Message).filter(
                Message.chat_id == chat_id,
                Message.sender_id != user_id,
                Message.is_read == False
            )
        ).scalars().all()
        
        for msg in unread_messages:
            msg.mark_as_read()
        
        # Décrémenter le compteur (l'utilisateur consulte les messages)
        chat.decrement_notification(user.role.name)
        db.session.commit()
        
        # Ajouter l'info de l'expéditeur à chaque message
        messages_data = []
        for msg in messages:
            msg_data = msg.to_dict()
            sender = db.session.get(User, msg.sender_id)
            msg_data['sender'] = {
                'id': sender.id,
                'email': sender.email,
                'role': sender.role.name
            }
            messages_data.append(msg_data)
        
        return jsonify({
            "messages": messages_data,
            "chat": chat.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500
# ============================
# 5. CHECK STATUS (polling pour notifications)
# ============================

@chat_bp.route('/check-status', methods=['GET'])
@jwt_required()
def check_status():
    """Vérifie s'il y a de nouveaux messages dans les chats de l'utilisateur"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        
        # Récupérer tous les chats de l'utilisateur
        if user.role.name == 'ADMIN':
            # Admin voit tous les chats support
            chats = db.session.execute(
                select(Chat).filter_by(chat_type=ChatType.SUPPORT)
            ).scalars().all()
        else:
            # Utilisateur normal voit ses chats mission + son chat support
            mission_chats = db.session.execute(
                select(Chat).filter(
                    and_(
                        Chat.chat_type == ChatType.MISSION,
                        or_(Chat.user1_id == user_id, Chat.user2_id == user_id)
                    )
                )
            ).scalars().all()
            
            support_chat = db.session.execute(
                select(Chat).filter(
                    Chat.chat_type == ChatType.SUPPORT,
                    Chat.user1_id == user_id
                )
            ).scalars().first()
            
            chats = list(mission_chats) + ([support_chat] if support_chat else [])
        
        # Construire la réponse
        notifications = []
        total_unread = 0
        
        for chat in chats:
            if not chat:
                continue
                
            count = chat.get_notification_count(user_id, user.role.name)
            if count > 0:
                total_unread += count
                notifications.append({
                    "chat_id": chat.id,
                    "notification_count": count,
                    "chat_type": chat.chat_type.value,
                    "mission_id": chat.mission_id
                })
        
        return jsonify({
            "has_new_messages": total_unread > 0,
            "total_unread": total_unread,
            "notifications": notifications,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

# ============================
# 6. LISTE DES CHATS DE L'UTILISATEUR
# ============================

@chat_bp.route('/my-chats', methods=['GET'])
@jwt_required()
def get_my_chats():
    """Liste tous les chats de l'utilisateur avec infos détaillées"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        
        if user.role.name == 'ADMIN':
            # Admin: tous les chats support
            chats = db.session.execute(
                select(Chat)
                .filter_by(chat_type=ChatType.SUPPORT)
                .order_by(Chat.updated_at.desc())
            ).scalars().all()
        else:
            # Utilisateur: ses chats mission + support
            mission_chats = db.session.execute(
                select(Chat)
                .filter(
                    and_(
                        Chat.chat_type == ChatType.MISSION,
                        or_(Chat.user1_id == user_id, Chat.user2_id == user_id)
                    )
                )
                .order_by(Chat.updated_at.desc())
            ).scalars().all()
            
            support_chat = db.session.execute(
                select(Chat)
                .filter(
                    Chat.chat_type == ChatType.SUPPORT,
                    Chat.user1_id == user_id
                )
            ).scalars().first()
            
            chats = list(mission_chats) + ([support_chat] if support_chat else [])
        
        # Préparer la réponse détaillée
        chats_data = []
        for chat in chats:
            if not chat:
                continue
                
            chat_data = chat.to_dict()
            
            # Dernier message
            last_message = db.session.execute(
                select(Message)
                .filter_by(chat_id=chat.id)
                .order_by(Message.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()
            
            if last_message:
                sender = db.session.get(User, last_message.sender_id)
                chat_data['last_message'] = {
                    **last_message.to_dict(),
                    'sender': {
                        'id': sender.id,
                        'email': sender.email
                    }
                }
            
            # Informations de l'autre participant (pour mission)
            if chat.chat_type == ChatType.MISSION:
                if chat.user1_id == user_id:
                    other_user_id = chat.user2_id
                else:
                    other_user_id = chat.user1_id
                
                if other_user_id:
                    other_user = db.session.get(User, other_user_id)
                    chat_data['other_user'] = {
                        'id': other_user.id,
                        'email': other_user.email,
                        'role': other_user.role.name
                    }
                
                # Infos mission
                if chat.mission_id:
                    mission = db.session.get(Mission, chat.mission_id)
                    chat_data['mission'] = {
                        'id': mission.id,
                        'title': mission.title,
                        'status': mission.status.value
                    }
            
            # Notifications non lues
            chat_data['unread_count'] = chat.get_notification_count(user_id, user.role.name)
            
            chats_data.append(chat_data)
        
        return jsonify({
            "chats": chats_data,
            "total": len(chats_data)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

# ============================
# 7. MARQUER UN CHAT COMME LU
# ============================

@chat_bp.route('/<int:chat_id>/read', methods=['POST'])
@jwt_required()
def mark_chat_as_read(chat_id):
    """Marque tous les messages d'un chat comme lus"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        
        chat = db.session.get(Chat, chat_id)
        if not chat:
            return jsonify({"error": "Chat introuvable"}), 404
        
        # Vérifier accès
        if chat.chat_type == ChatType.MISSION:
            if user_id not in [chat.user1_id, chat.user2_id]:
                return jsonify({"error": "Accès refusé"}), 403
        elif chat.chat_type == ChatType.SUPPORT:
            if user_id != chat.user1_id and user.role.name != 'ADMIN':
                return jsonify({"error": "Accès refusé"}), 403
        
        # Marquer tous les messages non lus comme lus
        unread_messages = db.session.execute(
            select(Message).filter(
                Message.chat_id == chat_id,
                Message.sender_id != user_id,
                Message.is_read == False
            )
        ).scalars().all()
        
        for msg in unread_messages:
            msg.mark_as_read()
        
        # Réinitialiser les notifications
        chat.decrement_notification(user.role.name)
        db.session.commit()
        
        return jsonify({
            "message": "Tous les messages ont été marqués comme lus",
            "unread_count": 0
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

# ============================
# 8. SUPPRIMER UN MESSAGE
# ============================

@chat_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """Supprime un message (seulement par l'expéditeur ou admin)"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        
        message = db.session.get(Message, message_id)
        if not message:
            return jsonify({"error": "Message introuvable"}), 404
        
        # Vérifier les permissions
        if user.role.name != 'ADMIN' and message.sender_id != user_id:
            return jsonify({"error": "Vous ne pouvez supprimer que vos propres messages"}), 403
        
        # Supprimer le message
        db.session.delete(message)
        db.session.commit()
        
        return jsonify({
            "message": "Message supprimé",
            "message_id": message_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

# ============================
# 9. RÉCUPÉRER UN CHAT SPÉCIFIQUE
# ============================

@chat_bp.route('/<int:chat_id>', methods=['GET'])
@jwt_required()
def get_chat(chat_id):
    """Récupère les détails d'un chat spécifique"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        
        chat = db.session.get(Chat, chat_id)
        if not chat:
            return jsonify({"error": "Chat introuvable"}), 404
        
        # Vérifier accès
        if chat.chat_type == ChatType.MISSION:
            if user_id not in [chat.user1_id, chat.user2_id]:
                return jsonify({"error": "Accès refusé"}), 403
        elif chat.chat_type == ChatType.SUPPORT:
            if user_id != chat.user1_id and user.role.name != 'ADMIN':
                return jsonify({"error": "Accès refusé"}), 403
        
        # Récupérer les infos complémentaires
        chat_data = chat.to_dict()
        
        # Ajouter les infos des utilisateurs
        user1 = db.session.get(User, chat.user1_id) if chat.user1_id else None
        user2 = db.session.get(User, chat.user2_id) if chat.user2_id else None
        
        chat_data['user1'] = {
            'id': user1.id if user1 else None,
            'email': user1.email if user1 else None,
            'role': user1.role.name if user1 else None
        }
        
        chat_data['user2'] = {
            'id': user2.id if user2 else None,
            'email': user2.email if user2 else None,
            'role': user2.role.name if user2 else None
        }
        
        # Infos mission si chat de mission
        if chat.mission_id:
            mission = db.session.get(Mission, chat.mission_id)
            if mission:
                chat_data['mission'] = {
                    'id': mission.id,
                    'title': mission.title,
                    'status': mission.status.value,
                    'client_id': mission.client_id,
                    'freelance_id': mission.assigned_freelance_id
                }
        
        # Notifications pour cet utilisateur
        chat_data['unread_count'] = chat.get_notification_count(user_id, user.role.name)
        
        return jsonify({"chat": chat_data}), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500
    

@chat_bp.route('/mission/<int:mission_id>/assign-freelance', methods=['POST'])
@jwt_required()
def assign_freelance_to_chat(mission_id):
    """Assigne un freelance au chat de mission (quand sa candidature est acceptée)"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user or user.role.name != 'CLIENT':
            return jsonify({"error": "Accès non autorisé"}), 403
        
        # Récupérer la mission
        mission = db.session.get(Mission, mission_id)
        if not mission or mission.client_id != user_id:
            return jsonify({"error": "Mission introuvable ou accès refusé"}), 404
        
        data = request.get_json()
        freelance_id = data.get('freelance_id')
        
        if not freelance_id:
            return jsonify({"error": "ID du freelance requis"}), 400
        
        # Vérifier que la candidature existe et est acceptée
        accepted_application = db.session.execute(
            select(Postulation).filter(
                Postulation.mission_id == mission_id,
                Postulation.freelance_id == freelance_id,
                Postulation.status == PostulationStatus.ACCEPTED
            )
        ).scalars().first()
        
        if not accepted_application:
            return jsonify({"error": "Candidature acceptée non trouvée"}), 400
        
        # Mettre à jour la mission
        mission.assigned_freelance_id = freelance_id
        mission.status = MissionStatus.IN_PROGRESS
        
        # Chercher le chat existant
        chat = db.session.execute(
            select(Chat).filter_by(
                mission_id=mission_id,
                chat_type=ChatType.MISSION
            )
        ).scalars().first()
        
        if chat:
            # Mettre à jour le chat
            chat.user2_id = freelance_id
        else:
            # Créer un nouveau chat
            chat = Chat(
                chat_type=ChatType.MISSION,
                user1_id=mission.client_id,
                user2_id=freelance_id,
                mission_id=mission_id
            )
            db.session.add(chat)
        
        db.session.commit()
        
        return jsonify({
            "message": "Freelance assigné avec succès",
            "chat": chat.to_dict(),
            "mission": {
                'id': mission.id,
                'assigned_freelance_id': mission.assigned_freelance_id,
                'status': mission.status.value
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500