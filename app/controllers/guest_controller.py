from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from app.models.guest_model import Guest
from app.models.payment_model import Payment
from app.utils.decorators import jwt_required, roles_required

guest_bp = Blueprint("guest", __name__)

@guest_bp.route("/guests", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_guests():
    guests = Guest.query.options(
        joinedload(Guest.church),
        joinedload(Guest.position),
        joinedload(Guest.directive)
    ).all()
    
    guests_data = []
    for guest in guests:
        guest_data = guest.serialize()
        guest_data["church_name"] = guest.church.nombre if guest.church else None
        guest_data["position_description"] = guest.position.descripcion if guest.position else None
        guest_data["directive_name"] = guest.directive.nombre if guest.directive else None
        guests_data.append(guest_data)
    return jsonify(guests_data)

@guest_bp.route("/guests/payment", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_guests_with_payments():
    guests = Guest.query.options(
        joinedload(Guest.church),
        joinedload(Guest.position),
        joinedload(Guest.directive),
        joinedload(Guest.payments_received).joinedload(Payment.payer)
    ).all()
    
    guests_data = []
    for guest in guests:
        guest_data = guest.serialize()
        guest_data["church_name"] = guest.church.nombre if guest.church else None
        guest_data["position_description"] = guest.position.descripcion if guest.position else None
        guest_data["directive_name"] = guest.directive.nombre if guest.directive else None
        guest_data["payments"] = []
        for payment in guest.payments_received:
            payment_data = payment.serialize()
            payer = payment.payer
            payment_data["payer_name"] = f"{payer.nombre} {payer.apellidos}" if payer else None
            guest_data["payments"].append(payment_data)
        guests_data.append(guest_data)
    return jsonify(guests_data)



@guest_bp.route("/guests/<int:id>", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_guest(id):
    guest = Guest.get_by_id(id)
    if guest:
        guest_data = guest.serialize()
        guest_data["church_name"] = guest.church.nombre if guest.church else None
        guest_data["position_description"] = guest.position.descripcion if guest.position else None
        guest_data["directive_name"] = guest.directive.nombre if guest.directive else None
        
        return jsonify(guest_data)
    return jsonify({"error": "Invitado no encontrado"}), 404

@guest_bp.route("/guests", methods=["POST"])
@jwt_required
@roles_required(["Editor"])
def create_guest():
    data = request.json
    print("DATA")
    print(data)
    nombre = data.get("nombre")
    apellidos = data.get("apellidos")
    email = data.get("email")
    telefono = data.get("telefono")
    position_id = data.get("position_id")
    church_id = data.get("church_id")
    directive_id = data.get("directive_id")
    code = data.get("code")
    if not nombre or not apellidos:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    guest = Guest(
        nombre=nombre, 
        apellidos=apellidos, 
        email=email, 
        telefono=telefono, 
        position_id=position_id if position_id not in [None, 0] else None, 
        church_id=church_id if church_id not in [None, 0] else None, 
        directive_id=directive_id if directive_id is not None else None,
        code=code
    )
    
    guest.save()
    return jsonify(guest.serialize()), 201

@guest_bp.route("/guests/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(["Editor"])
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
    directive_id = data.get("directive_id")
    code = data.get("code")
    
    # Actualizar los datos del invitado
    guest.update(
        nombre=nombre, 
        apellidos=apellidos, 
        email=email, 
        telefono=telefono, 
        position_id=position_id if position_id is not None else None, 
        church_id=church_id if church_id is not None else None, 
        directive_id=directive_id if directive_id is not None else None,
        code=code
    )
    
    
    return jsonify(guest.serialize())



@guest_bp.route("/guests/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(["Editor"])
def delete_guest(id):
    guest = Guest.get_by_id(id)
    if not guest:
        return jsonify({"error": "Invitado no encontrado"}), 404
    guest.delete()
    return "", 204





@guest_bp.route("/guests/qrcode", methods=["POST"])
@jwt_required
@roles_required(roles=["Scanner", "Editor"])
def create_event_detail_from_scanner():
    data = request.json
    guest_id = data.get("guest_id")
    guest_code = data.get("guest_code")
    guest = Guest.get_by_id(guest_id)
    if not guest:
        return jsonify({"error": "Invitado no encontrado"}), 404
    
    if guest.code == guest_code:
        return jsonify({"error": "El código QR ya esta asignado a esta persona"}), 400
    
    
    guestduplicade = Guest.query.filter_by(code=guest_code).first()
    if guestduplicade:
        return jsonify({"error": "El código QR ya esta asignado a la persona: "+guestduplicade.nombre+" "+guestduplicade.apellidos}), 400

    guest.update(code=guest_code)
    if not guest_id or not guest_code:
        return jsonify({"error": "QR invalido"}), 400
    if guest:
            guest_data = guest.serialize()
            guest_data["church_name"] = guest.church.nombre if guest.church else None
            guest_data["position_description"] = guest.position.descripcion if guest.position else None
            guest_data["directive_name"] = guest.directive.nombre if guest.directive else None
            return jsonify(guest_data), 201
