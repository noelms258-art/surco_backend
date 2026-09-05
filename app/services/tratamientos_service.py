from app.db import get_db_connection
from datetime import datetime


def insert_tratamientos_service(tratamientos, campo, cod_cliente):
    if not isinstance(tratamientos, list) or len(tratamientos) == 0:
        raise ValueError("tratamientos debe ser una lista con al menos 1 elemento")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COD_TRATAMIENTO FROM Tratamientos ORDER BY COD_TRATAMIENTO DESC LIMIT 1"
        )
        row = cursor.fetchone()
        cod_trat = row["COD_TRATAMIENTO"] if row else 0

        sql = """
            INSERT INTO Tratamientos
            (COD_TRATAMIENTO, COD_GASTO_PROD, COD_PRODUCTO, CANTIDAD, COD_CAMPO, FECHA, COD_CLIENTE)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        params = []

        for trat in tratamientos:
            print(trat)
            if trat.get("codProd") is None:
                raise ValueError("Cada tratamiento debe tener un producto")

            dt = datetime.fromisoformat(trat.get("fechaTrat").replace("Z", "+00:00"))
            fecha_formateada = dt.strftime("%d/%m/%Y")

            cod_trat += 1

            params.append(
                (
                    cod_trat,
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
            "ultimoCodTratamiento": cod_trat,
        }

    except:
        conn.rollback()
        raise
    finally:
        conn.close()
