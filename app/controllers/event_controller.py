from flask import Blueprint, request, jsonify
from models.event_model import Event
from utils.decorators import jwt_required, roles_required
from datetime import datetime

event_bp = Blueprint("event", __name__)

@event_bp.route("/events", methods=["GET"])
@jwt_required
@roles_required(roles=["admin", "user"])
def get_events():
    events = Event.get_all()
    return jsonify([event.serialize() for event in events])

@event_bp.route("/events/<int:id>", methods=["GET"])
@jwt_required
@roles_required(roles=["admin", "user"])
def get_event(id):
    event = Event.get_by_id(id)
    if event:
        return jsonify(event.serialize())
    return jsonify({"error": "Evento no encontrado"}), 404

@event_bp.route("/events", methods=["POST"])
@jwt_required
@roles_required(roles=["admin"])
def create_event():
    data = request.json
    descripcion = data.get("descripcion")
    estado = data.get("estado", True)
    fecha_str = data.get("fecha")
    if not descripcion or not fecha_str:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    try:
        fecha = datetime.fromisoformat(fecha_str)
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido"}), 400
    event = Event(descripcion=descripcion, estado=estado, fecha=fecha)
    event.save()
    return jsonify(event.serialize()), 201

@event_bp.route("/events/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(roles=["admin"])
def update_event(id):
    event = Event.get_by_id(id)
    if not event:
        return jsonify({"error": "Evento no encontrado"}), 404
    data = request.json
    descripcion = data.get("descripcion")
    estado = data.get("estado")
    fecha_str = data.get("fecha")
    try:
        fecha = datetime.fromisoformat(fecha_str)
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido"}), 400
    event.update(descripcion=descripcion, estado=estado, fecha=fecha)
    return jsonify(event.serialize())

@event_bp.route("/events/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(roles=["admin"])
def delete_event(id):
    event = Event.get_by_id(id)
    if not event:
        return jsonify({"error": "Evento no encontrado"}), 404
    event.delete()
    return "", 204