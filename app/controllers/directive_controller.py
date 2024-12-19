from flask import Blueprint, request, jsonify
from app.models.directive_model import Directive
from app.utils.decorators import jwt_required, roles_required

directive_bp = Blueprint("directive", __name__)

@directive_bp.route("/directives", methods=["GET"])
@jwt_required
@roles_required(roles=["Editor", "Viewer"])
def get_directives():
    directives = Directive.get_all()
    return jsonify([directive.serialize() for directive in directives])

@directive_bp.route("/directives/<int:id>", methods=["GET"])
@jwt_required
@roles_required(roles=["Editor", "Viewer"])
def get_directive(id):
    directive = Directive.get_by_id(id)
    if directive:
        return jsonify(directive.serialize())
    return jsonify({"error": "Directiva no encontrada"}), 404

@directive_bp.route("/directives", methods=["POST"])
@jwt_required
@roles_required(roles=["Editor"])
def create_directive():
    data = request.json
    nombre = data.get("nombre")
    if not nombre:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    directive = Directive(nombre=nombre)
    directive.save()
    return jsonify(directive.serialize()), 201

@directive_bp.route("/directives/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(roles=["Editor"])
def update_directive(id):
    directive = Directive.get_by_id(id)
    if not directive:
        return jsonify({"error": "Directiva no encontrada"}), 404
    data = request.json
    nombre = data.get("nombre")
    if not nombre:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    directive.update(nombre=nombre)
    return jsonify(directive.serialize())

@directive_bp.route("/directives/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(roles=["Editor"])
def delete_directive(id):
    directive = Directive.get_by_id(id)
    if not directive:
        return jsonify({"error": "Directiva no encontrada"}), 404
    directive.delete()
    return "", 204