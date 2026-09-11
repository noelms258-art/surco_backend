from app.db import get_db_connection


def get_tipo_activos_servcice():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT COD_TIPO_ACTIVO, tipo_activo FROM activos"

        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {"codTipActivo": row["cod_tipo_activo"], "nomActivo": row["tipo_activo"]}
            for row in rows
        ]
    finally:
        conn.close()


def insert_activos_servicio(data, cod_cliente):
    activos = data.get("activos", [])

    if not isinstance(activos, list) or len(activos) == 0:
        raise ValueError("activos debe ser una lista con al menos 1 elemento")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()


        sql = """
            INSERT INTO activos_clientes
            (cod_cliente, nom_activo, cod_tipo_activo, coste, vida_util, fec_compra)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        params = []
        for activo in activos:
            if activo.get("codTipActivo") is None:
                raise ValueError("Cada compra debe llevar un activo")

            params.append(
                (
                    cod_cliente,
                    activo.get("nomActivo"),
                    activo.get("codTipActivo"),
                    float(activo.get("txtImp")),
                    int(activo.get("txtVidaUtil")),
                    activo.get("fechaActivo"),
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
