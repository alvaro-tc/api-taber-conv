from flask import Blueprint, request, jsonify
from app.models.guest_model import Guest
from app.models.payment_model import Payment
from app.utils.decorators import jwt_required, roles_required
from datetime import datetime

guest_bp = Blueprint("guest", __name__)

@guest_bp.route("/guests", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_guests():
    guests = Guest.get_all()
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
    guests = Guest.get_all()
    guests_data = []
    for guest in guests:
        guest_data = guest.serialize()
        guest_data["church_name"] = guest.church.nombre if guest.church else None
        guest_data["position_description"] = guest.position.descripcion if guest.position else None
        guest_data["directive_name"] = guest.directive.nombre if guest.directive else None
        payment = Payment.query.filter_by(guest_id=guest.id).first()
        if payment:
            guest_data["monto1"] = payment.monto1
            guest_data["monto2"] = payment.monto2
            guest_data["observaciones1"] = payment.observaciones1
            guest_data["observaciones2"] = payment.observaciones2
            guest_data["fecha_registro"] = payment.fecha_registro.isoformat()
        else:
            guest_data["monto1"] = None
            guest_data["monto2"] = None
            guest_data["observaciones1"] = None
            guest_data["observaciones2"] = None
            guest_data["fecha_registro"] = None
        
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
        
        # Obtener los datos de pago
        payment = Payment.query.filter_by(guest_id=guest.id).first()
        if payment:
            guest_data["monto1"] = payment.monto1
            guest_data["monto2"] = payment.monto2
            guest_data["observaciones1"] = payment.observaciones1
            guest_data["observaciones2"] = payment.observaciones2
            guest_data["fecha_registro"] = payment.fecha_registro.isoformat()
        else:
            guest_data["monto1"] = None
            guest_data["monto2"] = None
            guest_data["observaciones1"] = None
            guest_data["observaciones2"] = None
            guest_data["fecha_registro"] = None
        
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
    
    # Actualizar los datos de pago
    monto1 = data.get("monto1")
    monto2 = data.get("monto2")
    observaciones1 = data.get("observaciones1")
    observaciones2 = data.get("observaciones2")
    
    if any([monto1, monto2, observaciones1, observaciones2]):
        payment = Payment.query.filter_by(guest_id=guest.id).first()
        if payment:
            payment.update(
                monto1=monto1 if monto1 is not None else payment.monto1,
                monto2=monto2 if monto2 is not None else payment.monto2,
                observaciones1=observaciones1 if observaciones1 is not None else payment.observaciones1,
                observaciones2=observaciones2 if observaciones2 is not None else payment.observaciones2
            )
        else:
            payment = Payment(
                monto1=monto1,
                monto2=monto2,
                observaciones1=observaciones1,
                observaciones2=observaciones2,
                guest_id=guest.id
            )
            payment.save()
    
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