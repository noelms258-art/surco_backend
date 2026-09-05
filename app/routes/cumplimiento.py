from flask import Blueprint, jsonify, request
from app.services.cumplimiento_service import (
    get_cumplimiento_resumen_service,
    get_cumplimiento_total_service,
    get_cumplimiento_macros_service,
    get_cumplimiento_productos_service
)
from flask_jwt_extended import jwt_required, get_jwt_identity

cumplimiento_bp = Blueprint("cumplimiento", __name__, url_prefix="/surco/cumplimiento")


@cumplimiento_bp.route("/resumen", methods=["GET"])
@jwt_required()
def get_cumplimiento_resumen():
    cod_campo = request.args.get("codCampo")

    if not cod_campo:
        return jsonify({"ok": False, "error": "El parámetro codCampo es obligatorio"}), 400

    try:
        result = get_cumplimiento_resumen_service(cod_campo)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@cumplimiento_bp.route("/total", methods=["GET"])
@jwt_required()
def get_cumplimiento_total():
    cod_campo = request.args.get("codCampo")

    if not cod_campo:
        return jsonify({"ok": False, "error": "El parámetro codCampo es obligatorio"}), 400

    try:
        result = get_cumplimiento_total_service(cod_campo)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@cumplimiento_bp.route("/macros", methods=["GET"])
@jwt_required()
def get_cumplimiento_macros():
    cod_campo = request.args.get("codCampo")

    if not cod_campo:
        return jsonify({"ok": False, "error": "El parámetro codCampo es obligatorio"}), 400

    try:
        result = get_cumplimiento_macros_service(cod_campo)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@cumplimiento_bp.route("/productos", methods=["GET"])
@jwt_required()
def get_cumplimiento_productos():
    cod_campo = request.args.get("codCampo")

    if not cod_campo:
        return jsonify({"ok": False, "error": "El parámetro codCampo es obligatorio"}), 400

    try:
        result = get_cumplimiento_productos_service(cod_campo)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500