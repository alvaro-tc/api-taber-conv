from flask import Blueprint, request, jsonify
from app.models.event_detail_model import EventDetail
from app.models.guest_model import Guest
from app.models.event_model import Event
from app.utils.decorators import jwt_required, roles_required
from datetime import datetime
from flask_jwt_extended import current_user

event_detail_bp = Blueprint("event_detail", __name__)

@event_detail_bp.route("/event_details/statistics", methods=["GET"])
@jwt_required
def get_active_event_detail():
    event_id = EventDetail.get_event_with_estado(0)
    if not event_id:
        latest_event_detail = EventDetail.query.order_by(EventDetail.created_at.desc()).first()
        event_id = latest_event_detail.event_id if latest_event_detail else None
    
    if event_id:
        event = Event.query.get(event_id)
        event_description = event.descripcion if event else None
        qr_available = event.qr_available if event else None
        event_details = EventDetail.query.filter_by(event_id=event_id).all()
        if event_details:
            directive_counts = {}
            for event_detail in event_details:
                directive_id = event_detail.guest.directive_id if event_detail.guest else None
                directive_nombre = event_detail.guest.directive.nombre if event_detail.guest and event_detail.guest.directive else "Iglesias"
                if directive_nombre not in directive_counts:
                    directive_counts[directive_nombre] = {"asistencia": 0, "total": 0}
                directive_counts[directive_nombre]["asistencia"] += 1
            
            for directive_nombre in directive_counts:
                if directive_nombre == "Iglesias":
                    total_guests = Guest.query.filter(Guest.directive_id.is_(None)).count()
                else:
                    directive_id = next((event_detail.guest.directive_id for event_detail in event_details if event_detail.guest and event_detail.guest.directive and event_detail.guest.directive.nombre == directive_nombre), None)
                    total_guests = Guest.query.filter_by(directive_id=directive_id).count() if directive_id else 0
                directive_counts[directive_nombre]["total"] = total_guests
            return jsonify({
                "event_id": event_id,
                "event_description": event_description,
                "qr_available": qr_available,
                "event_details": directive_counts
            })
    
    return jsonify([])

@event_detail_bp.route("/event_details", methods=["GET"])
@jwt_required
@roles_required(roles=["Editor"])
def get_event_details():
    event_details = EventDetail.get_all()
    event_details_data = [event_detail.serialize() for event_detail in event_details]
    return jsonify(event_details_data)

@event_detail_bp.route("/event_details/<int:id>", methods=["GET"])
@jwt_required
@roles_required(roles=["Editor"])
def get_event_detail(id):
    event_details = EventDetail.query.filter_by(event_id=id).all()
    if event_details:
        event_details_data = []
        for event_detail in event_details:
            event_detail_data = event_detail.serialize()
            event_detail_data["guest_nombre"] = event_detail.guest.nombre if event_detail.guest else None
            event_detail_data["guest_apellidos"] = event_detail.guest.apellidos if event_detail.guest else None
            event_details_data.append(event_detail_data)
        return jsonify(event_details_data)
    return jsonify([])

@event_detail_bp.route("/event_details", methods=["POST"])
@jwt_required
@roles_required(roles=["Editor"])
def create_event_detail():
    data = request.json
    hora = data.get("hora", datetime.utcnow())
    event_id = data.get("event_id")
    guest_id = data.get("guest_id")
    observaciones = data.get("observaciones")
    user_id = data.get("user_id")
    if not event_id or not guest_id or not user_id:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    event_detail = EventDetail(hora=hora, event_id=event_id, guest_id=guest_id, observaciones=observaciones, user_id=user_id)
    event_detail.save()
    return jsonify(event_detail.serialize()), 201

@event_detail_bp.route("/event_details/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(roles=["Editor"])
def update_event_detail(id):
    event_detail = EventDetail.get_by_id(id)
    if not event_detail:
        return jsonify({"error": "Detalle de evento no encontrado"}), 404
    data = request.json
    hora = data.get("hora", event_detail.hora)
    event_id = data.get("event_id", event_detail.event_id)
    guest_id = data.get("guest_id", event_detail.guest_id)
    observaciones = data.get("observaciones", event_detail.observaciones)
    user_id = data.get("user_id", event_detail.user_id)
    event_detail.update(hora=hora, event_id=event_id, guest_id=guest_id, observaciones=observaciones, user_id=user_id)
    return jsonify(event_detail.serialize())

@event_detail_bp.route("/event_details/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(roles=["Editor"])
def delete_event_detail(id):
    event_detail = EventDetail.get_by_id(id)
    if not event_detail:
        return jsonify({"error": "Detalle de evento no encontrado"}), 404
    event_detail.delete()
    return "", 204

@event_detail_bp.route("/scanner", methods=["POST"])
@jwt_required
@roles_required(roles=["Scanner", "Editor"])
def create_event_detail_from_scanner():
    data = request.json
    
    guest_id = data.get("guest_id")
    observaciones = data.get("observaciones")
    
    if not guest_id:
        return jsonify({"error": "QR invalido"}), 400
    
    # Buscar el evento con estado 0
    event_id = EventDetail.get_event_with_estado(0)
    if not event_id:
        return jsonify({"error": "No hay ningun evento activo"}), 400
    
    # Obtener el user_id del usuario actual
    user = current_user
    user_id = user.id
    
    # Obtener el guest
    guest = Guest.query.get(guest_id)
    if not guest:
        return jsonify({"error": "Invitado no encontrado"}), 404
    
    # Obtener el evento
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Evento no encontrado"}), 404
    
    event_detail = EventDetail(
        hora=datetime.utcnow(),
        event_id=event_id,
        guest_id=guest_id,
        observaciones=observaciones,
        user_id=user_id
    )
    event_detail.save()
    
    response = event_detail.serialize()
    response["guest_nombre"] = guest.nombre + " " + guest.apellidos
    response["event_descripcion"] = event.descripcion
    response["qr_available"] = event.qr_available
    
    return jsonify(response), 201