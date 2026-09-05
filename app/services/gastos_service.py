from app.db import get_db_connection


def insert_gastos_agricolas(data, cod_cliente):
    gastos = data.get("gastosAgricolas", [])

    if not isinstance(gastos, list) or len(gastos) == 0:
        raise ValueError("gastosAgricolas debe ser una lista con al menos 1 elemento")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COD_GASTO FROM Gastos_Producto ORDER BY COD_GASTO DESC LIMIT 1"
        )
        row = cursor.fetchone()
        cod_gasto = row["COD_GASTO"] if row else 0

        sql = """
            INSERT INTO Gastos_Producto
            (COD_GASTO, COD_CAMPO, COD_PRODUCTO, COD_EMPLEADO, HORAS, IMPORTE, CANTIDAD, FECHA_GASTO)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = []
        for gasto in gastos:
            if gasto.get("codProd") is None:
                raise ValueError("Cada gasto debe tener un producto")

            cod_gasto += 1
            params.append(
                (
                    cod_gasto,
                    None,
                    gasto.get("codProd"),
                    cod_cliente,
                    None,
                    float(gasto.get("txtImp")),
                    int(gasto.get("txtUnd")),
                    gasto.get("fechaGast"),
                )
            )

        cursor.executemany(sql, params)
        conn.commit()

        return {
            "ok": True,
            "insertados": len(params),
            "ultimoCodGasto": cod_gasto,
        }
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_gasto_by_tipo(tip_gasto):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT DISTINCT CLASS_GASTO FROM Gastos_Clase"
        params = []

        if tip_gasto != "none":
            query += " WHERE TIP_GASTO = ?"
            params.append(tip_gasto)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [{"classGasto": row["CLASS_GASTO"]} for row in rows]
    finally:
        conn.close()


def get_gasto_by_clase(clas_gasto):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT COD_TIP_GASTO, NOM_GASTO FROM Gastos_Clase"
        params = []

        if clas_gasto != "none":
            query += " WHERE CLASS_GASTO = ?"
            params.append(clas_gasto)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {"codTipGasto": row["COD_TIP_GASTO"], "nomGasto": row["NOM_GASTO"]}
            for row in rows
        ]
    finally:
        conn.close()


def insert_gasto(data, cod_cliente):
    gastos = data.get("gastos", [])

    if not isinstance(gastos, list) or len(gastos) == 0:
        raise ValueError("gastos debe ser una lista con al menos 1 elemento")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COD_GASTO FROM Gastos ORDER BY COD_GASTO DESC LIMIT 1")
        row = cursor.fetchone()
        cod_gasto = int(row["COD_GASTO"]) if row else 0

        sql = """
           INSERT INTO Gastos
            (cod_gasto, cod_tip_gasto, cod_cliente, tipo, subtipo, unidades, horas, importe, cod_campo, fecha, consumido, importe_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        params = []
        for gasto in gastos:
            if gasto.get("codTipGasto") is None:
                raise ValueError("Cada gasto debe tener un gasto")

            cod_gasto += 1
            if data.get("cantidad") in (None, ""):
                params.append(
                    (
                        str(cod_gasto),
                        gasto.get("codTipGasto"),
                        cod_cliente,  # Aqui falta el cliente que inserta el gasto
                        None,
                        None,
                        None,
                        None,
                        float(gasto.get("txtImp")),
                        gasto.get("codCampo"),
                        gasto.get("fechaGast"),
                        None,
                        float(gasto.get("txtImp")),
                    )
                )
            else:
                params.append(
                    (
                        str(cod_gasto),
                        gasto.get("codTipGasto"),
                        cod_cliente,  # Aqui falta el cliente que inserta el gasto
                        None,
                        None,
                        int(gasto.get("txtUnd")),
                        None,
                        float(gasto.get("txtImp")),
                        gasto.get("codCampo"),
                        gasto.get("fechaGast"),
                        None,
                        int(gasto.get("txtUnd")) * float(gasto.get("txtImp")),
                    )
                )

        cursor.executemany(sql, params)
        conn.commit()

        return {
            "ok": True,
            "insertados": len(params),
            "ultimoCodGasto": cod_gasto,
        }
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
