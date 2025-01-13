from flask import Blueprint, request, jsonify
from app.models.event_detail_model import EventDetail
from app.models.guest_model import Guest
from app.models.event_model import Event
from app.models.church_model import Church
from app.utils.decorators import jwt_required, roles_required
from datetime import datetime
from flask_jwt_extended import current_user
from app.models.directive_model import Directive
from sqlalchemy.orm import joinedload

event_detail_bp = Blueprint("event_detail", __name__)

@event_detail_bp.route("/event_details/<int:event_id>/<int:directive_id>", methods=["GET"])
@jwt_required
@roles_required(["Editor"])
def get_event_detail_by_directive(event_id, directive_id):
    guests = Guest.query.filter_by(directive_id=directive_id).options(
        joinedload(Guest.church),
        joinedload(Guest.position),
        joinedload(Guest.directive)
    ).all()
    event_details = EventDetail.query.filter_by(event_id=event_id).all()
    event_guest_ids = {event_detail.guest_id for event_detail in event_details}
    
    guests_data = []
    for guest in guests:
        guest_data = guest.serialize()
        guest_data["church_name"] = guest.church.nombre if guest.church else None
        guest_data["departamento"] = guest.church.departamento if guest.church else None
        guest_data["position_description"] = guest.position.descripcion if guest.position else None
        guest_data["directive_name"] = guest.directive.nombre if guest.directive else None
        if guest.id in event_guest_ids:
            detalle = EventDetail.query.filter_by(guest_id=guest.id).first()
            guest_data["hora"] = detalle.hora
            guest_data["observaciones"] = detalle.observaciones
            guest_data["asistencia"] = 1
        else:
            guest_data["hora"] = None
            guest_data["observaciones"] = None
            guest_data["asistencia"] = 0
        guests_data.append(guest_data)
    
    return jsonify(guests_data)





@event_detail_bp.route("/event_details/statistics", methods=["GET"])
@jwt_required
def get_active_event_detail():
    event_id = EventDetail.get_event_with_estado(0)
    print(event_id)
    if event_id is None:
        latest_event = Event.query.filter_by(qr_available=1).first()
        event_id = latest_event.id if latest_event else 1
        
    if event_id:
        event = Event.query.get(event_id)
        event_description = event.descripcion if event else None
        qr_available = event.qr_available if event else None
        event_details = EventDetail.query.options(
            joinedload(EventDetail.guest).joinedload(Guest.directive)
        ).filter_by(event_id=event_id).all()
        directive_counts = {}
        
        directives = Directive.query.all()
        
        # Add IGLESIAS first
        total_unique_churches = Church.query.count()
        directive_counts["IGLESIAS"] = {"directive_id": 0, "asistencia": 0, "total": total_unique_churches}
        
        for directive in directives:
            directive_nombre = directive.nombre
            total = Guest.query.filter_by(directive_id=directive.id).count()
            directive_counts[directive_nombre] = {"directive_id": directive.id, "asistencia": 0, "total": total}
            
        if event_details:
            unique_church_ids = set()
            for event_detail in event_details:
                directive_id = event_detail.guest.directive_id if event_detail.guest else None
                directive_nombre = event_detail.guest.directive.nombre if event_detail.guest and event_detail.guest.directive else "IGLESIAS"
                if directive_nombre in directive_counts:
                    if directive_id is None or directive_id == 0:
                        if event_detail.guest.church_id not in unique_church_ids:
                            unique_church_ids.add(event_detail.guest.church_id)
                            directive_counts["IGLESIAS"]["asistencia"] += 1
                    else:
                        directive_counts[directive_nombre]["asistencia"] += 1
        
        for directive_nombre in directive_counts:
            if directive_nombre == "IGLESIAS":
                total_guests = Guest.query.filter(Guest.directive_id.is_(None)).distinct(Guest.church_id).count()
                if not total_guests: total_guests = 0
            else:
                directive_id = next((event_detail.guest.directive_id for event_detail in event_details if event_detail.guest and event_detail.guest.directive and event_detail.guest.directive.nombre == directive_nombre), None)
                total_guests = Guest.query.filter_by(directive_id=directive_id).count() if directive_id else 0

        return jsonify({
            "event_id": event_id,
            "event_description": event_description,
            "qr_available": qr_available,
            "event_details": directive_counts
        })
    return jsonify([])





@event_detail_bp.route("/event_details", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_event_details():
    event_details = EventDetail.query.options(
        joinedload(EventDetail.event),
        joinedload(EventDetail.guest),
        joinedload(EventDetail.user)
    ).all()
    
    event_details_data = []
    for event_detail in event_details:
        event_detail_data = event_detail.serialize()
        event_detail_data["event_name"] = event_detail.event.nombre if event_detail.event else None
        event_detail_data["guest_name"] = f"{event_detail.guest.nombre} {event_detail.guest.apellidos}" if event_detail.guest else None
        event_detail_data["user_name"] = f"{event_detail.user.name} {event_detail.user.lastname}" if event_detail.user else None
        event_details_data.append(event_detail_data)
    return jsonify(event_details_data)

@event_detail_bp.route("/event_details/<int:event_id>", methods=["GET"])
@jwt_required
@roles_required(["Editor"])
def get_event_details_with_guests(event_id):
    guests = Guest.query.options(
        joinedload(Guest.church),
        joinedload(Guest.position),
        joinedload(Guest.directive)
    ).all()
    event_details = EventDetail.query.filter_by(event_id=event_id).all()
    event_guest_ids = {event_detail.guest_id for event_detail in event_details}
    
    guests_data = []
    for guest in guests:
        guest_data = guest.serialize()
        guest_data["church_name"] = guest.church.nombre if guest.church else None
        guest_data["departamento"] = guest.church.departamento if guest.church else None
        guest_data["position_description"] = guest.position.descripcion if guest.position else None
        guest_data["directive_name"] = guest.directive.nombre if guest.directive else None
        if guest.id in event_guest_ids:
            detalle = EventDetail.query.filter_by(guest_id=guest.id).first()
            guest_data["hora"] = detalle.hora
            guest_data["observaciones"] = detalle.observaciones
            guest_data["asistencia"] = 1
        else:
            guest_data["hora"] = None
            guest_data["observaciones"] = None
            guest_data["asistencia"] = 0
        guests_data.append(guest_data)
    
    return jsonify(guests_data)

@event_detail_bp.route("/event_details", methods=["POST"])
@jwt_required
@roles_required(["Editor"])
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
@roles_required(["Editor"])
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
@roles_required(["Editor"])
def delete_event_detail(id):
    event_detail = EventDetail.get_by_id(id)
    if not event_detail:
        return jsonify({"error": "Detalle de evento no encontrado"}), 404
    event_detail.delete()
    return "", 204

@event_detail_bp.route("/event_details/<int:event_id>/<int:guest_id>", methods=["DELETE"])
@jwt_required
@roles_required(["Editor"])
def delete_event_detail_by_guest_and_event(event_id, guest_id):
    event_detail = EventDetail.query.filter_by(event_id=event_id, guest_id=guest_id).first()
    if not event_detail:
        return jsonify({"error": "Detalle de evento no encontrado"}), 404
    event_detail.delete()
    return "", 204



@event_detail_bp.route("/scanner", methods=["POST"])
@jwt_required
@roles_required(["Scanner", "Editor"])
def create_event_detail_from_scanner():
    data = request.json
    
    guest_code = data.get("guest_code")
    observaciones = data.get("observaciones")
    
    if not guest_code:
        return jsonify({"error": "QR no asignado"}), 400
    
    # Buscar el evento con estado 0
    event_id = EventDetail.get_event_with_estado(0)
    if not event_id:
        return jsonify({"error": "No hay ningun evento activo"}), 400
    
    # Obtener el user_id del usuario actual
    user = current_user
    user_id = user.id
    
    # Obtener el guest
    guest = Guest.query.filter_by(code=guest_code).first()
    if not guest:
        return jsonify({"error": "Invitado no encontrado"}), 404
    
    # Obtener el evento
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Evento no encontrado"}), 404
    
    event_detail = EventDetail(
        hora=datetime.utcnow(),
        event_id=event_id,
        guest_id=guest.id,
        observaciones=observaciones,
        user_id=user_id
    )
    event_detail.save()
    
    response = event_detail.serialize()
    response["guest_nombre"] = guest.nombre + " " + guest.apellidos
    response["event_descripcion"] = event.descripcion
    response["qr_available"] = event.qr_available
    
    return jsonify(response), 201