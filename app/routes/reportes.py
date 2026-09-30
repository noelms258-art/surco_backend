from flask import Blueprint, jsonify, request
from app.services.reportes_service import get_ingresos_totales_service, get_gastos_totales_service, get_grafica_culotivo_services, get_grafica_campos_servicio
from flask_jwt_extended import jwt_required, get_jwt_identity


reportes_eco_bp = Blueprint("reportes", __name__, url_prefix="/surco")


@reportes_eco_bp.route("/ingresosTotales", methods=["GET"])
@jwt_required()
def get_ingresos_totales():
    cod_cliente = get_jwt_identity()
    result = get_ingresos_totales_service(cod_cliente)
    return jsonify(result)

@reportes_eco_bp.route("/gastossTotales", methods=["GET"])
@jwt_required()
def get_gastos_totales():
    cod_cliente = get_jwt_identity()
    result = get_gastos_totales_service(cod_cliente)
    return jsonify(result)

@reportes_eco_bp.route("/graficaCultivos", methods=["GET"])
@jwt_required()
def get_grafica_culotivos():
    cod_cliente = get_jwt_identity()
    result = get_grafica_culotivo_services(cod_cliente)
    return jsonify(result)

@reportes_eco_bp.route("/graficaCampos", methods=["GET"])
@jwt_required()
def get_grafica_campos():
    cod_cliente = get_jwt_identity()
    result = get_grafica_campos_servicio(cod_cliente)
    return jsonify(result)