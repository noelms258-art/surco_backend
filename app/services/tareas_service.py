from app.db import get_db_connection


def get_tareas_service():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select COD_TAREA, NOM_TAREA, activo from Tareas")
    rows = cursor.fetchall()

    return [
        {
            "codTarea": row["cod_tarea"],
            "nomTarea": row["nom_tarea"],
            "usaActivo": row["activo"],
        }
        for row in rows
    ]


def insert_tareas_service(data, cod_cliente):
    tareas = data.get("tareas", [])
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
                INSERT INTO gastos_tareas
                (cod_tarea, cod_campo, cod_cliente, horas, fec_tarea, cod_activo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
    try:
        params = []
        for tarea in tareas:
            if tarea.get("codTarea") is None:
                raise ValueError("Cada compra debe llevar una tarea")
    
            params.append(
                (
                    tarea.get("codTarea"),
                    tarea.get("codCampo"),
                    cod_cliente,
                    float(tarea.get("txtHoras")),
                    tarea.get("fechaTarea"),
                    tarea.get("codActivo")
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
