from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from app.models.payment_model import Payment
from app.models.guest_model import Guest
from app.utils.decorators import jwt_required, roles_required
from flask_jwt_extended import current_user

payment_bp = Blueprint("payment", __name__)




@payment_bp.route("/payments/report/", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payments_report_by_id():
    user_id = current_user.id
    payments = Payment.query.filter_by(id_user=user_id).options(
        joinedload(Payment.payer),
        joinedload(Payment.guest),
        joinedload(Payment.user)
    ).all()
    payments_data = []
    for payment in payments:
        payment_data = payment.serialize()
        payment_data["payer_name"] = f"{payment.payer.nombre} {payment.payer.apellidos}" if payment.payer else None
        payment_data["guest_name"] = f"{payment.guest.nombre} {payment.guest.apellidos}" if payment.guest else None
        payment_data["user_name"] = f"{payment.user.name} {payment.user.lastname}" if payment.user else None
        payments_data.append(payment_data)
    return jsonify(payments_data)



@payment_bp.route("/payments/report/<int:id>", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payments_report(id):
    user_id = id
    payments = Payment.query.filter_by(id_user=user_id).options(
        joinedload(Payment.payer),
        joinedload(Payment.guest).joinedload(Guest.church),
        joinedload(Payment.user)
    ).all()
    payments_data = []
    for payment in payments:
        payment_data = payment.serialize()
        payment_data["payer_name"] = f"{payment.payer.nombre} {payment.payer.apellidos}" if payment.payer else None
        payment_data["guest_name"] = f"{payment.guest.nombre} {payment.guest.apellidos}" if payment.guest else None
        payment_data["user_name"] = f"{payment.user.name} {payment.user.lastname}" if payment.user else None
        payment_data["church_name"] = payment.guest.church.nombre if payment.guest and payment.guest.church else None
        payment_data["church_area"] = payment.guest.church.area if payment.guest and payment.guest.church else None
        payment_data["directive_name"] = payment.guest.directive.nombre if payment.guest and payment.guest.directive else None
        payments_data.append(payment_data)
    return jsonify(payments_data)




@payment_bp.route("/payments/report/", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payments_report_all():
    payments = Payment.query.all()
    payments_data = []
    for payment in payments:
        payment_data = payment.serialize()
        payment_data["payer_name"] = f"{payment.payer.nombre} {payment.payer.apellidos}" if payment.payer else None
        payment_data["guest_name"] = f"{payment.guest.nombre} {payment.guest.apellidos}" if payment.guest else None
        payment_data["user_name"] = f"{payment.user.name} {payment.user.lastname}" if payment.user else None
        payment_data["church_name"] = payment.guest.church.nombre if payment.guest and payment.guest.church else None
        payment_data["church_area"] = payment.guest.church.area if payment.guest and payment.guest.church else None
        payment_data["directive_name"] = payment.guest.directive.nombre if payment.guest and payment.guest.directive else None
        payments_data.append(payment_data)
    return jsonify(payments_data)





@payment_bp.route("/payments/details", methods=["GET"])
@jwt_required
@roles_required(["Editor", "Viewer"])
def get_payments_details():
    guests = Guest.query.options(
        joinedload(Guest.church),
        joinedload(Guest.directive),
        joinedload(Guest.payments_received).joinedload(Payment.payer)
    ).order_by(Guest.fecha_registro.desc()).all()
    
    payments_data = []
    for guest in guests:
        guest_data = guest.serialize()
        guest_data["church_area"] = guest.church.area if guest.church else None
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


@payment_bp.route("/payments/guests", methods=["POST"])
@jwt_required
@roles_required(["Editor"])
def create_payment_guest():
    data = request.json
    id_user = current_user.id
    
    first_payment = data.get("first_payment") if data.get("first_payment") != '' else None
    second_payment = data.get("second_payment") if data.get("second_payment") != '' else None
    observaciones = data.get("observaciones") if data.get("observaciones") != '' else None
    
    
    nombre = data.get("nombre")
    apellidos = data.get("apellidos")
    telefono = data.get("telefono")
    position_id = data.get("position_id")
    church_id = data.get("church_id")
    directive_id = data.get("directive_id")
    
    if not nombre or not apellidos or not position_id:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    guest = Guest(
        nombre=nombre, 
        apellidos=apellidos, 
        telefono=telefono, 
        position_id=position_id if position_id not in [None, 0] else None, 
        church_id=church_id if church_id not in [None, 0] else None, 
        directive_id=directive_id if directive_id is not None else None,
    )
    
    guest.save()   
    
   
        
    id_guest = guest.id
    id_payer = guest.id
    
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





@payment_bp.route("/payments/guests/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(["Editor"])
def update_payment_guest(id):
    data = request.json
    guest = Guest.get_by_id(id)
    if not guest:
        return jsonify({"error": "Invitado no encontrado"}), 404
    nombre = data.get("nombre")
    apellidos = data.get("apellidos")
    email = data.get("email")
    telefono = data.get("telefono")
    position_id = data.get("position_id")
    church_id = data.get("church_id")
    directive_id = data.get("directive_id")
    code = data.get("code")

    guest.update(
        nombre=nombre, 
        apellidos=apellidos, 
        email=email, 
        telefono=telefono, 
        position_id=position_id if position_id is not None else None, 
        church_id=church_id if church_id not in [None, 0] else None, 
        directive_id=directive_id if directive_id not in [None, 0] else None,
        code=code if code is not None else None
    )
    
    id_user = current_user.id
    
    payment = Payment.query.filter_by(id_guest=id).first()
    if payment:
        id_guest = id
        id_payer = id
        
        first_payment = data.get("first_payment") if data.get("first_payment") != '' else None
        second_payment = data.get("second_payment") if data.get("second_payment") != '' else None
        observaciones = data.get("observaciones") if data.get("observaciones") != '' else None
        
        if not (first_payment or second_payment or observaciones):
            payment.delete()
        
        payment.update(id_payer=id_payer, id_guest=id, id_user=id_user, first_payment=first_payment, second_payment=second_payment, observaciones=observaciones)
    else:
        
        first_payment = data.get("first_payment") if data.get("first_payment") != '' else None
        second_payment = data.get("second_payment") if data.get("second_payment") != '' else None
        observaciones = data.get("observaciones") if data.get("observaciones") != '' else None
        

        id_guest = id
        id_payer = id
        payment = Payment(id_payer=id_payer, id_guest=id_guest, id_user=id_user, first_payment=first_payment, second_payment=second_payment, observaciones=observaciones)
        payment.save()
    
    return jsonify(payment.serialize())







@payment_bp.route("/payments/guests/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(["Editor"])
def delete_payment_guest(id):
    guest = Guest.get_by_id(id)
    if guest:
        payments = Payment.query.filter_by(id_guest=id).all()
        for payment in payments:
            payment.delete()
        guest.delete()
        return "", 204
    else:
        return jsonify({"error": "Invitado no encontrado"}), 404




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