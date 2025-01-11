from flask import Blueprint, request, jsonify
from app.models.payment_model import Payment
from app.utils.decorators import jwt_required, roles_required

payment_bp = Blueprint("payment", __name__)

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
    monto = data.get("monto")
    observaciones = data.get("observaciones")
    
    if not id_payer or not id_guest or not id_user or not monto:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    payment = Payment(id_payer=id_payer, id_guest=id_guest, id_user=id_user, monto=monto, observaciones=observaciones)
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
    monto = data.get("monto")
    observaciones = data.get("observaciones")
    
    payment.update(id_payer=id_payer, id_guest=id_guest, id_user=id_user, monto=monto, observaciones=observaciones)
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