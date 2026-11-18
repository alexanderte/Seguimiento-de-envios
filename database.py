
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "envios.db"


def get_connection():
    INSTANCE_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS envios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_seguimiento TEXT UNIQUE NOT NULL,
                destinatario TEXT NOT NULL,
                direccion TEXT NOT NULL,
                descripcion TEXT,
                estado_actual TEXT NOT NULL,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS historial_estados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                envio_id INTEGER NOT NULL,
                estado TEXT NOT NULL,
                observacion TEXT,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (envio_id) REFERENCES envios(id)
            )
        """)

        connection.commit()

    finally:
        connection.close()


def get_user_by_username(username):
    connection = get_connection()

    try:
        return connection.execute(
            "SELECT * FROM usuarios WHERE username = ?",
            (username,)
        ).fetchone()
    finally:
        connection.close()


def create_user(username, password_hash):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO usuarios (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash)
        )
        connection.commit()
    finally:
        connection.close()


def create_shipment(codigo, destinatario, direccion, descripcion):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Registrar el envío
        cursor.execute("""
            INSERT INTO envios (
                codigo_seguimiento,
                destinatario,
                direccion,
                descripcion,
                estado_actual
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            codigo,
            destinatario,
            direccion,
            descripcion,
            "Pendiente"
        ))

        envio_id = cursor.lastrowid

        # Registrar el estado inicial en el historial
        cursor.execute("""
            INSERT INTO historial_estados (
                envio_id,
                estado,
                observacion
            )
            VALUES (?, ?, ?)
        """, (
            envio_id,
            "Pendiente",
            "Envío registrado en el sistema"
        ))

        connection.commit()

        return True

    except sqlite3.IntegrityError:
        connection.rollback()
        return False

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_all_shipments():
    connection = get_connection()

    try:
        return connection.execute("""
            SELECT *
            FROM envios
            ORDER BY fecha_registro DESC
        """).fetchall()

    finally:
        connection.close()


def get_shipment_by_code(codigo):
    connection = get_connection()

    try:
        return connection.execute("""
            SELECT *
            FROM envios
            WHERE codigo_seguimiento = ?
        """, (codigo,)).fetchone()

    finally:
        connection.close()


def get_shipment_history(envio_id):
    connection = get_connection()

    try:
        return connection.execute("""
            SELECT *
            FROM historial_estados
            WHERE envio_id = ?
            ORDER BY fecha_actualizacion DESC, id DESC
        """, (envio_id,)).fetchall()

    finally:
        connection.close()

def update_shipment_status(envio_id, nuevo_estado, observacion):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE envios
            SET estado_actual = ?
            WHERE id = ?
        """, (nuevo_estado, envio_id))

        if cursor.rowcount == 0:
            connection.rollback()
            return False

        cursor.execute("""
            INSERT INTO historial_estados (
                envio_id,
                estado,
                observacion
            ) VALUES (?, ?, ?)
        """, (envio_id, nuevo_estado, observacion))

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()