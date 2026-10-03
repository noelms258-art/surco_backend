from app.db import get_db_connection

def get_tipo_ingresos():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT COD_TIP_INGRESO, NOM_INGRESO, forma_ingreso, iva FROM ingresos"
       
        cursor.execute(query)
        rows = cursor.fetchall()

        return [{"codTipIngreso": row["cod_tip_ingreso"], "nomIngreso": row["nom_ingreso"], "fromIngreso": row["forma_ingreso"], "iva": row["iva"]} for row in rows]
    finally:
        conn.close()


def insert_ingresos_service(data, cod_cliente):
    ingresos = data.get("ingresos", [])

    if not isinstance(ingresos, list) or len(ingresos) == 0:
        raise ValueError("ingresos debe ser una lista con al menos 1 elemento")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        sql = """
            INSERT INTO ingresos_clientes
            (cod_tip_ingreso, cod_campo, kg_ingreso, imp_ingreso, total_bruto, iva, total_neto, fec_ingreso, estimado, cod_fruta, cod_cliente)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = []
        for ingreso in ingresos:
            if ingreso.get("codTipIngreso") is None:
                raise ValueError("Cada compra debe llevar un activo")

            tip_cobro = ingreso.get("tipCobro") or ""

            kg_ingreso = None
            imp_ingreso = None
            total_bruto = None
            cod_campo = None

            if "C" in tip_cobro:
                cod_campo = ingreso.get("codCampo")

            if "K" in tip_cobro:
                kg_ingreso = float(str(ingreso.get("txtKgs") or 0).replace(",", "."))
                imp_ingreso = float(str(ingreso.get("txtImpKgs") or 0).replace(",", "."))
                total_bruto = kg_ingreso * imp_ingreso
            elif "H" in tip_cobro:
                total_bruto = float(str(ingreso.get("txtHoras") or 0).replace(",", ".")) * float(str(ingreso.get("txtImpHoras") or 0).replace(",", "."))
            elif "I" in tip_cobro:
                total_bruto = float(str(ingreso.get("txtImporte") or 0).replace(",", "."))

            imp_iva = total_bruto * (float(str(ingreso.get("iva") or 0).replace(",", ".")) / 100)
            total_neto = total_bruto - imp_iva
            
            params.append(
                (
                    ingreso.get("codTipIngreso"),
                    cod_campo,
                    kg_ingreso,
                    imp_ingreso if imp_ingreso is not None else total_bruto,
                    total_bruto,
                    imp_iva,
                    total_neto,
                    ingreso.get("fecIngreso"),
                    None,
                    None,
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