from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ingresos_service import get_tipo_ingresos, insert_ingresos_service

ingresos_bp = Blueprint("ingresos", __name__, url_prefix="/surco")

@ingresos_bp.route("/ingresos", methods=["GET"])
@jwt_required()
def gastos_clase():
    ingresos = get_tipo_ingresos()
    return jsonify(ingresos)

@ingresos_bp.route("/ingresos", methods=["POST"])
@jwt_required()
def insert_ingresos():
    cod_cliente = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        result = insert_ingresos_service(data, cod_cliente)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500