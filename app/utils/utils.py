
def obtener_mes_cierre(
    cursor,
    cod_campo,
):
    cursor.execute(
        """
        SELECT mes_cierre FROM explotaciones WHERE cod_campo = %s
    """,
        (cod_campo,),
    )

    row = cursor.fetchone()
    mes_cierre = row["mes_cierre"]
    if mes_cierre is None:
        raise ValueError(f"El campo {cod_campo} no tiene mes de cierre informado")

    return mes_cierre

def obtener_cierre_anual(
    cursor,
    cod_cliente,
):
    cursor.execute(
        """
        SELECT mes_cierre FROM explotaciones WHERE cod_cliente = %s AND ultimo_cierre = True
    """,
        (cod_cliente,),
    )

    row = cursor.fetchone()
    mes_cierre = row["mes_cierre"]
    if not row or row["mes_cierre"] is None:
        raise ValueError(f"El {cod_cliente} no tiene mes de cierre informado")

    return mes_cierre