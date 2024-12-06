from flask import Blueprint, request, jsonify
from models.guest_model import Guest
from utils.decorators import jwt_required, roles_required
from datetime import datetime


guest_bp = Blueprint("guest", __name__)





@guest_bp.route("/guests", methods=["GET"])
@jwt_required
@roles_required(roles=["admin", "user"])
def get_guests():
    guests = Guest.get_all()
    guests_data = []
    for guest in guests:
        guest_data = guest.serialize()
        guest_data["church_name"] = guest.church.nombre if guest.church else None
        guests_data.append(guest_data)
    return jsonify(guests_data)

@guest_bp.route("/guests/<int:id>", methods=["GET"])
@jwt_required
@roles_required(roles=["admin", "user"])
def get_guest(id):
    guest = Guest.get_by_id(id)
    if guest:
        guest_data = guest.serialize()
        guest_data["church_name"] = guest.church.nombre if guest.church else None
        guest_data["position_description"] = guest.position.descripcion if guest.position else None
        return jsonify(guest_data)
    return jsonify({"error": "Invitado no encontrado"}), 404

@guest_bp.route("/guests", methods=["POST"])
@jwt_required
@roles_required(roles=["admin"])
def create_guest():
    data = request.json
    nombre = data.get("nombre")
    apellidos = data.get("apellidos")
    email = data.get("email")
    telefono = data.get("telefono")
    position_id = data.get("position_id")
    church_id = data.get("church_id")
    if not nombre or not apellidos or not position_id or not church_id:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    guest = Guest(nombre=nombre, apellidos=apellidos, email=email, telefono=telefono, position_id=position_id, church_id=church_id)
    guest.save()
    return jsonify(guest.serialize()), 201

@guest_bp.route("/guests/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(roles=["admin"])
def update_guest(id):
    guest = Guest.get_by_id(id)
    if not guest:
        return jsonify({"error": "Invitado no encontrado"}), 404
    data = request.json
    nombre = data.get("nombre")
    apellidos = data.get("apellidos")
    email = data.get("email")
    telefono = data.get("telefono")
    position_id = data.get("position_id")
    church_id = data.get("church_id")
    guest.update(nombre=nombre, apellidos=apellidos, email=email, telefono=telefono, position_id=position_id, church_id=church_id)
    return jsonify(guest.serialize())

@guest_bp.route("/guests/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(roles=["admin"])
def delete_guest(id):
    guest = Guest.get_by_id(id)
    if not guest:
        return jsonify({"error": "Invitado no encontrado"}), 404
    guest.delete()
    return "", 204