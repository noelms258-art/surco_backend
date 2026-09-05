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
        "select MACRO_P + MACRO_N + MACRO_K + MACRO_CA + MICRO_FE + MICRO_ZN + MICRO_MN + MICRO_CU AS total_mensual from Plan_Abonado where COD_CAMPO = ? and MES = ? and EJERCICIO = ?",
        params,
    )
    row = cursor.fetchone()
    total_mensual = row[0] if row else 0

    cursor.execute(
        "select sum(MACRO_P) + sum(MACRO_N) + sum(MACRO_K) + sum(MACRO_CA) + sum(MICRO_FE) + sum(MICRO_ZN) + sum(MICRO_MN) + sum(MICRO_CU) AS total_anual from Plan_Abonado where COD_CAMPO = ? and EJERCICIO = ?",
        param_year,
    )
    row = cursor.fetchone()
    total_anual = row[0] if row else 0

    cursor.execute(
        "select (p.MACRO_P * t.cantidad + MACRO_N * t.cantidad + MACRO_K * t.cantidad + MACRO_CA * t.cantidad + MICRO_FE * t.cantidad + MICRO_ZN * t.cantidad + MICRO_MN * t.cantidad + MICRO_CU * t.cantidad) AS gasto "
        "from Tratamientos t, Productos p where t.COD_PRODUCTO = p.COD_PRODUCTO and t.COD_CAMPO = ? and CAST(SUBSTR(t.FECHA, 4, 2) AS INTEGER) = ? and CAST(substr(t.FECHA, -4) AS INTEGER) = ?",
        params,
    )
    row = cursor.fetchone()
    gasto_mensual = row[0] if row else 0

    cursor.execute(
        "select (p.MACRO_P * t.cantidad + MACRO_N * t.cantidad + MACRO_K * t.cantidad + MACRO_CA * t.cantidad + MICRO_FE * t.cantidad + MICRO_ZN * t.cantidad + MICRO_MN * t.cantidad + MICRO_CU * t.cantidad) AS gasto "
        "from Tratamientos t, Productos p where t.COD_PRODUCTO = p.COD_PRODUCTO and COD_CAMPO = ? and CAST(substr(t.FECHA, -4) AS INTEGER) = ?",
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
        "COALESCE(MACRO_P, 0) + "
        "COALESCE(MACRO_N, 0) + "
        "COALESCE(MACRO_K, 0) + "
        "COALESCE(MACRO_CA, 0) + "
        "COALESCE(MICRO_FE, 0) + "
        "COALESCE(MICRO_ZN, 0) + "
        "COALESCE(MICRO_MN, 0) + "
        "COALESCE(MICRO_CU, 0) AS total_mensual "
        "FROM Plan_Abonado "
        "WHERE COD_CAMPO = ? AND EJERCICIO = ?;",
        params,
    )
    rows = cursor.fetchall()
    total_meses = {r[0]: r[1] for r in rows}

    cursor.execute(
        "select CAST(SUBSTR(t.FECHA, 4, 2) AS INTEGER) AS mes, "
        "SUM("
        "COALESCE(p.MACRO_P,0) * t.CANTIDAD + "
        "COALESCE(p.MACRO_N,0) * t.CANTIDAD + "
        "COALESCE(p.MACRO_K,0) * t.CANTIDAD + "
        "COALESCE(p.MACRO_CA,0) * t.CANTIDAD + "
        "COALESCE(p.MICRO_FE,0) * t.CANTIDAD + "
        "COALESCE(p.MICRO_ZN,0) * t.CANTIDAD + "
        "COALESCE(p.MICRO_MN,0) * t.CANTIDAD + "
        "COALESCE(p.MICRO_CU,0) * t.CANTIDAD"
        ") AS gasto "
        "from Tratamientos t "
        "join Productos p on t.COD_PRODUCTO = p.COD_PRODUCTO "
        "where t.COD_CAMPO = ? and CAST(SUBSTR(t.FECHA, -4) AS INTEGER) = ? "
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
            pl.MACRO_P,
            COALESCE(SUM(COALESCE(p.MACRO_P, 0) * COALESCE(t.CANTIDAD, 0)), 0),
            pl.MACRO_N,
            COALESCE(SUM(COALESCE(p.MACRO_N, 0) * COALESCE(t.CANTIDAD, 0)), 0),
            pl.MACRO_K,
            COALESCE(SUM(COALESCE(p.MACRO_K, 0) * COALESCE(t.CANTIDAD, 0)), 0),
            pl.MACRO_CA,
            COALESCE(SUM(COALESCE(p.MACRO_CA, 0) * COALESCE(t.CANTIDAD, 0)), 0),
            pl.MICRO_FE,
            COALESCE(SUM(COALESCE(p.MICRO_FE, 0) * COALESCE(t.CANTIDAD, 0)), 0),
            pl.MICRO_ZN,
            COALESCE(SUM(COALESCE(p.MICRO_ZN, 0) * COALESCE(t.CANTIDAD, 0)), 0),
            pl.MICRO_MN,
            COALESCE(SUM(COALESCE(p.MICRO_MN, 0) * COALESCE(t.CANTIDAD, 0)), 0),
            pl.MICRO_CU,
            COALESCE(SUM(COALESCE(p.MICRO_CU, 0) * COALESCE(t.CANTIDAD, 0)), 0)
        FROM Plan_Abonado pl
        LEFT JOIN Tratamientos t ON t.COD_CAMPO = pl.COD_CAMPO
            AND CAST(SUBSTR(t.FECHA, 4, 2) AS INTEGER) = ?
            AND CAST(SUBSTR(t.FECHA, -4) AS INTEGER) = ?
        LEFT JOIN Productos p ON t.COD_PRODUCTO = p.COD_PRODUCTO
        WHERE pl.COD_CAMPO = ?
            AND pl.EJERCICIO = ?
            AND pl.MES = ?
        GROUP BY
            pl.MACRO_P,
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
            pp.COD_PROD,
            p.NOM_PRODUCTO,
            pp.CANTIDAD AS OBJETIVO,
            COALESCE(SUM(t.CANTIDAD), 0) AS CUMPLIMIENTO
        FROM Productos_plan pp
        JOIN Productos p ON p.COD_PRODUCTO = pp.COD_PROD
        LEFT JOIN Tratamientos t ON t.COD_CAMPO = pp.COD_CAMPO
            AND t.COD_PRODUCTO = pp.COD_PROD
            AND CAST(SUBSTR(t.FECHA, 4, 2) AS INTEGER) = ?
            AND CAST(SUBSTR(t.FECHA, -4) AS INTEGER) = ?
        WHERE pp.COD_CAMPO = ?
            AND pp.EJERCICIO = ?
            AND pp.MES = ?
        GROUP BY
            pp.COD_PROD,
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
