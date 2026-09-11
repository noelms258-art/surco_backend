from flask import Blueprint, jsonify
from app.services.productos_service import get_productos_by_tipo, get_clases_producto, get_producto_user_service
from flask_jwt_extended import jwt_required, get_jwt_identity

productos_bp = Blueprint("productos", __name__, url_prefix="/surco")


@productos_bp.route("/<clas_prod>/productos", methods=["GET"])
@jwt_required()
def get_productos(clas_prod):
    productos = get_productos_by_tipo(clas_prod)
    return jsonify(productos)


@productos_bp.route("/clases", methods=["GET"])
@jwt_required()
def get_clases():
    clases = get_clases_producto()
    return jsonify(clases)

@productos_bp.route("/productosUser", methods=["GET"])
@jwt_required()
def get_productos_usuario():
    cod_cliente = get_jwt_identity()
    productos = get_producto_user_service(cod_cliente)
    return jsonify(productos)