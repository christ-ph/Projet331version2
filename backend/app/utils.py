# app/utils.py - VERSION CORRIGÉE
from functools import wraps
from flask import jsonify, g, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, JWTDecodeError
from app.models import User
from app import db

def role_required(roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # 1. Vérifier le JWT
                verify_jwt_in_request()
                
                # 2. Récupérer l'ID utilisateur
                user_id_raw = get_jwt_identity()
                
                print(f"🔍 role_required: user_id_raw = {user_id_raw}")
                print(f"🔍 role_required: Authorization header = {request.headers.get('Authorization')}")
                
                if not user_id_raw:
                    return jsonify({"msg": "Token invalide ou expiré"}), 401
                
                # Convertir en int
                try:
                    user_id = int(user_id_raw)
                except (TypeError, ValueError):
                    return jsonify({"msg": "Format d'identifiant utilisateur invalide"}), 400
                
                # 3. Récupérer l'utilisateur
                user = db.session.get(User, user_id)
                
                print(f"🔍 role_required: user found = {user}")
                
                if not user:
                    return jsonify({"msg": "Utilisateur non trouvé"}), 404
                
                print(f"🔍 role_required: user role = {user.role.name}")
                
                # 4. Vérifier le rôle
                user_role = user.role.name
                
                # Si roles est un string, le convertir en liste
                if isinstance(roles, str):
                    allowed_roles = [roles]
                else:
                    allowed_roles = roles
                
                if user_role not in allowed_roles:
                    print(f"🚫 Accès refusé: rôle {user_role} pour route nécessitant {allowed_roles}")
                    return jsonify({"msg": f"Accès refusé : rôle {user_role} insuffisant. Requiert: {allowed_roles}"}), 403
                
                # 5. Stocker l'utilisateur dans g pour réutilisation
                g.current_user = user
                
                # 6. Exécuter la fonction
                return fn(*args, **kwargs)
                
            except NoAuthorizationError as e:
                print(f"❌ NoAuthorizationError: {str(e)}")
                return jsonify({"msg": "Token JWT manquant dans les en-têtes"}), 401
            except InvalidHeaderError as e:
                print(f"❌ InvalidHeaderError: {str(e)}")
                return jsonify({"msg": "En-tête Authorization invalide"}), 401
            except JWTDecodeError as e:
                print(f"❌ JWTDecodeError: {str(e)}")
                return jsonify({"msg": "Token JWT invalide"}), 401
            except Exception as e:
                print(f"❌ ERROR dans role_required: {str(e)}")
                return jsonify({"msg": "Erreur d'authentification"}), 500
        
        return decorator
    return wrapper