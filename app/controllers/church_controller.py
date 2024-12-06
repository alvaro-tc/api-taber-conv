from flask import Blueprint, request, jsonify
from models.church_model import Church
from utils.decorators import jwt_required, roles_required

church_bp = Blueprint("church", __name__)

@church_bp.route("/churches", methods=["GET"])
@jwt_required
@roles_required(roles=["admin", "user"])
def get_churches():
    churches = Church.get_all()
    return jsonify([church.serialize() for church in churches])

@church_bp.route("/churches/<int:id>", methods=["GET"])
@jwt_required
@roles_required(roles=["admin", "user"])
def get_church(id):
    church = Church.get_by_id(id)
    if church:
        return jsonify(church.serialize())
    return jsonify({"error": "Iglesia no encontrada"}), 404

@church_bp.route("/churches", methods=["POST"])
@jwt_required
@roles_required(roles=["admin"])
def create_church():
    data = request.json
    nombre = data.get("nombre")
    departamento = data.get("departamento")
    area = data.get("area")
    localidad = data.get("localidad")
    direccion = data.get("direccion")
    
    valid_departamentos = ['Chuquisaca', 'La Paz', 'Cochabamba', 'Oruro', 'Potosi', 'Tarija', 'Santa Cruz', 'Beni', 'Pando']
    valid_areas = ['URBANO', 'RURAL']
    
    if not nombre or not departamento or not area:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    if departamento not in valid_departamentos:
        return jsonify({"error": "Departamento no válido"}), 400
    if area not in valid_areas:
        return jsonify({"error": "Área no válida"}), 400
    
    church = Church(nombre=nombre, departamento=departamento, area=area, localidad=localidad, direccion=direccion)
    church.save()
    return jsonify(church.serialize()), 201

@church_bp.route("/churches/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(roles=["admin"])
def update_church(id):
    church = Church.get_by_id(id)
    if not church:
        return jsonify({"error": "Iglesia no encontrada"}), 404
    data = request.json
    nombre = data.get("nombre")
    departamento = data.get("departamento")
    area = data.get("area")
    localidad = data.get("localidad")
    direccion = data.get("direccion")
    
    valid_departamentos = ['Chuquisaca', 'La Paz', 'Cochabamba', 'Oruro', 'Potosi', 'Tarija', 'Santa Cruz', 'Beni', 'Pando']
    valid_areas = ['URBANO', 'RURAL']
    
    if departamento and departamento not in valid_departamentos:
        return jsonify({"error": "Departamento no válido"}), 400
    if area and area not in valid_areas:
        return jsonify({"error": "Área no válida"}), 400
    
    church.update(nombre=nombre, departamento=departamento, area=area, localidad=localidad, direccion=direccion)
    return jsonify(church.serialize())

@church_bp.route("/churches/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(roles=["admin"])
def delete_church(id):
    church = Church.get_by_id(id)
    if not church:
        return jsonify({"error": "Iglesia no encontrada"}), 404
    church.delete()
    return "", 204