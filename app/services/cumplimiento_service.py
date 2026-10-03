from app.db import get_db_connection
from datetime import datetime
import math
from decimal import Decimal

from app.utils.utils import obtener_mes_cierre


def get_cumplimiento_resumen_service(cod_campo):
    conn = get_db_connection()
    cursor = conn.cursor()

    mes_cierre = obtener_mes_cierre(cursor, cod_campo)
    anio_inicio = datetime.now().year
    anio_fin = anio_inicio + 1

    params = (cod_campo, datetime.now().month, datetime.now().year)
    param_year = (cod_campo, anio_inicio, mes_cierre, anio_fin, mes_cierre)

    cursor.execute(
        "select MACRO_PH + MACRO_N + MACRO_K + MACRO_CA + MICRO_FE + MICRO_ZN + MICRO_MN + MICRO_CU AS total_mensual from Plan_Abonado where COD_CAMPO = %s and MES = %s and EJERCICIO = %s",
        params,
    )
    row = cursor.fetchone()
    print("ROW:", row)
    print("TIPO:", type(row))
    total_mensual = row["total_mensual"] if row and row["total_mensual"] is not None else 0

    cursor.execute(
        "select sum(MACRO_PH) + sum(MACRO_N) + sum(MACRO_K) + sum(MACRO_CA) + sum(MICRO_FE) + sum(MICRO_ZN) + sum(MICRO_MN) + sum(MICRO_CU) AS total_anual from Plan_Abonado "
        "where COD_CAMPO = %s and ((ejercicio = %s AND mes > %s) OR (ejercicio = %s AND mes <= %s))",
        param_year,
    )
    row = cursor.fetchone()
    total_anual = row["total_anual"] if row and row["total_anual"] is not None else 0

    cursor.execute(
        """
            SELECT SUM(COALESCE(p.MACRO_PH, 0) * t.cant_trata + COALESCE(p.MACRO_N, 0) * t.cant_trata + COALESCE(p.MACRO_K, 0) * t.cant_trata +
            COALESCE(p.MACRO_CA, 0) * t.cant_trata + COALESCE(p.MICRO_FE, 0) * t.cant_trata + COALESCE(p.MICRO_ZN, 0) * t.cant_trata +
            COALESCE(p.MICRO_MN, 0) * t.cant_trata + COALESCE(p.MICRO_CU, 0) * t.cant_trata ) AS gasto
            FROM Tratamientos t, Productos p
            WHERE t.COD_PRODUCTO = p.COD_PRODUCTO
            AND t.COD_CAMPO = %s
            AND EXTRACT(MONTH FROM t.fec_trata) = %s
            AND EXTRACT(YEAR FROM t.fec_trata) = %s
        """,
        params,
    )
    row = cursor.fetchone()
    gasto_mensual = row["gasto"] if row and row["gasto"] is not None else 0

    cursor.execute(
        """
            SELECT SUM(COALESCE(p.MACRO_PH, 0) * t.cant_trata + COALESCE(p.MACRO_N, 0) * t.cant_trata + COALESCE(p.MACRO_K, 0) * t.cant_trata +
            COALESCE(p.MACRO_CA, 0) * t.cant_trata + COALESCE(p.MICRO_FE, 0) * t.cant_trata + COALESCE(p.MICRO_ZN, 0) * t.cant_trata +
            COALESCE(p.MICRO_MN, 0) * t.cant_trata + COALESCE(p.MICRO_CU, 0) * t.cant_trata) AS gasto
            FROM Tratamientos t, Productos p
            WHERE t.COD_PRODUCTO = p.COD_PRODUCTO
            AND t.COD_CAMPO = %s
            AND ((EXTRACT(YEAR FROM t.fec_trata) = %s AND EXTRACT(MONTH FROM t.fec_trata) > %s) OR
                (EXTRACT(YEAR FROM t.fec_trata) = %s AND EXTRACT(MONTH FROM t.fec_trata) <= %s))
        """,
        param_year,
    )
    row = cursor.fetchone()
    gasto_anual = row["gasto"] if row and row["gasto"] is not None else 0

    pct_anual = math.trunc((gasto_anual / total_anual) * 100) if total_anual else 0
    pct_mensual = (
        math.trunc((gasto_mensual / total_mensual) * 100) if total_mensual else 0
    )

    return {"pct_anual": pct_anual, "pct_mensual": pct_mensual}


def get_cumplimiento_total_service(cod_campo):
    conn = get_db_connection()
    cursor = conn.cursor()

    mes_cierre = obtener_mes_cierre(cursor, cod_campo)

    anio_inicio = datetime.now().year
    anio_fin = anio_inicio + 1

    params = (cod_campo, anio_inicio, mes_cierre, anio_fin, mes_cierre)
    cursor.execute(
        """
        SELECT MES,
               COALESCE(MACRO_PH, 0) AS fos,
               COALESCE(MACRO_N, 0) AS nit,
               COALESCE(MACRO_K, 0) AS pot,
               COALESCE(MACRO_CA, 0) AS cal,
               COALESCE(MICRO_FE, 0) AS hie,
               COALESCE(MICRO_ZN, 0) AS zin,
               COALESCE(MICRO_MN, 0) AS man,
               COALESCE(MICRO_CU, 0) AS cob
        FROM Plan_Abonado
        WHERE COD_CAMPO = %s
          AND ((ejercicio = %s AND mes > %s) OR (ejercicio = %s AND mes <= %s))
        """,
        params,
    )

    rows = cursor.fetchall()

    objetivos_meses = {}

    for r in rows:
        objetivos_meses[r["mes"]] = {
            "PH": r["fos"],
            "N": r["nit"],
            "K": r["pot"],
            "CA": r["cal"],
            "FE": r["hie"],
            "ZN": r["zin"],
            "MN": r["man"],
            "CU": r["cob"],
        }

    cursor.execute(
        """
        SELECT CAST(EXTRACT(MONTH FROM t.fec_trata) AS INTEGER) AS mes,
               SUM(COALESCE(p.MACRO_PH, 0) * t.cant_trata) AS fos,
               SUM(COALESCE(p.MACRO_N, 0) * t.cant_trata) AS nit,
               SUM(COALESCE(p.MACRO_K, 0) * t.cant_trata) AS pot,
               SUM(COALESCE(p.MACRO_CA, 0) * t.cant_trata) AS cal,
               SUM(COALESCE(p.MICRO_FE, 0) * t.cant_trata) AS hie,
               SUM(COALESCE(p.MICRO_ZN, 0) * t.cant_trata) AS zin,
               SUM(COALESCE(p.MICRO_MN, 0) * t.cant_trata) AS man,
               SUM(COALESCE(p.MICRO_CU, 0) * t.cant_trata) AS cob
        FROM Tratamientos t
        JOIN Productos p
          ON t.COD_PRODUCTO = p.COD_PRODUCTO
        WHERE t.COD_CAMPO = %s
          AND ((EXTRACT(YEAR FROM t.fec_trata) = %s AND EXTRACT(MONTH FROM t.fec_trata) > %s) OR 
          (EXTRACT(YEAR FROM t.fec_trata) = %s AND EXTRACT(MONTH FROM t.fec_trata) <= %s))
        GROUP BY EXTRACT(MONTH FROM t.fec_trata)
        ORDER BY EXTRACT(MONTH FROM t.fec_trata)
        """,
        params,
    )

    rows = cursor.fetchall()
    aplicado_meses = {}

    for r in rows:
        aplicado_meses[r["mes"]] = {
            "PH": r["fos"] or 0,
            "N": r["nit"] or 0,
            "K": r["pot"] or 0,
            "CA": r["cal"] or 0,
            "FE": r["hie"] or 0,
            "ZN": r["zin"] or 0,
            "MN": r["man"] or 0,
            "CU": r["cob"] or 0,
        }

    nombres_meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }

    resultado = []
    meses = list(range(1,13))

    meses_ordenados = (
        meses[mes_cierre:]
        + meses[:mes_cierre]
    )

    print("OBJETIVOS MESES:", objetivos_meses)
    print("APLICADO MESES:", aplicado_meses)

    for mes in meses_ordenados:

        objetivos = objetivos_meses.get(mes, {})
        aplicados = aplicado_meses.get(mes, {})

        nutrientes_planificados = [
            nutriente
            for nutriente, objetivo in objetivos.items()
            if objetivo > 0
        ]

        cantidad_nutrientes = len(nutrientes_planificados)

        if cantidad_nutrientes == 0:
            cumplimiento_total = 0
        else:
            peso_nutriente = Decimal("100") / Decimal(cantidad_nutrientes)
            cumplimiento_total = Decimal("0")

            for nutriente in nutrientes_planificados:

                objetivo = objetivos[nutriente]
                aplicado = aplicados.get(nutriente, Decimal("0"))
                porcentaje_nutriente = min(
                    aplicado / objetivo,
                    Decimal("1")
                )
                cumplimiento_total += (
                    porcentaje_nutriente * peso_nutriente
                )

        resultado.append(
            {
                "mes": nombres_meses[mes],
                "objetivo": 100 if cantidad_nutrientes > 0 else 0,
                "cumplimiento": float(round(cumplimiento_total, 2)),
            }
        )

    conn.close()

    return resultado


def get_cumplimiento_macros_service(cod_campo):
    conn = get_db_connection()
    cursor = conn.cursor()

    params = (
        datetime.now().month,
        datetime.now().year,
        cod_campo,
        datetime.now().year,
        datetime.now().month,
    )

    cursor.execute(
        """
        SELECT
            pl.MACRO_PH,
            COALESCE(SUM(COALESCE(p.MACRO_PH, 0) * COALESCE(t.cant_abonado, 0)), 0),
            pl.MACRO_N,
            COALESCE(SUM(COALESCE(p.MACRO_N, 0) * COALESCE(t.cant_abonado, 0)), 0),
            pl.MACRO_K,
            COALESCE(SUM(COALESCE(p.MACRO_K, 0) * COALESCE(t.cant_abonado, 0)), 0),
            pl.MACRO_CA,
            COALESCE(SUM(COALESCE(p.MACRO_CA, 0) * COALESCE(t.cant_abonado, 0)), 0),
            pl.MICRO_FE,
            COALESCE(SUM(COALESCE(p.MICRO_FE, 0) * COALESCE(t.cant_abonado, 0)), 0),
            pl.MICRO_ZN,
            COALESCE(SUM(COALESCE(p.MICRO_ZN, 0) * COALESCE(t.cant_abonado, 0)), 0),
            pl.MICRO_MN,
            COALESCE(SUM(COALESCE(p.MICRO_MN, 0) * COALESCE(t.cant_abonado, 0)), 0),
            pl.MICRO_CU,
            COALESCE(SUM(COALESCE(p.MICRO_CU, 0) * COALESCE(t.cant_abonado, 0)), 0)
        FROM Plan_Abonado pl
        LEFT JOIN Tratamientos t ON t.COD_CAMPO = pl.COD_CAMPO
            AND CAST(SUBSTR(t.fec_trata, 4, 2) AS INTEGER) = %s
            AND CAST(SUBSTR(t.fec_trata, -4) AS INTEGER) = %s
        LEFT JOIN Productos p ON t.COD_PRODUCTO = p.COD_PRODUCTO
        WHERE pl.COD_CAMPO = %s
            AND pl.EJERCICIO = %s
            AND pl.MES = %s
        GROUP BY
            pl.MACRO_PH,
            pl.MACRO_N,
            pl.MACRO_K,
            pl.MACRO_CA,
            pl.MICRO_FE,
            pl.MICRO_ZN,
            pl.MICRO_MN,
            pl.MICRO_CU
        """,
        params,
    )

    row = cursor.fetchone()

    if not row:
        return {"macros_anuales": {}}

    macros_anuales = {
        "macroP": {"objetivo": row[0] or 0, "cumplimiento": row[1] or 0},
        "macroN": {"objetivo": row[2] or 0, "cumplimiento": row[3] or 0},
        "macroK": {"objetivo": row[4] or 0, "cumplimiento": row[5] or 0},
        "macroCa": {"objetivo": row[6] or 0, "cumplimiento": row[7] or 0},
        "microFe": {"objetivo": row[8] or 0, "cumplimiento": row[9] or 0},
        "microZn": {"objetivo": row[10] or 0, "cumplimiento": row[11] or 0},
        "microMn": {"objetivo": row[12] or 0, "cumplimiento": row[13] or 0},
        "microCu": {"objetivo": row[14] or 0, "cumplimiento": row[15] or 0},
    }

    filtrado = {k: v for k, v in macros_anuales.items() if v["objetivo"] > 0}

    return {"macros_anuales": filtrado}


def get_cumplimiento_productos_service(cod_campo):
    conn = get_db_connection()
    cursor = conn.cursor()

    params = (
        datetime.now().month,
        datetime.now().year,
        cod_campo,
        datetime.now().year,
        datetime.now().month,
    )

    cursor.execute(
        """
        SELECT
            pp.cod_producto,
            p.NOM_PRODUCTO,
            pp.CANTIDAD AS OBJETIVO,
            COALESCE(SUM(t.CANTIDAD), 0) AS CUMPLIMIENTO
        FROM Productos_plan pp
        JOIN Productos p ON p.COD_PRODUCTO = pp.cod_producto
        LEFT JOIN Tratamientos t ON t.COD_CAMPO = pp.COD_CAMPO
            AND t.COD_PRODUCTO = pp.cod_producto
            AND CAST(SUBSTR(t.fec_trata, 4, 2) AS INTEGER) = %s
            AND CAST(SUBSTR(t.fec_trata, -4) AS INTEGER) = %s
        WHERE pp.COD_CAMPO = %s
            AND pp.EJERCICIO = %s
            AND pp.MES = %s
        GROUP BY
            pp.cod_producto,
            p.NOM_PRODUCTO,
            pp.CANTIDAD
        """,
        params,
    )

    rows = cursor.fetchall()

    productos = [
        {
            "codProd": r[0],
            "nomProd": r[1],
            "objetivo": r[2] or 0,
            "cumplimiento": r[3] or 0,
        }
        for r in rows
    ]

    return {"productos": productos}
