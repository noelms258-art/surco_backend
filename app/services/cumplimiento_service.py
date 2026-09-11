from app.db import get_db_connection
from datetime import datetime
import math


def get_cumplimiento_resumen_service(cod_campo):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (cod_campo, datetime.now().month, datetime.now().year)
    param_year = (
        cod_campo,
        datetime.now().year,
    )

    cursor.execute(
        "select MACRO_PH + MACRO_N + MACRO_K + MACRO_CA + MICRO_FE + MICRO_ZN + MICRO_MN + MICRO_CU AS total_mensual from Plan_Abonado where COD_CAMPO = %s and MES = %s and EJERCICIO = %s",
        params,
    )
    row = cursor.fetchone()
    total_mensual = row[0] if row else 0

    cursor.execute(
        "select sum(MACRO_PH) + sum(MACRO_N) + sum(MACRO_K) + sum(MACRO_CA) + sum(MICRO_FE) + sum(MICRO_ZN) + sum(MICRO_MN) + sum(MICRO_CU) AS total_anual from Plan_Abonado where COD_CAMPO = %s and EJERCICIO = %s",
        param_year,
    )
    row = cursor.fetchone()
    total_anual = row[0] if row else 0

    cursor.execute(
        "select (p.MACRO_PH * t.cant_abonado + MACRO_N * t.cant_abonado + MACRO_K * t.cant_abonado + MACRO_CA * t.cant_abonado + MICRO_FE * t.cant_abonado + MICRO_ZN * t.cant_abonado + MICRO_MN * t.cant_abonado + MICRO_CU * t.cant_abonado) AS gasto "
        "from Tratamientos t, Productos p where t.COD_PRODUCTO = p.COD_PRODUCTO and t.COD_CAMPO = %s and CAST(SUBSTR(t.fec_trata, 4, 2) AS INTEGER) = %s and CAST(substr(t.fec_trata, -4) AS INTEGER) = %s",
        params,
    )
    row = cursor.fetchone()
    gasto_mensual = row[0] if row else 0

    cursor.execute(
        "select (p.MACRO_PH * t.cant_abonado + MACRO_N * t.cant_abonado + MACRO_K * t.cant_abonado + MACRO_CA * t.cant_abonado + MICRO_FE * t.cant_abonado + MICRO_ZN * t.cant_abonado + MICRO_MN * t.cant_abonado + MICRO_CU * t.cant_abonado) AS gasto "
        "from Tratamientos t, Productos p where t.COD_PRODUCTO = p.COD_PRODUCTO and COD_CAMPO = %s and CAST(substr(t.fec_trata, -4) AS INTEGER) = %s",
        param_year,
    )
    row = cursor.fetchone()
    gasto_anual = row[0] if row else 0

    pct_anual = math.trunc((gasto_anual / total_anual) * 100) if total_anual else 0
    pct_mensual = (
        math.trunc((gasto_mensual / total_mensual) * 100) if total_mensual else 0
    )

    return {"pct_anual": pct_anual, "pct_mensual": pct_mensual}


def get_cumplimiento_total_service(cod_campo):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (cod_campo, datetime.now().year)
    cursor.execute(
        "select MES, "
        "COALESCE(MACRO_PH, 0) + "
        "COALESCE(MACRO_N, 0) + "
        "COALESCE(MACRO_K, 0) + "
        "COALESCE(MACRO_CA, 0) + "
        "COALESCE(MICRO_FE, 0) + "
        "COALESCE(MICRO_ZN, 0) + "
        "COALESCE(MICRO_MN, 0) + "
        "COALESCE(MICRO_CU, 0) AS total_mensual "
        "FROM Plan_Abonado "
        "WHERE COD_CAMPO = %s AND EJERCICIO = %s;",
        params,
    )
    rows = cursor.fetchall()
    total_meses = {r[0]: r[1] for r in rows}

    cursor.execute(
        "select CAST(SUBSTR(t.FECHA, 4, 2) AS INTEGER) AS mes, "
        "SUM("
        "COALESCE(p.MACRO_PH,0) * t.cant_abonado + "
        "COALESCE(p.MACRO_N,0) * t.cant_abonado + "
        "COALESCE(p.MACRO_K,0) * t.cant_abonado + "
        "COALESCE(p.MACRO_CA,0) * t.cant_abonado + "
        "COALESCE(p.MICRO_FE,0) * t.cant_abonado + "
        "COALESCE(p.MICRO_ZN,0) * t.cant_abonado + "
        "COALESCE(p.MICRO_MN,0) * t.cant_abonado + "
        "COALESCE(p.MICRO_CU,0) * t.cant_abonado"
        ") AS gasto "
        "from Tratamientos t "
        "join Productos p on t.COD_PRODUCTO = p.COD_PRODUCTO "
        "where t.COD_CAMPO = %s and CAST(SUBSTR(t.FECHA, -4) AS INTEGER) = %s "
        "group by mes "
        "order by mes",
        params,
    )
    rows = cursor.fetchall()
    gasto_meses = {r[0]: r[1] for r in rows}

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
    for mes in range(1, 13):
        resultado.append(
            {
                "mes": nombres_meses[mes],
                "objetivo": total_meses.get(mes, 0),
                "cumplimiento": gasto_meses.get(mes, 0),
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
