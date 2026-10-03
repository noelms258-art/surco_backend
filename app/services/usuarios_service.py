from app.db import get_db_connection
from datetime import datetime

def get_campos_by_user(cod_cliente):
    conn = get_db_connection()
    params = (datetime.now().year, cod_cliente)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT t.COD_CAMPO, t.NOM_CAMPO, t.superficie, sum(ec.NUM_ARBOLES) as num_arboles, STRING_AGG(f.nom_fruta, ' - ' ORDER BY f.nom_fruta) AS nom_fruta,
            CASE 
            WHEN EXISTS (
                SELECT 1
                FROM Plan_abonado pl
                WHERE pl.cod_campo = t.cod_campo
              AND pl.ejercicio = %s
            ) THEN 1
            ELSE 0
            END AS TIENE_PLAN, t.mes_cierre
            FROM explotaciones t, cultivo f, explotaciones_cultivos ec
            WHERE f.cod_fruta = ec.cod_fruta and t.cod_campo = ec.cod_campo and t.cod_cliente = %s
            GROUP BY t.cod_campo, t.nom_campo, t.superficie
            """,
            (params),
        )
        rows = cursor.fetchall()

        return [
            {"codCampo": row["cod_campo"], "nomCampo": row["nom_campo"], "tamaño": row["superficie"],
            "numArboles": row["num_arboles"], "nomFruta": row["nom_fruta"], "tienePlan": row["tiene_plan"], "mesCierre": row["mes_cierre"]} for row in rows
        ]
    finally:
        conn.close()


def get_empleados_by_user(cod_cliente):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                t.COD_TERCERO,
                (
                    SELECT us.NOM_CLIENTE || ' ' || us.APE_CLIENTE
                    FROM Usuarios us
                    WHERE t.COD_TERCERO = us.cod_cliente
                ) AS NOM_CLIENTE
            FROM Terceros t, Usuarios u WHERE u.cod_cliente = %s
            """,
            (cod_cliente,),
        )
        rows = cursor.fetchall()

        return [
            {"codTercero": row["cod_tercero"], "nomTercero": row["nom_cliente"]}
            for row in rows
        ]
    finally:
        conn.close()
