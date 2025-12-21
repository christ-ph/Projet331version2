from functools import wraps
from flask import jsonify, g, request
from flask_jwt_extended import (
    get_jwt_identity,
    verify_jwt_in_request
)
from flask_jwt_extended.exceptions import (
    NoAuthorizationError,
    InvalidHeaderError,
    JWTDecodeError
)

from app.models import User
from app import db


def role_required(roles):
    """
    Décorateur pour restreindre l'accès selon le rôle utilisateur.
    Exemple:
        @role_required("ADMIN")
        @role_required(["ADMIN", "MANAGER"])
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # 1️⃣ Vérifier le JWT
                verify_jwt_in_request()

                # 2️⃣ Récupérer l'ID utilisateur
                user_id_raw = get_jwt_identity()

                print(f"🔍 role_required: user_id_raw = {user_id_raw}")
                print(f"🔍 Authorization = {request.headers.get('Authorization')}")

                if not user_id_raw:
                    return jsonify({"msg": "Token invalide ou expiré"}), 401

                try:
                    user_id = int(user_id_raw)
                except (TypeError, ValueError):
                    return jsonify({"msg": "Identifiant utilisateur invalide"}), 400

                # 3️⃣ Charger l'utilisateur
                user = db.session.get(User, user_id)

                if not user:
                    return jsonify({"msg": "Utilisateur non trouvé"}), 404

                if not user.role:
                    return jsonify({"msg": "Rôle utilisateur non défini"}), 403

                user_role = user.role.name
                print(f"🔍 Rôle utilisateur = {user_role}")

                # 4️⃣ Vérifier les rôles autorisés
                allowed_roles = [roles] if isinstance(roles, str) else roles

                if user_role not in allowed_roles:
                    print(f"🚫 Accès refusé: {user_role} ∉ {allowed_roles}")
                    return jsonify({
                        "msg": f"Accès refusé : rôle {user_role} insuffisant",
                        "required_roles": allowed_roles
                    }), 403

                # 5️⃣ Stocker l'utilisateur pour réutilisation
                g.current_user = user

                return fn(*args, **kwargs)

            except NoAuthorizationError:
                return jsonify({"msg": "Token JWT manquant"}), 401
            except InvalidHeaderError:
                return jsonify({"msg": "En-tête Authorization invalide"}), 401
            except JWTDecodeError:
                return jsonify({"msg": "Token JWT invalide"}), 401
            except Exception as e:
                print(f"❌ ERROR role_required: {str(e)}")
                return jsonify({"msg": "Erreur d'authentification"}), 500

        return decorator
    return wrapper


def is_active_required(fn):
    """
    Décorateur pour vérifier que le compte utilisateur est actif.
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        try:
            # 1️⃣ Vérifier le JWT
            verify_jwt_in_request()

            # 2️⃣ Récupérer l'ID utilisateur
            user_id_raw = get_jwt_identity()

            if not user_id_raw:
                return jsonify({"msg": "Token invalide ou expiré"}), 401

            try:
                user_id = int(user_id_raw)
            except (TypeError, ValueError):
                return jsonify({"msg": "Identifiant utilisateur invalide"}), 400

            # 3️⃣ Charger l'utilisateur
            user = db.session.get(User, user_id)

            if not user:
                return jsonify({"msg": "Utilisateur non trouvé"}), 404

            # 4️⃣ Vérifier si le compte est actif
            if not user.is_active:
                return jsonify({"msg": "Compte désactivé"}), 403

            # 5️⃣ Stocker l'utilisateur
            g.current_user = user

            return fn(*args, **kwargs)

        except NoAuthorizationError:
            return jsonify({"msg": "Token JWT manquant"}), 401
        except InvalidHeaderError:
            return jsonify({"msg": "En-tête Authorization invalide"}), 401
        except JWTDecodeError:
            return jsonify({"msg": "Token JWT invalide"}), 401
        except Exception as e:
            print(f"❌ ERROR is_active_required: {str(e)}")
            return jsonify({"msg": "Erreur d'authentification"}), 500

    return decorator

