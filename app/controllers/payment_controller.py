from flask import Blueprint, request, jsonify
from app.models.payment_model import Payment
from app.models.guest_model import Guest
from app.utils.decorators import jwt_required, roles_required

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/payments", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payments():
    guests = Guest.query.all()
    payments = Payment.query.all()
    payments_by_guest_id = {payment.guest_id: payment for payment in payments}
    
    guests_data = []
    for guest in guests:
        guest_data = guest.serialize()
        payment = payments_by_guest_id.get(guest.id)
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

@payment_bp.route("/payments/<int:id>", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payment(id):
    payment = Payment.get_by_id(id)
    if payment:
        return jsonify(payment.serialize())
    return jsonify({"error": "Pago no encontrado"}), 404

@payment_bp.route("/payments", methods=["POST"])
@jwt_required
@roles_required(["Editor"])
def create_payment():
    data = request.json
    monto1 = data.get("monto1")
    monto2 = data.get("monto2")
    observaciones1 = data.get("observaciones1")
    observaciones2 = data.get("observaciones2")
    guest_id = data.get("guest_id")
    
    if not monto1 or not monto2:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    payment = Payment(monto1=monto1, monto2=monto2, observaciones1=observaciones1, observaciones2=observaciones2, guest_id=guest_id)
    payment.save()
    return jsonify(payment.serialize()), 201

@payment_bp.route("/payments/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(["Editor"])
def update_payment(id):
    payment = Payment.get_by_id(id)
    if not payment:
        return jsonify({"error": "Pago no encontrado"}), 404
    data = request.json
    monto1 = data.get("monto1")
    monto2 = data.get("monto2")
    observaciones1 = data.get("observaciones1")
    observaciones2 = data.get("observaciones2")
    guest_id = data.get("guest_id")
    
    payment.update(monto1=monto1, monto2=monto2, observaciones1=observaciones1, observaciones2=observaciones2, guest_id=guest_id)
    return jsonify(payment.serialize())

@payment_bp.route("/payments/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(["Editor"])
def delete_payment(id):
    payment = Payment.get_by_id(id)
    if not payment:
        return jsonify({"error": "Pago no encontrado"}), 404
    payment.delete()
    return "", 204