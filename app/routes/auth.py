from flask import Blueprint, request, jsonify
from app.services.auth_service import login_usuario
from werkzeug.security import generate_password_hash

auth_bp = Blueprint("auth", __name__, url_prefix="/surco")


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    password_hash = generate_password_hash('Pass1234!')

    print(password_hash)

    datos = request.get_json(silent=True) or {}

    email = datos.get('email')
    password = datos.get('password')

    if not email or not password:
        return jsonify({
            'mensaje': 'Debe indicar email y contraseña'
        }), 400

    resultado = login_usuario(
        email,
        password
    )

    if resultado is None:
        return jsonify({
            'mensaje': 'Usuario o contraseña incorrectos'
        }), 401

    return jsonify(resultado), 200