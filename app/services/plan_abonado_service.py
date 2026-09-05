from app.db import get_db_connection
from datetime import datetime


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
        " MACRO_P, MACRO_N, MACRO_K, MACRO_CA, MICRO_FE, MICRO_ZN, MICRO_MN, MICRO_CU"
        " from Plan_Abonado"
        " where COD_CAMPO = ? and EJERCICIO = ?",
        params,
    )
    rows = cursor.fetchall()

    for r in rows:
        mes = r[0]
        if mes in resultado:
            resultado[mes]["nutrientes"] = {
                "fosforo": r[1],
                "nitrogeno": r[2],
                "potasio": r[3],
                "calcio": r[4],
                "hierro": r[5],
                "zinc": r[6],
                "manganeso": r[7],
                "cobre": r[8],
            }

    cursor.execute(
        "select (CASE pl.MES WHEN 1 THEN 'Enero' WHEN 2 THEN 'Febrero' WHEN 3 THEN 'Marzo' WHEN 4 THEN 'Abril' WHEN 5 THEN 'Mayo' WHEN 6 THEN 'Junio' WHEN 7 THEN 'Julio'"
        " WHEN 8 THEN 'Agosto' WHEN 9 THEN 'Septiembre' WHEN 10 THEN 'Octubre' WHEN 11 THEN 'Noviembre' WHEN 12 THEN 'Diciembre' END) AS MES , p.NOM_PRODUCTO, pl.CANTIDAD"
        " from Productos_plan pl"
        " join Productos p on p.COD_PRODUCTO = pl.COD_PROD"
        " where pl.COD_CAMPO = ? and pl.EJERCICIO = ?",
        params,
    )
    rows = cursor.fetchall()

    for r in rows:
        mes = r[0]
        if mes in resultado:
            resultado[mes]["productos"].append({"nomProd": r[1], "cant": r[2]})

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
        SELECT MACRO_P, MACRO_N, MACRO_K, MACRO_CA,
               MICRO_FE, MICRO_ZN, MICRO_MN, MICRO_CU
        FROM Productos
        WHERE COD_PRODUCTO = ?
    """

    for prod in prods:
        cod_prod = prod.get("codProd")
        cantidad = float(prod.get("cant") or 0)

        cursor.execute(sql_nutrientes_producto, (cod_prod,))
        row = cursor.fetchone()

        if not row:
            raise ValueError(f"No se encontró el producto con código {cod_prod}")

        totales["fosforo"] += (row[0] or 0) * cantidad
        totales["nitrogeno"] += (row[1] or 0) * cantidad
        totales["potasio"] += (row[2] or 0) * cantidad
        totales["calcio"] += (row[3] or 0) * cantidad
        totales["hierro"] += (row[4] or 0) * cantidad
        totales["zinc"] += (row[5] or 0) * cantidad
        totales["manganeso"] += (row[6] or 0) * cantidad
        totales["cobre"] += (row[7] or 0) * cantidad

    return totales


def insert_plan_abonado_service(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    plan_meses = data.get("meses", {})
    cod_campo = data.get("codCampo", "")

    try:
        select = "SELECT COD_ABONADO FROM Plan_Abonado ORDER BY COD_ABONADO DESC LIMIT 1"
        cursor.execute(select)
        row = cursor.fetchone()
        cod_plan = int(row[0]) if row and row[0] is not None else 0
        cod_plan += 1

        sql = """
            INSERT INTO Plan_Abonado (
                COD_ABONADO, COD_CAMPO, EJERCICIO, MES, COD_PRODUCTO, CANTIDAD,
                MACRO_P, MACRO_N, MACRO_K, MACRO_CA,
                MICRO_FE, MICRO_ZN, MICRO_MN, MICRO_CU
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        sqlProds = """
            INSERT INTO Productos_plan (
                COD_ABONADO, COD_CAMPO, COD_PROD, MES, EJERCICIO, CANTIDAD
            )
            VALUES (?, ?, ?, ?, ?, ?)
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
                for k in ["fosforo", "nitrogeno", "potasio", "calcio", "hierro", "zinc", "manganeso", "cobre"]
            )

            if len(prods) == 0 and nutrientes_vacios:
                continue

            # Insertar productos del mes
            for prod in prods:
                paramsProd = (
                    cod_plan,
                    cod_campo,
                    prod.get("codProd"),
                    mes_num,
                    ejer,
                    prod.get("cant"),
                )
                cursor.execute(sqlProds, paramsProd)

            # Si no vienen nutrientes pero sí productos, los calculamos
            if nutrientes_vacios and len(prods) > 0:
                nutrs = calcular_nutrientes_desde_productos(cursor, prods)

            params = (
                cod_plan,
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
            insertados += 1

        conn.commit()
        return {"ok": True, "insertados": insertados, "IdPlan": cod_plan}, 201

    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}, 500

    finally:
        cursor.close()
        conn.close()