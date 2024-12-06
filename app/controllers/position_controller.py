from flask import Blueprint, request, jsonify
from models.position_model import Position
from utils.decorators import jwt_required, roles_required

position_bp = Blueprint("position", __name__)

@position_bp.route("/positions", methods=["GET"])
@jwt_required
@roles_required(roles=["admin", "user"])
def get_positions():
    positions = Position.get_all()
    return jsonify([position.serialize() for position in positions])

@position_bp.route("/positions/<int:id>", methods=["GET"])
@jwt_required
@roles_required(roles=["admin", "user"])
def get_position(id):
    position = Position.get_by_id(id)
    if position:
        return jsonify(position.serialize())
    return jsonify({"error": "Posición no encontrada"}), 404

@position_bp.route("/positions", methods=["POST"])
@jwt_required
@roles_required(roles=["admin"])
def create_position():
    data = request.json
    descripcion = data.get("descripcion")
    if not descripcion:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    position = Position(descripcion=descripcion)
    position.save()
    return jsonify(position.serialize()), 201

@position_bp.route("/positions/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(roles=["admin"])
def update_position(id):
    position = Position.get_by_id(id)
    if not position:
        return jsonify({"error": "Posición no encontrada"}), 404
    data = request.json
    descripcion = data.get("descripcion")
    position.update(descripcion=descripcion)
    return jsonify(position.serialize())

@position_bp.route("/positions/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(roles=["admin"])
def delete_position(id):
    position = Position.get_by_id(id)
    if not position:
        return jsonify({"error": "Posición no encontrada"}), 404
    position.delete()
    return "", 204