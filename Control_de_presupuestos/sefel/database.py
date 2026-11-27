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


def crear_usuario(
    usuario,
    contrasena,
    rol="administrador"
):
    """
    Crea un usuario almacenando únicamente el salt,
    el hash de la contraseña y su rol.
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
                salt,
                rol
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                usuario,
                hash_contrasena,
                salt,
                rol
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

def obtener_rol_usuario(usuario):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT rol
        FROM usuarios
        WHERE usuario = ?
        """,
        (usuario,)
    )

    resultado = cursor.fetchone()

    conexion.close()

    if resultado:
        return resultado[0]

    return None

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

def crear_usuario_gerencia():
    """
    Crea el usuario de gerencia solamente
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
        ("gerencia",)
    )

    usuario_existente = cursor.fetchone()

    conexion.close()

    if usuario_existente is None:
        crear_usuario(
            "gerencia",
            "123",
            "gerencia"
        )

# CREACIÓN DE BASE DE DATOS

def crear_base_datos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'administrador'
        )
        """
    )

    cursor.execute(
        "PRAGMA table_info(usuarios)"
    )

    columnas_usuarios = [
        columna[1]
        for columna in cursor.fetchall()
    ]

    if "rol" not in columnas_usuarios:
        cursor.execute(
            """
            ALTER TABLE usuarios
            ADD COLUMN rol TEXT NOT NULL
            DEFAULT 'administrador'
            """
        )

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


    # MAESTRO DE RECURSOS
    # Crea una tabla en SQLite para almacenar los recursos
    # utilizados en la elaboración de APU y presupuestos.
    # IF NOT EXISTS evita volver a crear la tabla si ya existe,
    # conservando los registros almacenados anteriormente.

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE COLLATE NOCASE,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL CHECK (
                categoria IN (
                    'Material',
                    'Mano de obra',
                    'Equipo',
                    'Herramienta'
                )
            ),
            unidad TEXT NOT NULL,
            precio_unitario REAL NOT NULL CHECK (
                precio_unitario >= 0
            ),
            activo INTEGER NOT NULL DEFAULT 1 CHECK (
                activo IN (0, 1)
            )
        )
    """)

    # ======================================================
    # MAESTRO DE PARTIDAS
    # ======================================================

    # Crea una tabla para almacenar las actividades
    # constructivas que serán utilizadas en los APU
    # y en la elaboración de presupuestos.
    #
    # IF NOT EXISTS evita crear nuevamente la tabla
    # si ya existe, conservando los datos anteriores.

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE COLLATE NOCASE
                CHECK (length(trim(codigo)) > 0),
            nombre TEXT NOT NULL
                CHECK (length(trim(nombre)) > 0),
            descripcion TEXT NOT NULL DEFAULT '',
            unidad TEXT NOT NULL
                CHECK (length(trim(unidad)) > 0),
            activo INTEGER NOT NULL DEFAULT 1 CHECK (
                activo IN (0, 1)
            )
        )
    """)

    conexion.commit()
    conexion.close()

    crear_usuario_administrador()
    crear_usuario_gerencia()


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

def actualizar_gasto(
    gasto_id,
    obra_id,
    partida,
    concepto,
    monto,
    fecha
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE gastos
        SET
            obra_id = ?,
            partida = ?,
            concepto = ?,
            monto = ?,
            fecha = ?
        WHERE id = ?
        """,
        (
            obra_id,
            partida,
            concepto,
            monto,
            fecha,
            gasto_id
        )
    )

    conexion.commit()
    conexion.close()


# ==========================================================
# MAESTRO DE RECURSOS
# ==========================================================

# Estas funciones permiten administrar los recursos
# almacenados en la base de datos SQLite.
# Posteriormente serán utilizadas por la interfaz gráfica
# y por el módulo de Análisis de Precios Unitarios (APU).


def agregar_recurso(codigo, nombre, categoria, unidad, precio_unitario):
    """
    Registra un nuevo recurso en la base de datos.

    Recibe el código, nombre, categoría, unidad de medida
    y precio unitario ingresados por el usuario.
    El recurso queda activo de manera predeterminada.
    """

    # Abre una conexión con la base de datos existente.
    conexion = obtener_conexion()

    # El cursor permite ejecutar instrucciones SQL.
    cursor = conexion.cursor()

    try:
        # INSERT INTO permite agregar un nuevo registro.
        # Los signos de interrogación representan parámetros.
        # Evitan concatenar directamente los datos ingresados
        # por el usuario y ayudan a prevenir inyecciones SQL.

        cursor.execute("""
            INSERT INTO recursos (
                codigo,
                nombre,
                categoria,
                unidad,
                precio_unitario
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            codigo.strip(),
            nombre.strip(),
            categoria,
            unidad.strip(),
            precio_unitario
        ))

        # Guarda permanentemente los cambios realizados.
        conexion.commit()

        # Devuelve True para indicar un registro exitoso.
        return True

    except sqlite3.IntegrityError:

        # Captura errores relacionados con las restricciones
        # de la tabla, como códigos duplicados o precios negativos.
        conexion.rollback()
        return False

    finally:

        # Cierra la conexión aunque ocurra un error.
        conexion.close()


def obtener_recursos():
    """
    Consulta todos los recursos registrados, incluyendo
    aquellos que se encuentran activos e inactivos.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # SELECT permite consultar los campos de la tabla.
        # ORDER BY organiza los resultados por nombre.

        cursor.execute("""
            SELECT
                id,
                codigo,
                nombre,
                categoria,
                unidad,
                precio_unitario,
                activo
            FROM recursos
            ORDER BY nombre ASC
        """)

        # fetchall recupera todos los registros encontrados
        # y los devuelve como una lista de tuplas.
        return cursor.fetchall()

    finally:
        conexion.close()


def actualizar_recurso(
    recurso_id,
    codigo,
    nombre,
    categoria,
    unidad,
    precio_unitario
):
    """
    Modifica la información de un recurso existente.

    Utiliza el identificador interno del recurso para
    actualizar únicamente el registro seleccionado.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # UPDATE modifica los campos de un registro existente.
        # WHERE id = ? evita modificar todos los recursos
        # y limita el cambio al recurso seleccionado.

        cursor.execute("""
            UPDATE recursos
            SET
                codigo = ?,
                nombre = ?,
                categoria = ?,
                unidad = ?,
                precio_unitario = ?
            WHERE id = ?
        """, (
            codigo.strip(),
            nombre.strip(),
            categoria,
            unidad.strip(),
            precio_unitario,
            recurso_id
        ))

        conexion.commit()

        # rowcount indica cuántos registros fueron modificados.
        # Si no existe el recurso, devuelve False.
        return cursor.rowcount > 0

    except sqlite3.IntegrityError:
        conexion.rollback()
        return False

    finally:
        conexion.close()


def desactivar_recurso(recurso_id):
    """
    Cambia el estado de un recurso de activo a inactivo.

    No elimina el registro de la base de datos, permitiendo
    conservar su información y sus futuras relaciones
    con los APU y presupuestos.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # El valor 0 representa un recurso inactivo.
        # Se modifica únicamente el campo activo.

        cursor.execute("""
            UPDATE recursos
            SET activo = 0
            WHERE id = ?
        """, (recurso_id,))

        conexion.commit()

        return cursor.rowcount > 0

    finally:
        conexion.close()


def activar_recurso(recurso_id):
    """
    Permite volver a habilitar un recurso desactivado
    sin tener que registrarlo nuevamente.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # El valor 1 representa un recurso activo.

        cursor.execute("""
            UPDATE recursos
            SET activo = 1
            WHERE id = ?
        """, (recurso_id,))

        conexion.commit()

        return cursor.rowcount > 0

    finally:
        conexion.close()


def buscar_recursos(texto):
    """
    Busca recursos utilizando su código, nombre o categoría.

    Permite encontrar coincidencias parciales sin necesidad
    de escribir el nombre completo del recurso.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # strip elimina espacios innecesarios al inicio y al final.
    # El símbolo % permite buscar coincidencias parciales.
    # Por ejemplo, buscar "cem" puede encontrar "Cemento".

    busqueda = f"%{texto.strip()}%"

    try:
        # LIKE compara el texto ingresado con los datos
        # almacenados en los campos seleccionados.
        # OR permite encontrar coincidencias en cualquiera
        # de los tres campos consultados.

        cursor.execute("""
            SELECT
                id,
                codigo,
                nombre,
                categoria,
                unidad,
                precio_unitario,
                activo
            FROM recursos
            WHERE codigo LIKE ?
               OR nombre LIKE ?
               OR categoria LIKE ?
            ORDER BY nombre ASC
        """, (
            busqueda,
            busqueda,
            busqueda
        ))

        return cursor.fetchall()

    finally:
        conexion.close()

# ==========================================================
# MAESTRO DE PARTIDAS
# ==========================================================

# Estas funciones permiten administrar las actividades
# constructivas almacenadas en la base de datos.
# Posteriormente serán utilizadas por la interfaz gráfica,
# el módulo APU y la elaboración de presupuestos.


def agregar_partida(codigo, nombre, descripcion, unidad):
    """
    Registra una nueva partida constructiva.
    La partida queda activa de manera predeterminada.
    """

    # Abre la conexión con la base de datos SQLite.
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # INSERT INTO agrega un nuevo registro.
        # Los parámetros ? ayudan a prevenir inyecciones SQL
        # al separar los datos de las instrucciones SQL.
        cursor.execute("""
            INSERT INTO partidas (
                codigo,
                nombre,
                descripcion,
                unidad
            )
            VALUES (?, ?, ?, ?)
        """, (
            codigo.strip().upper(),
            nombre.strip(),
            descripcion.strip(),
            unidad.strip()
        ))

        # Guarda los cambios permanentemente.
        conexion.commit()

        return True

    except sqlite3.IntegrityError:

        # Controla errores de integridad, como códigos
        # duplicados o campos obligatorios vacíos.
        conexion.rollback()
        return False

    finally:

        # Cierra la conexión incluso si ocurre un error.
        conexion.close()


def obtener_partidas():
    """
    Consulta todas las partidas registradas,
    incluyendo las activas e inactivas.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # SELECT recupera los campos de la tabla.
        # ORDER BY organiza las partidas alfabéticamente.
        cursor.execute("""
            SELECT
                id,
                codigo,
                nombre,
                descripcion,
                unidad,
                activo
            FROM partidas
            ORDER BY nombre ASC
        """)

        # Devuelve los registros como una lista de tuplas.
        return cursor.fetchall()

    finally:
        conexion.close()


def actualizar_partida(
    partida_id,
    codigo,
    nombre,
    descripcion,
    unidad
):
    """
    Modifica los datos de una partida existente
    utilizando su identificador interno.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # UPDATE modifica la información almacenada.
        # WHERE id = ? limita la modificación a la
        # partida seleccionada por el usuario.
        cursor.execute("""
            UPDATE partidas
            SET
                codigo = ?,
                nombre = ?,
                descripcion = ?,
                unidad = ?
            WHERE id = ?
        """, (
            codigo.strip().upper(),
            nombre.strip(),
            descripcion.strip(),
            unidad.strip(),
            partida_id
        ))

        conexion.commit()

        # Comprueba que exista un registro afectado
        # por la operación de actualización.
        return cursor.rowcount > 0

    except sqlite3.IntegrityError:
        conexion.rollback()
        return False

    finally:
        conexion.close()


def desactivar_partida(partida_id):
    """
    Deshabilita una partida sin eliminarla
    permanentemente de la base de datos.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # El valor 0 representa una partida inactiva.
        # Se conserva el registro para mantener sus
        # futuras relaciones con APU y presupuestos.
        cursor.execute("""
            UPDATE partidas
            SET activo = 0
            WHERE id = ?
        """, (partida_id,))

        conexion.commit()

        return cursor.rowcount > 0

    finally:
        conexion.close()


def activar_partida(partida_id):
    """
    Reactiva una partida previamente deshabilitada,
    evitando tener que registrarla nuevamente.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # El valor 1 representa una partida activa.
        cursor.execute("""
            UPDATE partidas
            SET activo = 1
            WHERE id = ?
        """, (partida_id,))

        conexion.commit()

        return cursor.rowcount > 0

    finally:
        conexion.close()


def buscar_partidas(texto):
    """
    Busca partidas mediante su código, nombre
    o descripción.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # El símbolo % permite encontrar coincidencias
    # parciales sin escribir el nombre completo.
    busqueda = f"%{texto.strip()}%"

    try:
        # LIKE permite comparar el texto ingresado.
        # OR busca coincidencias en cualquiera de
        # los tres campos definidos.
        cursor.execute("""
            SELECT
                id,
                codigo,
                nombre,
                descripcion,
                unidad,
                activo
            FROM partidas
            WHERE codigo LIKE ?
               OR nombre LIKE ?
               OR descripcion LIKE ?
            ORDER BY nombre ASC
        """, (
            busqueda,
            busqueda,
            busqueda
        ))

        return cursor.fetchall()

    finally:
        conexion.close()
