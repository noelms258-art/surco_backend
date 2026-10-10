from app.db import get_db_connection
from datetime import date, datetime

from app.utils.utils import obtener_cierre_anual


def get_ingresos_totales_service(cod_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    mes_cierre = obtener_cierre_anual(cursor, cod_cliente)
    anio_inicio = datetime.now().year
    anio_fin = anio_inicio + 1

    params = (cod_cliente, anio_inicio, mes_cierre, anio_fin, mes_cierre)
    cursor.execute("SELECT SUM(i.total_bruto) AS total_bruto FROM ingresos_clientes AS i JOIN explotaciones AS t ON i.cod_campo = t.cod_campo WHERE t.cod_cliente = %s"
                   " AND ((EXTRACT(YEAR FROM i.fec_ingreso) = %s AND EXTRACT(MONTH FROM i.fec_ingreso) > %s) OR (EXTRACT(YEAR FROM i.fec_ingreso) = %s " 
                   " AND EXTRACT(MONTH FROM i.fec_ingreso) <= %s))",
                     params)

    row = cursor.fetchone()
    ingreso_total = row["total_bruto"] if row else 0
    return [
        {"ingresoTotal": ingreso_total}
    ]

def get_gastos_totales_service(cod_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    mes_cierre = obtener_cierre_anual(cursor, cod_cliente)
    anio_inicio = datetime.now().year
    anio_fin = anio_inicio + 1

    mes_inicio = mes_cierre + 1

    if mes_inicio == 13:
        mes_inicio = 1
        anio_inicio += 1

    fecha_inicio = date(anio_inicio, mes_inicio, 1)
    fecha_fin = date(fecha_inicio.year + 1, fecha_inicio.month, 1)

    paramsTer = (fecha_fin, fecha_fin, fecha_inicio, cod_cliente, fecha_fin, fecha_inicio)
    cursor.execute("select COALESCE(SUM((t.salario_anual / 365.0) * (LEAST(COALESCE(t.fecha_baja, %s::date), %s::date) - GREATEST( t.fecha_inicio, %s::date))), 0"
    ") AS salario_campana from Terceros t where t.cod_cliente = %s AND t.fecha_inicio < %s  AND (t.fecha_baja IS NULL OR t.fecha_baja >= %s )", paramsTer)
    row = cursor.fetchone()
    salarios = row["salario_campana"] or 0

    params = (cod_cliente,)
    cursor.execute("select COALESCE(sum((a.coste/NULLIF(a.vida_util, 0))), 0) AS activo_anual from activos_clientes a where a.cod_cliente  = %s"
    " AND CURRENT_DATE < (a.fec_compra + a.vida_util * INTERVAL '1 year')", params)
    row = cursor.fetchone()
    activos = row["activo_anual"] or 0

    params_prod = (cod_cliente, anio_inicio, mes_cierre, anio_fin,  mes_cierre)
    cursor.execute("select COALESCE(sum(imp_total_prod), 0) AS gastos_prod from gastos_productos where cod_cliente = %s AND " 
    " ((EXTRACT(YEAR FROM fec_compra) = %s AND EXTRACT(MONTH FROM fec_compra) > %s) OR (EXTRACT(YEAR FROM fec_compra) = %s " 
                   " AND EXTRACT(MONTH FROM fec_compra) <= %s))", params_prod)
    row_prod = cursor.fetchone()
    productos = row_prod["gastos_prod"] or 0

    cursor.close()
    conn.close()

    return [
        {"gastosTotales": salarios + activos + productos}
    ]


def get_grafica_culotivo_services(cod_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (cod_cliente, datetime.now().year)
    cursor. execute("select i.cod_fruta, sum(total_neto) AS total_ingresos from ingresos_cliente i, explotaciones t where t.cod_campo = i.cod_campo and t.cod_cliente = %s"
                    " AND EXTRACT(YEAR FROM i.fec_ingreso) = %s", params)

    return ""

def get_grafica_campos_servicio(cod_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()

    mes_cierre = obtener_cierre_anual(cursor, cod_cliente)
    anio_inicio = datetime.now().year
    anio_fin = anio_inicio + 1

    params = (cod_cliente, anio_inicio, mes_cierre, anio_fin, mes_cierre)
    resultado = {}

    cursor.execute(
        """
        SELECT i.cod_campo, t.nom_campo, SUM(i.total_neto) AS total_ingresos FROM ingresos_clientes i, explotaciones t WHERE t.cod_campo = i.cod_campo
          AND t.cod_cliente = %s AND ((EXTRACT(YEAR FROM i.fec_ingreso) = %s AND EXTRACT(MONTH FROM i.fec_ingreso) > %s ) OR 
          (EXTRACT(YEAR FROM i.fec_ingreso) = %s AND EXTRACT(MONTH FROM i.fec_ingreso) <= %s )) GROUP BY i.cod_campo, t.nom_campo
        """,
        params
    )

    for row in cursor.fetchall():

        cod_campo = row["cod_campo"]
        nom_campo = row["nom_campo"] or ""
        ingresos = row["total_ingresos"] or 0

        paramsTar = (cod_cliente, cod_campo, anio_inicio, mes_cierre, anio_fin, mes_cierre)

        cursor.execute(
            """
            SELECT COALESCE( SUM( (CAST(te.salario_anual AS REAL) / NULLIF(te.horario_mes, 0)) * ta.horas ), 0 ) AS gastos_ter
            FROM Terceros te, Gastos_Tareas ta WHERE te.cod_cliente = ta.cod_cliente AND te.cod_cliente = %s AND ta.cod_campo = %s 
            AND ((EXTRACT(YEAR FROM ta.fec_tarea) = %s AND EXTRACT(MONTH FROM ta.fec_tarea) > %s ) OR
            (EXTRACT(YEAR FROM ta.fec_tarea) = %s AND EXTRACT(MONTH FROM ta.fec_tarea) <= %s ))
            """,
            paramsTar
        )

        row_salarios = cursor.fetchone()
        salarios = row_salarios["gastos_ter"] if row_salarios else 0

        paramsActivos = (
            anio_inicio, mes_cierre, anio_fin, mes_cierre, cod_cliente, anio_inicio, mes_cierre, anio_fin, mes_cierre, cod_campo
        )

        cursor.execute(
            """
            SELECT COALESCE( SUM( (CAST(a.coste AS REAL) / NULLIF(a.vida_util, 0)) * ( CAST(ta.horas AS REAL) /
             NULLIF(( SELECT SUM(gt.horas) FROM Gastos_Tareas gt  WHERE gt.cod_activo = ta.cod_activo AND gt.cod_cliente = ta.cod_cliente
             AND AND ((EXTRACT(YEAR FROM gt.fec_tarea) = %s AND EXTRACT(MONTH FROM gt.fec_tarea) > %s ) OR
             (EXTRACT(YEAR FROM gt.fec_tarea) = %s AND EXTRACT(MONTH FROM gt.fec_tarea) <= %s ) ) ), 0 ))), 0 ) AS gasto_activo 
             FROM activos_clientes a, Gastos_Tareas ta WHERE a.cod_cliente = ta.cod_cliente AND a.cod_activo = ta.cod_activo AND a.cod_cliente = %s 
             AND ((EXTRACT(YEAR FROM ta.fec_tarea) = %s AND EXTRACT(MONTH FROM ta.fec_tarea) > %s ) OR
             (EXTRACT(YEAR FROM ta.fec_tarea) = %s AND EXTRACT(MONTH FROM ta.fec_tarea) <= %s )) AND ta.cod_campo = %s
            """,
            paramsActivos
        )

        row_activos = cursor.fetchone()
        activos = row_activos["gasto_activo"] if row_activos else 0

        paramsProd = ( cod_cliente, cod_campo, anio_inicio, mes_cierre, anio_fin, mes_cierre)

        cursor.execute(
            """
            SELECT t.cod_campo, SUM(t.cant_trata * gp.imp_ud_prod) AS gasto_productos FROM tratamientos t JOIN gastos_productos gp
            ON gp.cod_gasto_prod = t.cod_gasto WHERE t.cod_cliente = %s AND t.cod_campo = %s AND 
            ((EXTRACT(YEAR FROM t.fec_trata) = %s AND EXTRACT(MONTH FROM t.fec_trata) > %s ) OR 
            (EXTRACT(YEAR FROM t.fec_trata) = %s AND EXTRACT(MONTH FROM t.fec_trata) <= %s ))
            """,
            paramsProd
        )
        
        row_activos = cursor.fetchone()
        productos = row_activos["gasto_productos"] if row_activos else 0

        resultado[cod_campo] = {
            "cod_campo": cod_campo,
            "nom_campo": nom_campo,
            "ingresos": ingresos,
            "gastos": salarios + activos + productos
        }

    cursor.close()
    conn.close()

    return resultado