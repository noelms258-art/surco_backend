from app.db import get_db_connection

try:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT current_database(), current_user
    """)

    resultado = cursor.fetchone()

    print("Conexión correcta")
    print(resultado)

    cursor.close()
    conn.close()

except Exception as e:
    print("Error de conexión")
    print(e)