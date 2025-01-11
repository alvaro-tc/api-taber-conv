from flask import Blueprint, request, jsonify
from app.models.payment_model import PaymentDetail
from app.utils.decorators import jwt_required, roles_required

payment_detail_bp = Blueprint("payment_detail", __name__)

@payment_detail_bp.route("/payment_details", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payment_details():
    payment_details = PaymentDetail.get_all()
    return jsonify([payment_detail.serialize() for payment_detail in payment_details])

@payment_detail_bp.route("/payment_details/<int:id>", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payment_detail(id):
    payment_detail = PaymentDetail.get_by_id(id)
    if payment_detail:
        return jsonify(payment_detail.serialize())
    return jsonify({"error": "Detalle de pago no encontrado"}), 404

@payment_detail_bp.route("/payment_details", methods=["POST"])
@jwt_required
@roles_required(["Editor"])
def create_payment_detail():
    data = request.json
    id_payment = data.get("id_payment")
    concepto = data.get("concepto")
    monto = data.get("monto")
    
    if not id_payment or not concepto or not monto:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    payment_detail = PaymentDetail(id_payment=id_payment, concepto=concepto, monto=monto)
    payment_detail.save()
    return jsonify(payment_detail.serialize()), 201

@payment_detail_bp.route("/payment_details/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(["Editor"])
def update_payment_detail(id):
    payment_detail = PaymentDetail.get_by_id(id)
    if not payment_detail:
        return jsonify({"error": "Detalle de pago no encontrado"}), 404
    data = request.json
    id_payment = data.get("id_payment")
    concepto = data.get("concepto")
    monto = data.get("monto")
    
    payment_detail.update(id_payment=id_payment, concepto=concepto, monto=monto)
    return jsonify(payment_detail.serialize())

@payment_detail_bp.route("/payment_details/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(["Editor"])
def delete_payment_detail(id):
    payment_detail = PaymentDetail.get_by_id(id)
    if not payment_detail:
        return jsonify({"error": "Detalle de pago no encontrado"}), 404
    payment_detail.delete()
    return "", 204