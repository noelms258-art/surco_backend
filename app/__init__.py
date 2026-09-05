from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.routes.usuarios import usuarios_bp
from app.routes.productos import productos_bp
from app.routes.gastos import gastos_bp
from app.routes.tratamientos import tratamientos_bp
from app.routes.tareas import tareas_bp
from app.routes.plan_abonado import plan_abonado_bp
from app.routes.cumplimiento import cumplimiento_bp
from app.routes.reportes import reportes_eco_bp
from app.routes.activos import activos_bp
from app.routes.auth import auth_bp
from app.routes.ingresos import ingresos_bp

from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    JWTManager(app)

    app.register_blueprint(usuarios_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(gastos_bp)
    app.register_blueprint(tratamientos_bp)
    app.register_blueprint(tareas_bp)
    app.register_blueprint(plan_abonado_bp)
    app.register_blueprint(cumplimiento_bp)
    app.register_blueprint(reportes_eco_bp)
    app.register_blueprint(activos_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ingresos_bp)

    return app