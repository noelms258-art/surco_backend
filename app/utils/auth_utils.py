from flask_jwt_extended import get_jwt_identity


def obtener_cod_cliente_actual():

    cod_cliente = get_jwt_identity()

    if cod_cliente is None:
        return None

    return cod_cliente