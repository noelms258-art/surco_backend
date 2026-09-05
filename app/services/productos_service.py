from app.db import get_db_connection


def get_productos_by_tipo(clas_prod):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT COD_PRODUCTO, NOM_PRODUCTO FROM Productos"
        params = []

        if clas_prod != "none":
            query += " WHERE tipo = ?"
            params.append(clas_prod)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {"codProd": row["COD_PRODUCTO"], "nomProd": row["NOM_PRODUCTO"]}
            for row in rows
        ]
    finally:
        conn.close()


def get_clases_producto():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT TIPO FROM Productos")
        rows = cursor.fetchall()

        return [{"clasProd": row["TIPO"]} for row in rows]
    finally:
        conn.close()


def get_producto_user_service(cod_cliente):
    conn = get_db_connection()
    params = (cod_cliente,)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT p.NOM_PRODUCTO, p.COD_PRODUCTO, gp.CANTIDAD  FROM Gastos_Producto gp, Productos p WHERE gp.cod_producto = p.cod_producto "
            "AND gp.COD_EMPLEADO = ? AND gp.CANTIDAD >= 1 GROUP BY gp.COD_PRODUCTO, p.NOM_PRODUCTO"
        , params)
        rows = cursor.fetchall()

        return [{"nomProd": row["NOM_PRODUCTO"], "codProd": row["COD_PRODUCTO"], "cantidad": row["CANTIDAD"]} for row in rows]
    finally:
        conn.close()
