from app.db import get_db_connection
from datetime import datetime
from decimal import Decimal


def get_plan_abonado_service(params):
    conn = get_db_connection()
    cursor = conn.cursor()
    meses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    resultado = {mes: {"nutrientes": {}, "productos": []} for mes in meses}

    cursor.execute(
        "select (CASE MES WHEN 1 THEN 'Enero' WHEN 2 THEN 'Febrero' WHEN 3 THEN 'Marzo' WHEN 4 THEN 'Abril' WHEN 5 THEN 'Mayo' WHEN 6 THEN 'Junio' WHEN 7 THEN 'Julio'"
        " WHEN 8 THEN 'Agosto' WHEN 9 THEN 'Septiembre' WHEN 10 THEN 'Octubre' WHEN 11 THEN 'Noviembre' WHEN 12 THEN 'Diciembre' END) AS MES,"
        " MACRO_PH, MACRO_N, MACRO_K, MACRO_CA, MICRO_FE, MICRO_ZN, MICRO_MN, MICRO_CU"
        " from Plan_Abonado"
        " where COD_CAMPO = %s and EJERCICIO = %s",
        params,
    )
    rows = cursor.fetchall()

    for r in rows:
        mes = r["mes"]
        if mes in resultado:
            resultado[mes]["nutrientes"] = {
            "fosforo": r["macro_ph"],
            "nitrogeno": r["macro_n"],
            "potasio": r["macro_k"],
            "calcio": r["macro_ca"],
            "hierro": r["micro_fe"],
            "zinc": r["micro_zn"],
            "manganeso": r["micro_mn"],
            "cobre": r["micro_cu"],
        }

    cursor.execute(
        "select (CASE pl.MES WHEN 1 THEN 'Enero' WHEN 2 THEN 'Febrero' WHEN 3 THEN 'Marzo' WHEN 4 THEN 'Abril' WHEN 5 THEN 'Mayo' WHEN 6 THEN 'Junio' WHEN 7 THEN 'Julio'"
        " WHEN 8 THEN 'Agosto' WHEN 9 THEN 'Septiembre' WHEN 10 THEN 'Octubre' WHEN 11 THEN 'Noviembre' WHEN 12 THEN 'Diciembre' END) AS MES , p.NOM_PRODUCTO, pl.cantidad"
        " from Productos_plan pl"
        " join Productos p on p.COD_PRODUCTO = pl.cod_producto"
        " where pl.COD_CAMPO = %s and pl.EJERCICIO = %s",
        params,
    )
    rows = cursor.fetchall()

    for r in rows:
        mes = r["mes"]
        if mes in resultado:
            resultado[mes]["productos"].append({"nomProd": r["nom_producto"], "cant": r["cantidad"]})

    conn.close()
    return resultado


def mes_a_numero(mes):
    meses = {
        "Enero": 1,
        "Febrero": 2,
        "Marzo": 3,
        "Abril": 4,
        "Mayo": 5,
        "Junio": 6,
        "Julio": 7,
        "Agosto": 8,
        "Septiembre": 9,
        "Octubre": 10,
        "Noviembre": 11,
        "Diciembre": 12,
    }
    return meses.get(mes)


def calcular_nutrientes_desde_productos(cursor, prods):
    totales = {
        "fosforo": 0,
        "nitrogeno": 0,
        "potasio": 0,
        "calcio": 0,
        "hierro": 0,
        "zinc": 0,
        "manganeso": 0,
        "cobre": 0,
    }

    sql_nutrientes_producto = """
        SELECT MACRO_PH, MACRO_N, MACRO_K, MACRO_CA,
               MICRO_FE, MICRO_ZN, MICRO_MN, MICRO_CU
        FROM Productos
        WHERE COD_PRODUCTO = %s
    """

    for prod in prods:
        cod_prod = prod.get("codProd")
        cantidad = Decimal(str(prod.get("cant") or 0))

        cursor.execute(sql_nutrientes_producto, (cod_prod,))
        row = cursor.fetchone()

        if not row:
            raise ValueError(f"No se encontró el producto con código {cod_prod}")

        totales["fosforo"] += (row["macro_ph"] or 0) * cantidad
        totales["nitrogeno"] += (row["macro_n"] or 0) * cantidad
        totales["potasio"] += (row["macro_k"] or 0) * cantidad
        totales["calcio"] += (row["macro_ca"] or 0) * cantidad
        totales["hierro"] += (row["micro_fe"] or 0) * cantidad
        totales["zinc"] += (row["micro_zn"] or 0) * cantidad
        totales["manganeso"] += (row["micro_mn"] or 0) * cantidad
        totales["cobre"] += (row["micro_cu"] or 0) * cantidad

    return totales


def insert_plan_abonado_service(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    plan_meses = data.get("meses", {})
    cod_campo = data.get("codCampo", "")

    try:
        sql = """
            INSERT INTO Plan_Abonado (COD_CAMPO, EJERCICIO, MES, COD_PRODUCTO, cant_abonado,
                MACRO_PH, MACRO_N, MACRO_K, MACRO_CA,
                MICRO_FE, MICRO_ZN, MICRO_MN, MICRO_CU
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING COD_ABONADO
        """

        sqlProds = """
            INSERT INTO Productos_plan (
               cod_abonado, COD_CAMPO, COD_PRODUCTO, MES, EJERCICIO, CANTIDAD
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        insertados = 0
        ejer = datetime.now().year

        for mes, plan_mes in plan_meses.items():

            mes_num = mes_a_numero(mes)

            if not mes_num:
                raise ValueError(f"Mes no válido: {mes}")

            prods = plan_mes.get("productos", [])
            nutrs = plan_mes.get("nutrientes", {}) or {}

            nutrientes_vacios = all(
                nutrs.get(k) in (None, "", 0)
                for k in [
                    "fosforo",
                    "nitrogeno",
                    "potasio",
                    "calcio",
                    "hierro",
                    "zinc",
                    "manganeso",
                    "cobre",
                ]
            )

            if len(prods) == 0 and nutrientes_vacios:
                continue

            # Si no vienen nutrientes pero sí productos, los calculamos
            if nutrientes_vacios and len(prods) > 0:
                nutrs = calcular_nutrientes_desde_productos(cursor, prods)

            # ----------------------------------------
            # 1. INSERTAMOS PLAN_ABONADO
            # ----------------------------------------

            params = (
                cod_campo,
                ejer,
                mes_num,
                None,
                None,
                nutrs.get("fosforo"),
                nutrs.get("nitrogeno"),
                nutrs.get("potasio"),
                nutrs.get("calcio"),
                nutrs.get("hierro"),
                nutrs.get("zinc"),
                nutrs.get("manganeso"),
                nutrs.get("cobre"),
            )

            cursor.execute(sql, params)

            # Recuperamos el COD_ABONADO recién generado
            row = cursor.fetchone()
            cod_abonado = row["cod_abonado"]

            print("COD_ABONADO generado:", cod_abonado)

            # ----------------------------------------
            # 2. INSERTAMOS LOS PRODUCTOS
            # ----------------------------------------

            for prod in prods:

                paramsProd = (
                    cod_abonado,
                    cod_campo,
                    prod.get("codProd"),
                    mes_num,
                    ejer,
                    prod.get("cant"),
                )

            cursor.execute(sqlProds, paramsProd)

            insertados += 1

        conn.commit()
        return {"ok": True, "insertados": insertados}, 201

    except Exception as e:
        conn.rollback()

        import traceback

        print("========== ERROR INSERT PLAN ABONADO ==========")
        print("TIPO ERROR:", type(e).__name__)
        print("ERROR STR:", str(e))
        print("ERROR REPR:", repr(e))
        traceback.print_exc()

        return {"ok": False, "error": repr(e), "tipo": type(e).__name__}, 500

    finally:
        cursor.close()
        conn.close()
