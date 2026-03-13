import sqlite3


def crear_bd():
    conn = sqlite3.connect("directorio.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS directorio (
        expediente INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        telefono TEXT NOT NULL,
        telefono2 TEXT
    )
    """)

    # Migración: agrega telefono2 si la tabla ya existía sin esa columna
    try:
        cursor.execute("ALTER TABLE directorio ADD COLUMN telefono2 TEXT")
    except Exception:
        pass

    conn.commit()
    conn.close()


def agregar_persona(expediente, nombre, telefono, telefono2=""):
    conn = sqlite3.connect("directorio.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO directorio VALUES (?, ?, ?, ?)",
            (expediente, nombre, telefono, telefono2)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def ver_directorio():
    conn = sqlite3.connect("directorio.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM directorio")
    datos = cursor.fetchall()

    conn.close()
    return datos


def actualizar_persona(expediente, nombre, telefono, telefono2=""):
    conn = sqlite3.connect("directorio.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE directorio
        SET nombre = ?, telefono = ?, telefono2 = ?
        WHERE expediente = ?
    """, (nombre, telefono, telefono2, expediente))

    conn.commit()
    conn.close()


def borrar_persona(expediente):
    conn = sqlite3.connect("directorio.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM directorio WHERE expediente = ?",
        (expediente,)
    )

    conn.commit()
    conn.close()


def buscar_personas(query):
    conn = sqlite3.connect("directorio.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM directorio
        WHERE CAST(expediente AS TEXT) LIKE ? OR nombre LIKE ?
    """, (f"%{query}%", f"%{query}%"))
    datos = cursor.fetchall()

    conn.close()
    return datos
