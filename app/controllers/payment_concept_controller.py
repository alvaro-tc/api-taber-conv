from flask import Blueprint, request, jsonify
from app.models.payment_model import PaymentConcept
from app.utils.decorators import jwt_required, roles_required

payment_concept_bp = Blueprint("payment_concept", __name__)

@payment_concept_bp.route("/payment_concepts", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payment_concepts():
    payment_concepts = PaymentConcept.get_all()
    return jsonify([payment_concept.serialize() for payment_concept in payment_concepts])

@payment_concept_bp.route("/payment_concepts/<int:id>", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payment_concept(id):
    payment_concept = PaymentConcept.get_by_id(id)
    if payment_concept:
        return jsonify(payment_concept.serialize())
    return jsonify({"error": "Concepto de pago no encontrado"}), 404

@payment_concept_bp.route("/payment_concepts", methods=["POST"])
@jwt_required
@roles_required(["Editor"])
def create_payment_concept():
    data = request.json
    nombre = data.get("nombre")
    monto_inicial = data.get("monto_inicial")
    
    if not nombre or not monto_inicial:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    payment_concept = PaymentConcept(nombre=nombre, monto_inicial=monto_inicial)
    payment_concept.save()
    return jsonify(payment_concept.serialize()), 201

@payment_concept_bp.route("/payment_concepts/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(["Editor"])
def update_payment_concept(id):
    payment_concept = PaymentConcept.get_by_id(id)
    if not payment_concept:
        return jsonify({"error": "Concepto de pago no encontrado"}), 404
    data = request.json
    nombre = data.get("nombre")
    monto_inicial = data.get("monto_inicial")
    
    payment_concept.update(nombre=nombre, monto_inicial=monto_inicial)
    return jsonify(payment_concept.serialize())

@payment_concept_bp.route("/payment_concepts/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(["Editor"])
def delete_payment_concept(id):
    payment_concept = PaymentConcept.get_by_id(id)
    if not payment_concept:
        return jsonify({"error": "Concepto de pago no encontrado"}), 404
    payment_concept.delete()
    return "", 204