from flask import Blueprint, jsonify, request
from app.services.activos_service import get_tipo_activos_servcice, insert_activos_servicio
from flask_jwt_extended import jwt_required, get_jwt_identity

activos_bp = Blueprint("activos", __name__, url_prefix="/surco")


@activos_bp.route("/activos", methods=["GET"])
@jwt_required()
def get_tipo_activos():
    activos = get_tipo_activos_servcice()
    return jsonify(activos)

@activos_bp.route("/activos", methods=["POST"])
@jwt_required()
def insert_activos():
    cod_cliente = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    try:
        result = insert_activos_servicio(data, cod_cliente)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500