from flask import Blueprint, jsonify, request
from app.services.gastos_service import insert_gastos_agricolas, get_gasto_by_clase, get_gasto_by_tipo, insert_gasto
from flask_jwt_extended import jwt_required, get_jwt_identity

gastos_bp = Blueprint("gastos", __name__, url_prefix="/surco")


@gastos_bp.route("/insert/gastosProd", methods=["POST"])
@jwt_required()
def insert_gastos_argicolas():
    cod_cliente = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    try:
        result = insert_gastos_agricolas(data, cod_cliente)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@gastos_bp.route("/<tip_gasto>/claseGasto", methods=["GET"])
@jwt_required()
def gastos_clase(tip_gasto):
    gastos_clases = get_gasto_by_tipo(tip_gasto)
    return jsonify(gastos_clases)

@gastos_bp.route("/<clas_gasto>/gastos", methods=["GET"])
@jwt_required()
def get_productos(clas_gasto):
    gastos = get_gasto_by_clase(clas_gasto)
    return jsonify(gastos)

@gastos_bp.route("/insert/gastos", methods=["POST"])
@jwt_required()
def insert_gastos():
    cod_cliente = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    try:
        result = insert_gasto(data, cod_cliente)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500