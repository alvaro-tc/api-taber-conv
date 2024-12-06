from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    current_user,
    get_jwt_identity,
)

from models.user_model import User
from models.token_block_list import TokenBlocklist
from schemas.user_schema import UserSchema
import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
user_bp = Blueprint("user", __name__)


@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    roles = data.get("roles", ["user"])
    
    if not email or not password:
        return jsonify({"error": "Se requieren email y contraseña"}), 400

    existing_user = User.find_by_email(email)
    if existing_user:
        return jsonify({"error": "El usuario ya existe"}), 409
    
    
    new_user = User(email=email, roles=roles, password=password)
    new_user.save()

    return jsonify({"message": "Usuario creado exitosamente"}), 201

@user_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.find_by_email(email)
    if user and user.check_password(password):
        roles = user.get_roles()  # Asegúrate de que esto devuelva una lista.
        
        # Usa una lista de roles como parte de la identidad
        identity = json.dumps({"email": user.email, "roles": roles})
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        logger.info("Usuario autenticado: %s con roles: %s", email, roles)

        return (
            jsonify(
                {
                    "message": "Ha accedido correctamente",
                    "tokens": {"access": access_token, "refresh": refresh_token},
                }
            ),
            200,
        )

    logger.warning("Credenciales inválidas para el usuario: %s", email)
    return jsonify({"error": "Credenciales inválidas"}), 400


@user_bp.route("/whoami", methods=["GET"])
@jwt_required()
def whoami():
    return jsonify(
        {
            "message": "message",
            "user_details": {
                "email": current_user.email,
                "roles": json.loads(current_user.roles),
                "cellphone": current_user.cellphone,
                "lastname": current_user.lastname,
                "name": current_user.name,
                "id": current_user.id,
                
            },
        }
    )
    
    
@user_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_access():
    identity = get_jwt_identity()

    new_access_token = create_access_token(identity=identity)

    return jsonify({"access_token": new_access_token})

@user_bp.route('/logout', methods=["GET"])
@jwt_required(verify_type=False) 
def logout_user():
    jwt = get_jwt()

    jti = jwt['jti']
    token_type = jwt['type']

    token_b = TokenBlocklist(jti=jti)

    token_b.save()

    return jsonify({"message": f"{token_type} token removido exitosamente"}) , 200



@user_bp.route("/users", methods=["GET"])
@jwt_required()
def get_all_users():
    claims = get_jwt()

    if claims.get("admin") == True:
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=3, type=int)
        
        users = User.query.paginate(page=page, per_page=per_page)
        result = UserSchema().dump(users, many=True)
        
        return (
            jsonify(
                {
                    "users": result,
                }
            ),
            200,
        )

    return jsonify({"message": "No tienes autorizacion para acceder a esto"}), 401


@user_bp.route("/user", methods=["GET"])
@jwt_required()
def get_current_user():
    user = current_user
    user_data = UserSchema().dump(user)
    print(user_data)
    return jsonify({"user": user_data}), 200



@user_bp.route("/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    user_data = UserSchema().dump(user)
    return jsonify({"user": user_data}), 200


@user_bp.route("/user/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    roles = data.get("roles")
    name = data.get("name")
    lastname = data.get("lastname")
    cellphone = data.get("cellphone")

    if email:
        user.email = email
    if password:
        user.set_password(password)
    if roles:
        user.roles = roles
    if name:
        user.name = name
    if lastname:
        user.lastname = lastname
    if cellphone:
        user.cellphone = cellphone

    user.save()

    user_data = UserSchema().dump(user)
    return jsonify({"user": user_data}), 200

@user_bp.route("/user", methods=["PUT"])
@jwt_required()
def update_current_user():
    user = current_user
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    roles = data.get("roles")
    name = data.get("name")
    lastname = data.get("lastname")
    cellphone = data.get("cellphone")

    if email:
        user.email = email
    if password:
        user.set_password(password)
    if roles:
        user.roles = roles
    if name:
        user.name = name
    if lastname:
        user.lastname = lastname
    if cellphone:
        user.cellphone = cellphone

    user.save()

    user_data = UserSchema().dump(user)
    return jsonify({"user": user_data}), 200


@user_bp.route("/user/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    user.delete()
    return jsonify({"message": "Usuario eliminado exitosamente"}), 200


@user_bp.route("/user", methods=["DELETE"])
@jwt_required()
def delete_current_user():
    user = current_user
    user.delete()
    return jsonify({"message": "Usuario eliminado exitosamente"}), 200