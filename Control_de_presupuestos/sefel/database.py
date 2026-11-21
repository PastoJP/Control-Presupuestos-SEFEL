import sqlite3
import os
import hashlib
import secrets
import hmac


def obtener_ruta_base_datos():
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sefel.db"
    )


def base_datos_existe():
    ruta = obtener_ruta_base_datos()
    return os.path.exists(ruta)


def obtener_conexion():
    ruta = obtener_ruta_base_datos()

    if not os.path.exists(ruta):
        raise FileNotFoundError(
            "No se encontró la base de datos sefel.db."
        )

    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


# SEGURIDAD DE USUARIOS

def generar_hash_contrasena(contrasena, salt=None):
    """
    Genera un hash seguro utilizando PBKDF2-HMAC-SHA256.
    Retorna el salt y el hash en formato hexadecimal.
    """

    if salt is None:
        salt = secrets.token_bytes(16)

    hash_contrasena = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        salt,
        200000
    )

    return salt.hex(), hash_contrasena.hex()


def verificar_hash_contrasena(contrasena, salt_hex, hash_guardado):
    """
    Comprueba una contraseña ingresada contra el hash
    almacenado en la base de datos.
    """

    salt = bytes.fromhex(salt_hex)

    _, hash_generado = generar_hash_contrasena(
        contrasena,
        salt
    )

    return hmac.compare_digest(
        hash_generado,
        hash_guardado
    )


def crear_usuario(usuario, contrasena):
    """
    Crea un usuario almacenando únicamente el salt y
    el hash de la contraseña.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    salt, hash_contrasena = generar_hash_contrasena(
        contrasena
    )

    try:
        cursor.execute(
            """
            INSERT INTO usuarios (
                usuario,
                password_hash,
                salt
            )
            VALUES (?, ?, ?)
            """,
            (
                usuario,
                hash_contrasena,
                salt
            )
        )

        conexion.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conexion.close()


def verificar_usuario(usuario, contrasena):
    """
    Verifica que el usuario exista y que la contraseña
    coincida con el hash almacenado.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT password_hash, salt
        FROM usuarios
        WHERE usuario = ?
        """,
        (usuario,)
    )

    resultado = cursor.fetchone()

    conexion.close()

    if resultado is None:
        return False

    hash_guardado, salt = resultado

    return verificar_hash_contrasena(
        contrasena,
        salt,
        hash_guardado
    )


def crear_usuario_administrador():
    """
    Crea el usuario administrador inicial solamente
    si todavía no existe.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id
        FROM usuarios
        WHERE usuario = ?
        """,
        ("admin",)
    )

    usuario_existente = cursor.fetchone()

    conexion.close()

    if usuario_existente is None:
        crear_usuario(
            "admin",
            "123"
        )


# CREACIÓN DE BASE DE DATOS

def crear_base_datos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS obras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            obra_id INTEGER NOT NULL,
            partida TEXT NOT NULL,
            monto REAL NOT NULL,
            FOREIGN KEY (obra_id) REFERENCES obras(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            obra_id INTEGER NOT NULL,
            partida TEXT NOT NULL,
            concepto TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (obra_id) REFERENCES obras(id)
        )
    """)

    conexion.commit()
    conexion.close()

    crear_usuario_administrador()


# OBRAS

def agregar_obra(nombre, descripcion):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO obras (nombre, descripcion)
        VALUES (?, ?)
        """,
        (nombre, descripcion)
    )

    conexion.commit()
    conexion.close()


def obtener_obras():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id, nombre, descripcion
        FROM obras
        ORDER BY id DESC
        """
    )

    obras = cursor.fetchall()

    conexion.close()
    return obras


# PRESUPUESTOS

def agregar_presupuesto(obra_id, partida, monto):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO presupuestos (obra_id, partida, monto)
        VALUES (?, ?, ?)
        """,
        (obra_id, partida, monto)
    )

    conexion.commit()
    conexion.close()


def obtener_presupuestos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            presupuestos.id,
            obras.nombre,
            presupuestos.partida,
            presupuestos.monto
        FROM presupuestos
        INNER JOIN obras
            ON presupuestos.obra_id = obras.id
        ORDER BY presupuestos.id DESC
        """
    )

    presupuestos = cursor.fetchall()

    conexion.close()
    return presupuestos


def obtener_total_presupuesto_obra(obra_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT COALESCE(SUM(monto), 0)
        FROM presupuestos
        WHERE obra_id = ?
        """,
        (obra_id,)
    )

    total = cursor.fetchone()[0]

    conexion.close()
    return total


# GASTOS

def agregar_gasto(obra_id, partida, concepto, monto, fecha):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO gastos (
            obra_id,
            partida,
            concepto,
            monto,
            fecha
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            obra_id,
            partida,
            concepto,
            monto,
            fecha
        )
    )

    conexion.commit()
    conexion.close()


def obtener_gastos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            gastos.id,
            obras.nombre,
            gastos.partida,
            gastos.concepto,
            gastos.monto,
            gastos.fecha
        FROM gastos
        INNER JOIN obras
            ON gastos.obra_id = obras.id
        ORDER BY gastos.id DESC
        """
    )

    gastos = cursor.fetchall()

    conexion.close()
    return gastos


def obtener_total_gastos_obra(obra_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT COALESCE(SUM(monto), 0)
        FROM gastos
        WHERE obra_id = ?
        """,
        (obra_id,)
    )

    total = cursor.fetchone()[0]

    conexion.close()
    return total


# COMPARACIÓN DE COSTOS

def obtener_resumen_costos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            obras.id,
            obras.nombre,

            COALESCE(
                (
                    SELECT SUM(p.monto)
                    FROM presupuestos p
                    WHERE p.obra_id = obras.id
                ),
                0
            ) AS presupuesto,

            COALESCE(
                (
                    SELECT SUM(g.monto)
                    FROM gastos g
                    WHERE g.obra_id = obras.id
                ),
                0
            ) AS gastos

        FROM obras

        ORDER BY obras.id DESC
    """)

    datos = cursor.fetchall()

    conexion.close()
    return datos

def obtener_resumen_partidas_obra(obra_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            partidas.partida,

            COALESCE(
                (
                    SELECT SUM(p.monto)
                    FROM presupuestos p
                    WHERE p.obra_id = ?
                    AND p.partida = partidas.partida
                ),
                0
            ) AS presupuesto,

            COALESCE(
                (
                    SELECT SUM(g.monto)
                    FROM gastos g
                    WHERE g.obra_id = ?
                    AND g.partida = partidas.partida
                ),
                0
            ) AS gastos

        FROM (
            SELECT partida
            FROM presupuestos
            WHERE obra_id = ?

            UNION

            SELECT partida
            FROM gastos
            WHERE obra_id = ?
        ) AS partidas

        ORDER BY partidas.partida
        """,
        (
            obra_id,
            obra_id,
            obra_id,
            obra_id
        )
    )

    datos = cursor.fetchall()

    conexion.close()
    return datos