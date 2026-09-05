from flask import Blueprint, jsonify, request
from app.services.reportes_service import get_ingresos_totales_service, get_gastos_totales_service, get_grafica_culotivo_services, get_grafica_campos_servicio


reportes_eco_bp = Blueprint("reportes", __name__, url_prefix="/surco")


@reportes_eco_bp.route("/<user_name>/ingresosTotales", methods=["GET"])
def get_ingresos_totales(user_name):
    result = get_ingresos_totales_service(user_name)
    return jsonify(result)

@reportes_eco_bp.route("/<user_name>/gastossTotales", methods=["GET"])
def get_gastos_totales(user_name):
    result = get_gastos_totales_service(user_name)
    return jsonify(result)

@reportes_eco_bp.route("/<user_name>/graficaCultivos", methods=["GET"])
def get_grafica_culotivos(user_name):
    result = get_grafica_culotivo_services(user_name)
    return jsonify(result)

@reportes_eco_bp.route("/<user_name>/graficaCampos", methods=["GET"])
def get_grafica_campos(user_name):
    result = get_grafica_campos_servicio(user_name)
    return jsonify(result)