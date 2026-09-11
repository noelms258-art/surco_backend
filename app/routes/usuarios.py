from flask import Blueprint, jsonify
from app.services.usuarios_service import get_campos_by_user, get_empleados_by_user
from flask_jwt_extended import jwt_required, get_jwt_identity


usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/surco")


@usuarios_bp.route("/usuarios/campos", methods=["GET"])
@jwt_required()
def get_user_campos():
    cod_cliente = get_jwt_identity()

    campos = get_campos_by_user(cod_cliente)
    return jsonify(campos)


@usuarios_bp.route("/<user_name>/empleados", methods=["GET"])
@jwt_required()
def get_empleados(user_name):
    empleados = get_empleados_by_user(user_name)
    return jsonify(empleados)