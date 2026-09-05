from app.db import get_db_connection
from datetime import datetime


def get_ingresos_totales_service(user_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (user_name, datetime.now().year)
    cursor.execute("SELECT SUM(i.total_bruto) FROM Ingresos AS i JOIN Terrenos AS t ON i.cod_campo = t.cod_campo WHERE t.cod_cliente IN ( SELECT cod_cliente " +
    " FROM Usuarios WHERE email = ?) AND CAST(substr(i.fecha, -4) AS INTEGER) = ?", params)

    row = cursor.fetchone()
    ingreso_total = row[0] if row else 0
    return [
        {"ingresoTotal": ingreso_total}
    ]

def get_gastos_totales_service(user_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (user_name,)
    cursor.execute("select sum(t.salario) from Terceros t where t.cod_cliente IN ( SELECT cod_cliente FROM Usuarios WHERE email = ?)", params)
    row = cursor.fetchone()
    salarios = row[0] if row else 0

    cursor.execute("select sum((a.coste_activo/a.vida_util)) from Activos a where a.cod_cliente IN ( SELECT cod_cliente FROM Usuarios WHERE email = ?)", params)
    row = cursor.fetchone()
    activos = row[0] if row else 0

    return [
        {"gastosTotales": salarios + activos }
    ]


def get_grafica_culotivo_services(user_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (user_name, datetime.now().year)
    cursor. execute("select i.cod_fruta, sum(total_neto) AS total_ingresos from Ingresos i, Terrenos t where t.cod_campo = i.cod_campo and t.cod_cliente" \
    " IN ( SELECT cod_cliente FROM Usuarios WHERE email = ?) AND CAST(substr(i.fecha, -4) AS INTEGER) = ?", params)

    

    return ""

def get_grafica_campos_servicio(user_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (user_name, datetime.now().year)
    resultado = {}
    cursor. execute("select i.cod_campo, t.nom_campo, sum(total_neto) AS total_ingresos from Ingresos i, Terrenos t where t.cod_campo = i.cod_campo and t.cod_cliente" \
        " IN ( SELECT cod_cliente FROM Usuarios WHERE email = ?) AND CAST(substr(i.fecha, -4) AS INTEGER) = ? GROUP BY i.cod_campo, t.nom_campo", params)

    for row in cursor.fetchall():
        cod_campo = row[0]
        nom_campo = row[1] or 0
        ingresos = row[2] or 0

        paramsTar = (user_name, datetime.now().year, cod_campo)
        cursor.execute("select (CAST(te.salario AS REAL) / te.horario) * ta.horas AS gastos_ter from Terceros te, Gastos_Tareas ta where te.cod_cliente = ta.cod_cliente " +
                       "AND  te.cod_cliente IN ( SELECT cod_cliente FROM Usuarios WHERE email = ?) "
                       "AND CAST(substr(ta.fecha, -4) AS INTEGER) = ?  AND ta.cod_campo = ?", paramsTar)
        row = cursor.fetchone()
        salarios = row[0] if row else 0

        paramsActivos = (datetime.now().year, user_name, datetime.now().year, cod_campo)
        cursor.execute("select (CAST(a.coste_activo AS REAL) / a.vida_util) * (CAST(ta.horas AS REAL) /  (SELECT SUM(gt.horas) FROM Gastos_Tareas gt WHERE gt.cod_activo = ta.cod_activo "
                        "AND gt.cod_cliente = ta.cod_cliente AND CAST(SUBSTR(gt.fecha, -4) AS INTEGER) = ?)) AS gasto_activo "
                        "from Activos a, Gastos_Tareas ta where a.cod_cliente = ta.cod_cliente and a.cod_activo = ta.cod_activo "
                        "and  a.cod_cliente IN ( SELECT cod_cliente FROM Usuarios WHERE email = ?) AND CAST(substr(ta.fecha, -4) AS INTEGER) = ? AND ta.cod_campo = ?", paramsActivos)
        row = cursor.fetchone()
        activos = row[0] if row else 0


        resultado[cod_campo] = {
            "cod_campo": cod_campo,
            "nom_campo": nom_campo,
            "ingresos": ingresos,
            "gastos": salarios + activos
        }
    
    
    
    return resultado