from app.db import get_db_connection
from datetime import datetime


def insert_tratamientos_service(tratamientos, campo, cod_cliente):
    if not isinstance(tratamientos, list) or len(tratamientos) == 0:
        raise ValueError("tratamientos debe ser una lista con al menos 1 elemento")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        sql = """
            INSERT INTO Tratamientos
            (COD_GASTO, COD_PRODUCTO, cant_trata, COD_CAMPO, fec_trata, COD_CLIENTE)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        params = []

        for trat in tratamientos:
            print(trat)
            if trat.get("codProd") is None:
                raise ValueError("Cada tratamiento debe tener un producto")

            dt = datetime.fromisoformat(trat.get("fechaTrat").replace("Z", "+00:00"))
            fecha_formateada = dt.strftime("%d/%m/%Y")

            params.append(
                (
                    None,
                    trat.get("codProd"),
                    float(trat.get("cantTrat")),
                    campo,
                    fecha_formateada,
                    cod_cliente
                )
            )

        cursor.executemany(sql, params)
        conn.commit()

        return {
            "ok": True,
            "insertados": len(params),
        }

    except:
        conn.rollback()
        raise
    finally:
        conn.close()
