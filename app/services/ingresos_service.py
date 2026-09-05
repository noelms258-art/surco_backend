from app.db import get_db_connection

def get_tipo_ingresos():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT COD_TIP_INGRESO, NOM_INGRESO, TIP_COBRO, USO_ACTIVO, CAMPO_ESPECIFICO FROM Ingresos_Clase"
       
        cursor.execute(query)
        rows = cursor.fetchall()

        return [{"codTipIngreso": row["COD_TIP_INGRESO"], "nomIngreso": row["NOM_INGRESO"], "tipCobro": row["TIP_COBRO"],
                  "usoActivo": row["USO_ACTIVO"], "campoEsp": row["CAMPO_ESPECIFICO"]} for row in rows]
    finally:
        conn.close()

def insert_ingresos_service(data, cod_cliente):
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