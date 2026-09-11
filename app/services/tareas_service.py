from app.db import get_db_connection


def get_tareas_service():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select COD_TAREA, NOM_TAREA from Tareas")
    rows = cursor.fetchall()

    return [
        {"codTarea": row["cod_tarea"], "nomTarea": row["nom_tarea"]} for row in rows
    ]
