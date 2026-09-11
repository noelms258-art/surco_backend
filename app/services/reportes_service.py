from app.db import get_db_connection
from datetime import datetime


def get_ingresos_totales_service(cod_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (cod_cliente, datetime.now().year)
    cursor.execute("SELECT SUM(i.total_bruto) FROM ingresos_clientes AS i JOIN explotaciones AS t ON i.cod_campo = t.cod_campo WHERE t.cod_cliente = %s"
                   " AND CAST(substr(i.fec_ingreso, -4) AS INTEGER) = %s", params)

    row = cursor.fetchone()
    ingreso_total = row[0] if row else 0
    return [
        {"ingresoTotal": ingreso_total}
    ]

def get_gastos_totales_service(cod_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (cod_cliente,)
    cursor.execute("select sum(t.salario_anual) from Terceros t where t.cod_cliente = %s", params)
    row = cursor.fetchone()
    salarios = row[0] if row else 0

    cursor.execute("select sum((a.coste/a.vida_util)) from Activos a where a.cod_cliente  = %s", params)
    row = cursor.fetchone()
    activos = row[0] if row else 0

    return [
        {"gastosTotales": salarios + activos }
    ]


def get_grafica_culotivo_services(cod_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (cod_cliente, datetime.now().year)
    cursor. execute("select i.cod_fruta, sum(total_neto) AS total_ingresos from ingresos_cliente i, explotaciones t where t.cod_campo = i.cod_campo and t.cod_cliente = %s"
                    " AND CAST(substr(i.fecha, -4) AS INTEGER) = %s", params)

    return ""

def get_grafica_campos_servicio(cod_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (cod_cliente, datetime.now().year)
    resultado = {}

    cursor. execute("select i.cod_campo, t.nom_campo, sum(total_neto) AS total_ingresos from ingresos_clientes i, explotaciones t where t.cod_campo = i.cod_campo and t.cod_cliente" \
        " = %s AND CAST(substr(i.fec_ingreso, -4) AS INTEGER) = %s GROUP BY i.cod_campo, t.nom_campo", params)

    for row in cursor.fetchall():
        cod_campo = row[0]
        nom_campo = row[1] or 0
        ingresos = row[2] or 0

        paramsTar = (cod_cliente, datetime.now().year, cod_campo)
        cursor.execute("select (CAST(te.salario_anual AS REAL) / te.horario_mes) * ta.horas AS gastos_ter from Terceros te, Gastos_Tareas ta where te.cod_cliente = ta.cod_cliente " +
                       "AND  te.cod_cliente = %s AND CAST(substr(ta.fec_tarea, -4) AS INTEGER) = %s  AND ta.cod_campo = %s", paramsTar)
        row = cursor.fetchone()
        salarios = row[0] if row else 0

        paramsActivos = (datetime.now().year, cod_cliente, datetime.now().year, cod_campo)
        cursor.execute("select (CAST(a.coste AS REAL) / a.vida_util) * (CAST(ta.horas AS REAL) /  (SELECT SUM(gt.horas) FROM Gastos_Tareas gt WHERE gt.cod_activo = ta.cod_activo "
                        "AND gt.cod_cliente = ta.cod_cliente AND CAST(SUBSTR(gt.fec_tarea, -4) AS INTEGER) = %s)) AS gasto_activo "
                        "from activos_clientes a, Gastos_Tareas ta where a.cod_cliente = ta.cod_cliente and a.cod_activo = ta.cod_activo "
                        "and  a.cod_cliente = %s AND CAST(substr(ta.fec_tarea, -4) AS INTEGER) = %s AND ta.cod_campo = %s", paramsActivos)
        row = cursor.fetchone()
        activos = row[0] if row else 0


        resultado[cod_campo] = {
            "cod_campo": cod_campo,
            "nom_campo": nom_campo,
            "ingresos": ingresos,
            "gastos": salarios + activos
        }
    
    
    
    return resultado