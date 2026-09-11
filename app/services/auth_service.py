from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from app.db import get_db_connection


def login_usuario(email, password):

    conexion = get_db_connection()

    usuario = conexion.execute(
        '''
        SELECT
            cod_cliente,
            email,
            contra
        FROM Usuarios
        WHERE email = %s
        ''',
        (email,)
    ).fetchone()

    if usuario is None:
        return None

    if not check_password_hash(
        usuario['contra'],
        password
    ):
        return None

    token = create_access_token(
        identity=str(usuario['cod_cliente'])
    )

    return {
        'token': token,
        'usuario': {
            'cod_cliente': usuario['cod_cliente'],
            'email': usuario['email']
        }
    }