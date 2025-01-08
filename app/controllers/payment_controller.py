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
    monto1 = data.get("monto1")
    monto2 = data.get("monto2")
    observaciones1 = data.get("observaciones1")
    observaciones2 = data.get("observaciones2")
    
    if not monto1 or not monto2:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    payment = Payment(monto1=monto1, monto2=monto2, observaciones1=observaciones1, observaciones2=observaciones2)
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
    
    payment.update(monto1=monto1, monto2=monto2, observaciones1=observaciones1, observaciones2=observaciones2)
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