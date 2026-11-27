
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Importamos los colores y fuentes corporativas.
# Esto permite mantener el mismo diseño visual
# utilizado en los demás módulos de SEFEL.

from .styles import (
    COLOR_PRINCIPAL,
    COLOR_PRINCIPAL_ACTIVO,
    COLOR_FONDO,
    COLOR_BLANCO,
    COLOR_TEXTO,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_LINEA,
    COLOR_SELECCION,
    FUENTE_TITULO,
    FUENTE_NORMAL,
    FUENTE_NORMAL_NEGRITA,
    FUENTE_ENTRADA
)

# Importamos las funciones del maestro de partidas.
# Estas permiten consultar y modificar la información
# de SQLite sin escribir instrucciones SQL en la interfaz.

from .database import (
    agregar_partida,
    obtener_partidas,
    actualizar_partida,
    desactivar_partida,
    activar_partida,
    buscar_partidas
)


class PartidasView:

    # ==================================================
    # INICIALIZACIÓN DE LA PANTALLA
    # ==================================================

    def __init__(self, ventana, usuario, rol):

        # Conservamos los datos de la sesión actual.
        # El rol es obligatorio para mantener los permisos
        # originales del usuario durante la navegación.

        self.ventana = ventana
        self.usuario = usuario
        self.rol = rol

        # Diccionario que almacena temporalmente las partidas
        # consultadas, utilizando su ID como identificador.
        # Facilita recuperar los datos de la fila seleccionada.

        self.partidas = {}

        self.limpiar()
        self.crear_interfaz()

    def limpiar(self):

        # Elimina los elementos gráficos de la pantalla
        # anterior sin cerrar la aplicación ni borrar datos.

        for widget in self.ventana.winfo_children():
            widget.destroy()

    def crear_interfaz(self):

        # Divide la interfaz en tres secciones:
        # barra superior, menú lateral y contenido principal.

        self.crear_barra_superior()

        cuerpo = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )

        cuerpo.pack(fill="both", expand=True)

        self.crear_menu(cuerpo)
        self.crear_contenido(cuerpo)

    # ==================================================
    # BARRA SUPERIOR
    # ==================================================

    def crear_barra_superior(self):

        # Crea el encabezado corporativo de SEFEL.
        # Conserva el diseño de las pantallas anteriores.

        barra = tk.Frame(
            self.ventana,
            bg=COLOR_PRINCIPAL,
            height=55
        )

        barra.pack(fill="x")
        barra.pack_propagate(False)

        tk.Label(
            barra,
            text="SEFEL | Control de presupuestos y gastos",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=25)

        tk.Label(
            barra,
            text="Aplicación de escritorio",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            font=("Arial", 9)
        ).pack(side="right", padx=25)

    # ==================================================
    # MENÚ LATERAL
    # ==================================================

    def crear_menu(self, cuerpo):

        # Permite navegar entre los diferentes módulos
        # sin necesidad de volver a iniciar sesión.

        menu = tk.Frame(
            cuerpo,
            bg=COLOR_BLANCO,
            width=170
        )

        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)

        tk.Label(
            menu,
            text="MENÚ PRINCIPAL",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Arial", 8, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        # Cada opción contiene el nombre del módulo
        # y la función encargada de abrir su pantalla.
        # Partidas utiliza None porque ya está abierto.

        opciones = [
            ("Obras", self.ir_obras),
            ("Recursos", self.ir_recursos),
            ("Partidas", None),
            ("Presupuestos", self.ir_presupuestos),
            ("Gastos", self.ir_gastos),
            ("Comparar costos", self.ir_comparacion)
        ]

        for texto, comando in opciones:

            # Resalta visualmente el módulo seleccionado.

            seleccionado = texto == "Partidas"

            tk.Button(
                menu,
                text=texto,
                command=comando,
                bg=COLOR_SELECCION if seleccionado else COLOR_BLANCO,
                fg=COLOR_TEXTO,
                activebackground=COLOR_SELECCION,
                relief="flat",
                anchor="w",
                padx=20,
                pady=8,
                font=FUENTE_NORMAL_NEGRITA if seleccionado else FUENTE_NORMAL
            ).pack(fill="x")

        # Mantiene los datos del usuario y el botón
        # de cierre de sesión al final del menú.

        tk.Frame(
            menu,
            bg=COLOR_BLANCO
        ).pack(fill="both", expand=True)

        tk.Frame(
            menu,
            bg=COLOR_LINEA,
            height=1
        ).pack(fill="x", padx=15)

        tk.Label(
            menu,
            text=f"Usuario: {self.usuario}",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Arial", 8)
        ).pack(
            anchor="w",
            padx=20,
            pady=(10, 5)
        )

        tk.Button(
            menu,
            text="Cerrar sesión",
            command=self.cerrar_sesion,
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            relief="flat",
            font=("Arial", 8, "bold"),
            cursor="hand2"
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 20)
        )

    # ==================================================
    # CONTENIDO PRINCIPAL
    # ==================================================

    def crear_contenido(self, cuerpo):

        # Contenedor principal que reúne el título,
        # buscador, botones de gestión y tabla de partidas.

        contenido = tk.Frame(
            cuerpo,
            bg=COLOR_FONDO
        )

        contenido.pack(
            side="left",
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        tk.Label(
            contenido,
            text="MAESTRO DE PARTIDAS",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            font=FUENTE_TITULO
        ).pack(anchor="w")

        tk.Frame(
            contenido,
            bg=COLOR_LINEA,
            height=2
        ).pack(fill="x", pady=(8, 8))

        tk.Label(
            contenido,
            text="Catálogo de actividades constructivas",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=FUENTE_NORMAL
        ).pack(anchor="w", pady=(0, 15))

        # Informa cuando el usuario no dispone
        # de permisos para modificar información.

        if self.rol != "administrador":

            tk.Label(
                contenido,
                text="Modo consulta - Gerencia",
                bg=COLOR_FONDO,
                fg=COLOR_TEXTO_SECUNDARIO,
                font=FUENTE_NORMAL_NEGRITA
            ).pack(anchor="w", pady=(0, 10))

        panel = tk.Frame(
            contenido,
            bg=COLOR_BLANCO,
            bd=1,
            relief="solid",
            padx=15,
            pady=15
        )

        panel.pack(fill="both", expand=True)

        self.crear_buscador(panel)

        # Los botones de gestión solamente se muestran
        # cuando el usuario pertenece a Administración.

        if self.rol == "administrador":
            self.crear_botones(panel)

        self.crear_tabla(panel)
        self.cargar_partidas()

    # ==================================================
    # BUSCADOR DE PARTIDAS
    # ==================================================

    def crear_buscador(self, panel):

        tk.Label(
            panel,
            text="Buscar por código, nombre o descripción",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        ).pack(anchor="w")

        self.entrada_busqueda = tk.Entry(
            panel,
            font=FUENTE_ENTRADA
        )

        self.entrada_busqueda.pack(
            fill="x",
            ipady=5,
            pady=(5, 15)
        )

        # KeyRelease actualiza los resultados cada vez
        # que el usuario escribe o elimina un carácter.

        self.entrada_busqueda.bind(
            "<KeyRelease>",
            self.filtrar_partidas
        )

    def filtrar_partidas(self, event=None):

        # Actualiza la tabla utilizando el texto
        # ingresado en el campo de búsqueda.

        self.cargar_partidas()

    # ==================================================
    # BOTONES DE ADMINISTRACIÓN
    # ==================================================

    def crear_botones(self, panel):

        fila = tk.Frame(
            panel,
            bg=COLOR_BLANCO
        )

        fila.pack(fill="x", pady=(0, 15))

        # Cada botón está asociado a una función
        # que realiza una operación sobre las partidas.

        botones = [
            ("+ Nueva partida", self.nueva_partida),
            ("Editar", self.editar_partida),
            ("Desactivar", self.desactivar),
            ("Activar", self.activar)
        ]

        for texto, comando in botones:

            tk.Button(
                fila,
                text=texto,
                command=comando,
                bg=COLOR_PRINCIPAL,
                fg=COLOR_BLANCO,
                activebackground=COLOR_PRINCIPAL_ACTIVO,
                activeforeground=COLOR_BLANCO,
                font=FUENTE_NORMAL_NEGRITA,
                cursor="hand2",
                padx=10,
                pady=5
            ).pack(side="left", padx=(0, 8))

    # ==================================================
    # TABLA DE PARTIDAS
    # ==================================================

    def crear_tabla(self, panel):

        # Treeview permite mostrar los registros
        # de SQLite mediante filas y columnas.

        contenedor = tk.Frame(
            panel,
            bg=COLOR_BLANCO
        )

        contenedor.pack(fill="both", expand=True)

        columnas = (
            "codigo",
            "nombre",
            "descripcion",
            "unidad",
            "estado"
        )

        self.tabla = ttk.Treeview(
            contenedor,
            columns=columnas,
            show="headings",
            selectmode="browse"
        )

        # Define el título visible y el ancho
        # inicial de cada columna de la tabla.

        encabezados = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 180),
            ("descripcion", "Descripción", 220),
            ("unidad", "Unidad", 75),
            ("estado", "Estado", 75)
        ]

        for columna, titulo, ancho in encabezados:

            self.tabla.heading(
                columna,
                text=titulo
            )

            self.tabla.column(
                columna,
                width=ancho,
                minwidth=60,
                anchor="center"
            )

        # Las barras de desplazamiento permiten consultar
        # los registros cuando la ventana es pequeña
        # o cuando existen muchas partidas almacenadas.

        barra_vertical = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=self.tabla.yview
        )

        barra_horizontal = ttk.Scrollbar(
            contenedor,
            orient="horizontal",
            command=self.tabla.xview
        )

        self.tabla.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set
        )

        barra_vertical.pack(side="right", fill="y")
        barra_horizontal.pack(side="bottom", fill="x")

        self.tabla.pack(fill="both", expand=True)

        # Las partidas inactivas se muestran en gris
        # para distinguirlas de las partidas activas.

        self.tabla.tag_configure(
            "inactivo",
            foreground=COLOR_TEXTO_SECUNDARIO,
            background="#EEEEEE"
        )

        # Etiqueta que indica la cantidad de partidas
        # que se encuentran visibles en la tabla.

        self.etiqueta_total = tk.Label(
            panel,
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=FUENTE_NORMAL
        )

        self.etiqueta_total.pack(
            anchor="w",
            pady=(10, 0)
        )

    def cargar_partidas(self):

        # Obtiene el texto ingresado en el buscador.
        # strip elimina espacios innecesarios.

        texto = self.entrada_busqueda.get().strip()

        try:

            # Si existe texto, busca coincidencias.
            # De lo contrario, consulta todas las partidas.

            if texto:
                datos = buscar_partidas(texto)
            else:
                datos = obtener_partidas()

        except sqlite3.Error:

            messagebox.showerror(
                "Partidas",
                "No fue posible consultar las partidas."
            )

            return

        # Limpia las filas visibles después de realizar
        # correctamente la consulta a SQLite.
        # Esto no elimina registros de la base de datos.

        for registro in self.tabla.get_children():
            self.tabla.delete(registro)

        self.partidas.clear()

        for partida in datos:

            # Desempaqueta los seis campos recuperados
            # desde la tabla partidas de SQLite.

            partida_id, codigo, nombre, descripcion, unidad, activo = partida

            # Conserva los datos utilizando su ID real.

            self.partidas[partida_id] = partida

            estado = "Activo" if activo == 1 else "Inactivo"

            # iid permite relacionar cada fila visible
            # con el identificador real de SQLite.
            # Así se modifica únicamente la partida elegida.

            self.tabla.insert(
                "",
                "end",
                iid=str(partida_id),
                values=(
                    codigo,
                    nombre,
                    descripcion,
                    unidad,
                    estado
                ),
                tags=("inactivo",) if activo == 0 else ()
            )

        self.etiqueta_total.config(
            text=f"Partidas mostradas: {len(datos)}"
        )

    # ==================================================
    # VALIDACIÓN DE PERMISOS Y SELECCIÓN
    # ==================================================

    def verificar_permiso(self):

        # Además de ocultar los botones de gestión,
        # comprueba el rol antes de modificar información.
        # Solo Administración puede gestionar partidas.

        if self.rol != "administrador":

            messagebox.showwarning(
                "Acceso restringido",
                "No tiene permisos para modificar partidas."
            )

            return False

        return True

    def obtener_seleccion(self):

        # Comprueba que el usuario haya seleccionado
        # una partida antes de editarla o desactivarla.

        seleccion = self.tabla.selection()

        if not seleccion:

            messagebox.showwarning(
                "Partidas",
                "Debe seleccionar una partida de la tabla."
            )

            return None

        partida_id = int(seleccion[0])

        return self.partidas.get(partida_id)

    # ==================================================
    # REGISTRO Y EDICIÓN DE PARTIDAS
    # ==================================================

    def nueva_partida(self):

        # Abre un formulario vacío para registrar
        # una nueva actividad constructiva.

        if self.verificar_permiso():
            self.abrir_formulario()

    def editar_partida(self):

        # Recupera los datos de la partida seleccionada
        # y los carga en el formulario de edición.

        if not self.verificar_permiso():
            return

        partida = self.obtener_seleccion()

        if partida is not None:
            self.abrir_formulario(partida)

    def abrir_formulario(self, partida=None):

        # Toplevel crea una ventana secundaria.
        # El mismo formulario permite registrar y editar,
        # evitando duplicar el código de ambas operaciones.

        formulario = tk.Toplevel(self.ventana)

        formulario.title(
            "Editar partida" if partida else "Nueva partida"
        )

        formulario.geometry("430x390")
        formulario.resizable(False, False)
        formulario.configure(bg=COLOR_BLANCO)

        # transient vincula el formulario con la ventana
        # principal y grab_set evita interactuar con otros
        # módulos mientras el formulario está abierto.

        formulario.transient(self.ventana)
        formulario.grab_set()

        campos = {}

        # Define los campos que podrá ingresar el usuario.
        # La descripción es opcional, mientras que código,
        # nombre y unidad de medida son obligatorios.

        nombres = [
            ("codigo", "Código"),
            ("nombre", "Nombre"),
            ("descripcion", "Descripción (opcional)"),
            ("unidad", "Unidad de medida")
        ]

        for clave, titulo in nombres:

            tk.Label(
                formulario,
                text=titulo,
                bg=COLOR_BLANCO,
                fg=COLOR_TEXTO,
                font=FUENTE_NORMAL_NEGRITA
            ).pack(
                anchor="w",
                padx=25,
                pady=(10, 2)
            )

            entrada = tk.Entry(
                formulario,
                font=FUENTE_ENTRADA
            )

            entrada.pack(
                fill="x",
                padx=25,
                ipady=3
            )

            campos[clave] = entrada

        # Si estamos editando una partida, recuperamos
        # sus datos para mostrarlos en el formulario.

        if partida:

            campos["codigo"].insert(0, partida[1])
            campos["nombre"].insert(0, partida[2])
            campos["descripcion"].insert(0, partida[3])
            campos["unidad"].insert(0, partida[4])

        tk.Label(
            formulario,
            text="Ejemplos de unidad: m2, m3, ml, unidad.",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Arial", 9)
        ).pack(anchor="w", padx=25, pady=5)

        # Esta función interna recupera y valida los datos
        # antes de enviarlos a la base de datos SQLite.

        def guardar():

            if not self.verificar_permiso():
                return

            # upper convierte el código a mayúsculas
            # para mantener un formato uniforme.
            # strip elimina espacios al inicio y al final.

            codigo = campos["codigo"].get().strip().upper()
            nombre = campos["nombre"].get().strip()
            descripcion = campos["descripcion"].get().strip()
            unidad = campos["unidad"].get().strip()

            # Comprueba los campos obligatorios.
            # La descripción no se incluye porque
            # puede quedar vacía de manera intencional.

            if not all((codigo, nombre, unidad)):

                messagebox.showerror(
                    "Datos incompletos",
                    "Debe completar el código, nombre "
                    "y unidad de medida.",
                    parent=formulario
                )

                return

            try:

                # Si existe una partida seleccionada,
                # modifica sus datos mediante su ID.
                # De lo contrario, registra una nueva.

                if partida:

                    resultado = actualizar_partida(
                        partida[0],
                        codigo,
                        nombre,
                        descripcion,
                        unidad
                    )

                else:

                    resultado = agregar_partida(
                        codigo,
                        nombre,
                        descripcion,
                        unidad
                    )

            except sqlite3.Error:

                # Controla errores relacionados con SQLite
                # evitando que la aplicación se cierre.

                messagebox.showerror(
                    "Error de base de datos",
                    "No fue posible guardar la partida.",
                    parent=formulario
                )

                return

            # False indica que la operación no se realizó.
            # Puede deberse a un código duplicado,
            # un registro inexistente o datos inválidos.

            if not resultado:

                messagebox.showerror(
                    "No se pudo guardar",
                    "Verifique que el código no esté duplicado "
                    "y que los datos sean válidos.",
                    parent=formulario
                )

                return

            messagebox.showinfo(
                "Partidas",
                "La partida se guardó correctamente.",
                parent=formulario
            )

            # Cierra el formulario y actualiza la tabla
            # para mostrar los cambios realizados.

            formulario.destroy()
            self.cargar_partidas()

        tk.Button(
            formulario,
            text="Guardar partida",
            command=guardar,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            activebackground=COLOR_PRINCIPAL_ACTIVO,
            activeforeground=COLOR_BLANCO,
            font=FUENTE_NORMAL_NEGRITA,
            cursor="hand2"
        ).pack(
            fill="x",
            padx=25,
            pady=15,
            ipady=5
        )

    # ==================================================
    # ACTIVACIÓN Y DESACTIVACIÓN
    # ==================================================

    def desactivar(self):

        # Solicita cambiar el estado de la partida a 0,
        # lo que representa una partida inactiva.

        self.cambiar_estado(0)

    def activar(self):

        # Solicita cambiar el estado de la partida a 1,
        # lo que representa una partida activa.

        self.cambiar_estado(1)

    def cambiar_estado(self, nuevo_estado):

        # Centraliza ambas operaciones para evitar
        # repetir las mismas validaciones y mensajes.

        if not self.verificar_permiso():
            return

        partida = self.obtener_seleccion()

        if partida is None:
            return

        partida_id = partida[0]
        nombre = partida[2]
        estado_actual = partida[5]

        # Evita modificar una partida que ya posee
        # el estado solicitado por el usuario.

        if estado_actual == nuevo_estado:

            messagebox.showinfo(
                "Partidas",
                "La partida ya se encuentra en ese estado."
            )

            return

        accion = "activar" if nuevo_estado == 1 else "desactivar"

        # Solicita confirmación antes de modificar
        # la disponibilidad de una partida constructiva.

        confirmar = messagebox.askyesno(
            "Confirmar operación",
            f"¿Desea {accion} la partida {nombre}?"
        )

        if not confirmar:
            return

        try:

            # Ejecuta la función correspondiente.
            # No elimina registros permanentemente,
            # conservando su información para futuros APU.

            if nuevo_estado == 1:
                resultado = activar_partida(partida_id)
            else:
                resultado = desactivar_partida(partida_id)

        except sqlite3.Error:

            messagebox.showerror(
                "Partidas",
                "No fue posible modificar el estado."
            )

            return

        if resultado:

            self.cargar_partidas()

            messagebox.showinfo(
                "Partidas",
                "Estado actualizado correctamente."
            )

        else:

            messagebox.showerror(
                "Partidas",
                "No fue posible actualizar la partida."
            )

    # ==================================================
    # NAVEGACIÓN ENTRE MÓDULOS
    # ==================================================

    # Las importaciones se realizan dentro de cada función
    # para evitar importaciones circulares entre pantallas.
    # Se conserva siempre el usuario y su rol original.

    def ir_obras(self):

        from .main_view import MainView

        MainView(
            self.ventana,
            self.usuario,
            self.rol
        )

    def ir_recursos(self):

        from .resources_view import ResourcesView

        ResourcesView(
            self.ventana,
            self.usuario,
            self.rol
        )

    def ir_presupuestos(self):

        from .budget_view import BudgetView

        BudgetView(
            self.ventana,
            self.usuario,
            self.rol
        )

    def ir_gastos(self):

        from .expenses_view import ExpensesView

        ExpensesView(
            self.ventana,
            self.usuario,
            self.rol
        )

    def ir_comparacion(self):

        from .compare_view import CompareView

        CompareView(
            self.ventana,
            self.usuario,
            rol=self.rol
        )

    def cerrar_sesion(self):

        # Elimina la interfaz actual y devuelve al usuario
        # a la pantalla de inicio de sesión.

        from .login import LoginView

        self.limpiar()

        LoginView(self.ventana)
