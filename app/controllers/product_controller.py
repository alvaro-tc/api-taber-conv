from flask import Blueprint, request, jsonify
from models.product_model import Product
from views.product_view import render_product_list, render_product_detail
from utils.decorators import jwt_required, roles_required

product_bp = Blueprint("product", __name__)


@product_bp.route("/products", methods=["GET"])
@jwt_required
@roles_required(roles=["admin", "user"])
def get_products():
    products = Product.get_all()
    return jsonify(render_product_list(products))


@product_bp.route("/products/<int:id>", methods=["GET"])
@jwt_required
@roles_required(roles=["admin", "user"])
def get_product(id):
    product = Product.get_by_id(id)
    if product:
        return jsonify(render_product_detail(product))
    return jsonify({"error": "Producto no encontrado"}), 404


@product_bp.route("/products", methods=["POST"])
def create_product():
    data = request.json
    name = data.get("name",None)
    description = data.get("description",None)
    price = data.get("price",0)
    stock = data.get("stock",0)
    if not name or not description or not  price>=0 or not stock>=0 :
        return jsonify({"error": "Faltan datos requeridos"}), 400
    product = Product(name=name, description=description, price=price, stock=stock)
    product.save()
    return jsonify(render_product_detail(product)), 201



@product_bp.route("/products/<int:id>", methods=["PUT"])
@jwt_required
@roles_required(roles=["admin"])
def update_product(id):
    product = Product.get_by_id(id)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404
    data = request.json
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    stock = data.get("stock")
    product.update(name=name, description=description, price=price, stock=stock)

    return jsonify(render_product_detail(product))


@product_bp.route("/products/<int:id>", methods=["DELETE"])
@jwt_required
@roles_required(roles=["admin"])
def delete_product(id):
    product = Product.get_by_id(id)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404
    product.delete()
    return "", 204