from app.db import get_db_connection


def insert_gastos_agricolas(data, cod_cliente):
    gastos = data.get("gastosAgricolas", [])

    if not isinstance(gastos, list) or len(gastos) == 0:
        raise ValueError("gastosAgricolas debe ser una lista con al menos 1 elemento")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        sql = """
            INSERT INTO gastos_productos
            (cod_producto, cod_cliente, unidades_prod, imp_ud_prod, imp_total_prod, cod_campo, fec_compra, uds_consumido)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = []
        for gasto in gastos:
            if gasto.get("codProd") is None:
                raise ValueError("Cada gasto debe tener un producto")

            params.append(
                (
                    gasto.get("codProd"),
                    cod_cliente,
                    int(gasto.get("txtUnd")),
                    float(gasto.get("txtImp")),
                    int(gasto.get("txtUnd")) * float(gasto.get("txtImp")) ,
                    None,
                    gasto.get("fechaGast"),
                    None
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


def get_gasto_by_tipo(tip_gasto):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT DISTINCT CLASS_GASTO FROM gastos"
        params = []

        if tip_gasto != "none":
            query += " WHERE TIP_GASTO = %s"
            params.append(tip_gasto)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [{"classGasto": row["class_gasto"]} for row in rows]
    finally:
        conn.close()


def get_gasto_by_clase(clas_gasto):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT COD_TIP_GASTO, NOM_GASTO FROM gastos"
        params = []

        if clas_gasto != "none":
            query += " WHERE CLASS_GASTO = %s"
            params.append(clas_gasto)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {"codTipGasto": row["cod_tip_gasto"], "nomGasto": row["nom_gasto"]}
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

        sql = """
           INSERT INTO gastos_cliente
            (cod_tip_gasto, cod_cliente, unidades, horas, imp_gasto, cod_campo, fec_gasto, consumido)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """

        params = []
        for gasto in gastos:
            if gasto.get("codTipGasto") is None:
                raise ValueError("Cada gasto debe tener un gasto")

            if data.get("cantidad") in (None, ""):
                params.append(
                    (
                        gasto.get("codTipGasto"),
                        cod_cliente,
                        None,
                        None,
                        float(gasto.get("txtImp")),
                        gasto.get("codCampo"),
                        gasto.get("fechaGast"),
                        None,
                    ),
                )
            else:
                params.append(
                    (
                        gasto.get("codTipGasto"),
                        cod_cliente,
                        int(gasto.get("txtUnd")),
                        None,
                        float(gasto.get("txtImp")),
                        gasto.get("codCampo"),
                        gasto.get("fechaGast"),
                        None,
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
