from app.db import get_db_connection


def get_tipo_activos_servcice():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT COD_TIPO_ACTIVO, NOM_ACTIVO FROM Tipo_Activos"

        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {"codTipActivo": row["COD_TIPO_ACTIVO"], "nomActivo": row["NOM_ACTIVO"]}
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

        cursor.execute(
            "SELECT cod_activo FROM Activos ORDER BY cod_activo DESC LIMIT 1"
        )
        row = cursor.fetchone()
        cod_activo = int(row["cod_activo"]) if row else 0

        sql = """
            INSERT INTO Activos
            (cod_activo, cod_cliente, nom_activo, tip_activo, coste_activo, vida_util, fec_compra)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        params = []
        for activo in activos:
            if activo.get("codTipActivo") is None:
                raise ValueError("Cada compra debe llevar un activo")

            cod_activo += 1
            params.append(
                (
                    cod_activo,
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
            "ultimoCodGasto": cod_activo,
        }
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
