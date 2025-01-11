from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from app.models.payment_model import Payment
from app.models.guest_model import Guest
from app.utils.decorators import jwt_required, roles_required
from flask_jwt_extended import current_user

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/payments/details", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payments_details():
    guests = Guest.query.options(
        joinedload(Guest.church),
        joinedload(Guest.directive),
        joinedload(Guest.payments_received).joinedload(Payment.payer)
    ).all()
    
    payments_data = []
    for guest in guests:
        guest_data = guest.serialize()
        guest_data["church_name"] = guest.church.nombre if guest.church else None
        guest_data["directive_name"] = guest.directive.nombre if guest.directive else None
        guest_data["payments"] = []
        for payment in guest.payments_received:
            payment_data = payment.serialize()
            payer = payment.payer
            payment_data["payer_name"] = f"{payer.nombre} {payer.apellidos}" if payer else None
            guest_data["payments"].append(payment_data)
        payments_data.append(guest_data)
    return jsonify(payments_data)

@payment_bp.route("/payments", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payments():
    payments = Payment.get_all()
    return jsonify([payment.serialize() for payment in payments])

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
    id_payer = data.get("id_payer")
    id_guest = data.get("id_guest")
    id_user = data.get("id_user")
    first_payment = data.get("first_payment")
    second_payment = data.get("second_payment")
    observaciones = data.get("observaciones")
    
    if not id_payer or not id_guest or not id_user or not first_payment:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    payment = Payment(id_payer=id_payer, id_guest=id_guest, id_user=id_user, first_payment=first_payment, second_payment=second_payment, observaciones=observaciones)
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
    id_payer = data.get("id_payer")
    id_guest = data.get("id_guest")
    id_user = data.get("id_user")
    first_payment = data.get("first_payment")
    second_payment = data.get("second_payment")
    observaciones = data.get("observaciones")
    
    payment.update(id_payer=id_payer, id_guest=id_guest, id_user=id_user, first_payment=first_payment, second_payment=second_payment, observaciones=observaciones)
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

@payment_bp.route("/payments/multiple", methods=["POST"])
@jwt_required
@roles_required(["Editor"])
def create_multiple_payments():
    data = request.json
    print("HOlaaaaaaaa")
    print(data)
    payments = data.get("payments")
    
    if not payments or not isinstance(payments, list):
        return jsonify({"error": "Faltan datos requeridos o formato incorrecto"}), 400
    
    created_payments = []
    id_user = current_user.id  # Extract id_user from the JWT token
    for payment_data in payments:
        id_payer = payment_data.get("id_payer")
        id_guest = payment_data.get("id_guest")
        first_payment = payment_data.get("first_payment")
        second_payment = payment_data.get("second_payment")
        observaciones = payment_data.get("observaciones")
        
        if not id_payer or not id_guest:
            return jsonify({"error": "Faltan datos requeridos en uno de los pagos"}), 400
        
        payment = Payment(id_payer=id_payer, id_guest=id_guest, id_user=id_user, first_payment=first_payment, second_payment=second_payment, observaciones=observaciones)
        payment.save()
        created_payments.append(payment.serialize())
    
    return jsonify(created_payments), 201



@payment_bp.route("/payments/guest/<int:id_guest>", methods=["DELETE"])
@jwt_required
@roles_required(["Editor"])
def delete_payments_by_guest(id_guest):
    payments = Payment.query.filter_by(id_guest=id_guest).all()
    if not payments:
        return jsonify({"error": "No se encontraron pagos para el invitado proporcionado"}), 404
    
    for payment in payments:
        payment.delete()
    
    return "", 204