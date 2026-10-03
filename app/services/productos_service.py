from app.db import get_db_connection
from datetime import datetime


def get_productos_by_tipo(clas_prod):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT COD_PRODUCTO, NOM_PRODUCTO FROM Productos"
        params = []

        if clas_prod != "none":
            query += " WHERE sub_tip_producto like %s"
            params.append(f"{clas_prod}%")

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {"codProd": row["cod_producto"], "nomProd": row["nom_producto"]}
            for row in rows
        ]
    finally:
        conn.close()


def get_clases_producto():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sub_tip_producto FROM Productos")
        rows = cursor.fetchall()

        return [{"clasProd": row["sub_tip_producto"]} for row in rows]
    finally:
        conn.close()


def get_producto_user_service(cod_cliente):
    conn = get_db_connection()
    params = (cod_cliente, datetime.now().year,)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT gp.COD_PRODUCTO, p.NOM_PRODUCTO, sum(gp.unidades_prod) as unidades  FROM gastos_productos gp, Productos p WHERE gp.cod_producto = p.cod_producto "
            "AND gp.cod_cliente = %s AND p.sub_tip_producto = 'ABONO - FERTILIZANTE'  AND EXTRACT(YEAR FROM gp.fec_compra) = %s GROUP BY gp.COD_PRODUCTO, p.nom_producto HAVING SUM(gp.unidades_prod) >= 1"
        , params)
        rows = cursor.fetchall()

        return [{"nomProd": row["nom_producto"], "codProd": row["cod_producto"], "cantidad": row["unidades"]} for row in rows]
    finally:
        conn.close()
