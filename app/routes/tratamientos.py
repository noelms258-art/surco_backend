from flask import Blueprint, jsonify, request
from app.services.tratamientos_service import insert_tratamientos_service
from flask_jwt_extended import jwt_required, get_jwt_identity


tratamientos_bp = Blueprint("tratamientos", __name__, url_prefix="/surco")


@tratamientos_bp.route("/tratamientos", methods=["POST"])
@jwt_required()
def insert_tratamientos():
    cod_cliente = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    tratamientos = data.get("tratamientos", [])
    campo = data.get("campo", "")
    try:
        result = insert_tratamientos_service(tratamientos, campo, cod_cliente)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
