
import tkinter as tk
from tkinter import ttk, messagebox
import math
import sqlite3

# Importamos los colores y fuentes corporativas.
# Esto permite mantener el mismo diseño en todas las
# pantallas sin definir nuevamente los colores.

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

# Importamos las funciones que desarrollamos anteriormente.
# Estas permiten que la interfaz interactúe con SQLite
# sin tener que ejecutar instrucciones SQL directamente.

from .database import (
    agregar_recurso,
    obtener_recursos,
    actualizar_recurso,
    desactivar_recurso,
    activar_recurso,
    buscar_recursos
)


class ResourcesView:

    # ==================================================
    # INICIALIZACIÓN DE LA PANTALLA
    # ==================================================

    def __init__(self, ventana, usuario, rol):

        # Conservamos la ventana, el usuario y su rol.
        # El rol es obligatorio para evitar que Gerencia
        # obtenga permisos de administrador al navegar.

        self.ventana = ventana
        self.usuario = usuario
        self.rol = rol

        # Diccionario que almacena temporalmente los recursos
        # consultados, utilizando su ID como identificador.

        self.recursos = {}

        # Categorías permitidas por la base de datos.

        self.categorias = (
            "Material",
            "Mano de obra",
            "Equipo",
            "Herramienta"
        )

        self.limpiar()
        self.crear_interfaz()

    def limpiar(self):

        # Elimina los elementos gráficos de la pantalla
        # anterior, sin cerrar la aplicación ni borrar datos.

        for widget in self.ventana.winfo_children():
            widget.destroy()

    def crear_interfaz(self):

        # Organiza la pantalla en tres secciones:
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
        # Se mantiene el diseño de las pantallas existentes.

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

        # El menú permite desplazarse entre los módulos
        # sin cerrar la sesión del usuario.

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

        opciones = [
            ("Obras", self.ir_obras),
            ("Recursos", None),
            ("Presupuestos", self.ir_presupuestos),
            ("Gastos", self.ir_gastos),
            ("Comparar costos", self.ir_comparacion)
        ]

        for texto, comando in opciones:

            # Resalta Recursos porque corresponde
            # al módulo que se encuentra abierto.

            seleccionado = texto == "Recursos"

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

        # El espacio expandible mantiene los datos
        # del usuario en la parte inferior del menú.

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

        # Este contenedor reúne el título, buscador,
        # botones de gestión y tabla de recursos.

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
            text="MAESTRO DE RECURSOS",
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
            text="Catálogo de materiales, mano de obra, equipos y herramientas",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=FUENTE_NORMAL
        ).pack(anchor="w", pady=(0, 15))

        # Informa al usuario cuando solamente dispone
        # de permisos para consultar información.

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

        # Solo Administración puede visualizar los
        # botones que permiten modificar información.

        if self.rol == "administrador":
            self.crear_botones(panel)

        self.crear_tabla(panel)
        self.cargar_recursos()

    # ==================================================
    # BUSCADOR DE RECURSOS
    # ==================================================

    def crear_buscador(self, panel):

        tk.Label(
            panel,
            text="Buscar por código, nombre o categoría",
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

        # KeyRelease ejecuta la búsqueda cada vez que
        # el usuario escribe o elimina un carácter.
        # Esto permite filtrar la tabla automáticamente.

        self.entrada_busqueda.bind(
            "<KeyRelease>",
            self.filtrar_recursos
        )

    def filtrar_recursos(self, event=None):

        # Obtiene el texto ingresado y actualiza la tabla
        # mostrando únicamente los recursos coincidentes.

        self.cargar_recursos()

    # ==================================================
    # BOTONES DE ADMINISTRACIÓN
    # ==================================================

    def crear_botones(self, panel):

        fila = tk.Frame(
            panel,
            bg=COLOR_BLANCO
        )

        fila.pack(fill="x", pady=(0, 15))

        # Cada botón ejecuta una operación diferente
        # sobre los recursos almacenados.

        botones = [
            ("+ Nuevo recurso", self.nuevo_recurso),
            ("Editar", self.editar_recurso),
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
    # TABLA DE RECURSOS
    # ==================================================

    def crear_tabla(self, panel):

        # Treeview es un componente de Tkinter que
        # permite presentar información en filas y columnas.

        contenedor = tk.Frame(
            panel,
            bg=COLOR_BLANCO
        )

        contenedor.pack(fill="both", expand=True)

        columnas = (
            "codigo",
            "nombre",
            "categoria",
            "unidad",
            "precio",
            "estado"
        )

        self.tabla = ttk.Treeview(
            contenedor,
            columns=columnas,
            show="headings",
            selectmode="browse"
        )

        # Define el nombre visible y ancho de cada columna.

        encabezados = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 170),
            ("categoria", "Categoría", 110),
            ("unidad", "Unidad", 75),
            ("precio", "Precio unitario", 110),
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
        # todos los registros aunque la ventana sea pequeña.

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

        # Los recursos inactivos se muestran en gris
        # para diferenciarlos visualmente de los activos.

        self.tabla.tag_configure(
            "inactivo",
            foreground=COLOR_TEXTO_SECUNDARIO,
            background="#EEEEEE"
        )

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

    def cargar_recursos(self):

        # Elimina las filas visibles de la tabla.
        # Esto no elimina registros de SQLite.

        for registro in self.tabla.get_children():
            self.tabla.delete(registro)

        texto = self.entrada_busqueda.get().strip()

        try:

            # Si existe texto, consulta las coincidencias.
            # Si está vacío, obtiene el catálogo completo.

            if texto:
                datos = buscar_recursos(texto)
            else:
                datos = obtener_recursos()

        except sqlite3.Error:

            messagebox.showerror(
                "Recursos",
                "No fue posible consultar los recursos."
            )

            return

        self.recursos.clear()

        for recurso in datos:

            # Desempaqueta los siete campos recuperados
            # desde la tabla de recursos de SQLite.

            recurso_id, codigo, nombre, categoria, unidad, precio, activo = recurso

            self.recursos[recurso_id] = recurso

            estado = "Activo" if activo == 1 else "Inactivo"

            # Formatea el precio utilizando separadores
            # de miles y decimales habituales en Chile.

            precio_formato = f"{precio:,.2f}"
            precio_formato = precio_formato.translate(
                str.maketrans(",.", ".,")
            )

            # iid conserva el ID real de la base de datos.
            # Así podemos identificar correctamente el
            # recurso seleccionado al editarlo o desactivarlo.

            self.tabla.insert(
                "",
                "end",
                iid=str(recurso_id),
                values=(
                    codigo,
                    nombre,
                    categoria,
                    unidad,
                    f"$ {precio_formato}",
                    estado
                ),
                tags=("inactivo",) if activo == 0 else ()
            )

        self.etiqueta_total.config(
            text=f"Recursos mostrados: {len(datos)}"
        )

    # ==================================================
    # VALIDACIÓN DE PERMISOS Y SELECCIÓN
    # ==================================================

    def verificar_permiso(self):

        # Además de ocultar los botones, comprobamos
        # el rol antes de ejecutar cualquier modificación.
        # Solo Administración puede gestionar recursos.

        if self.rol != "administrador":

            messagebox.showwarning(
                "Acceso restringido",
                "No tiene permisos para modificar recursos."
            )

            return False

        return True

    def obtener_seleccion(self):

        # Comprueba que exista una fila seleccionada
        # antes de intentar editar o cambiar su estado.

        seleccion = self.tabla.selection()

        if not seleccion:

            messagebox.showwarning(
                "Recursos",
                "Debe seleccionar un recurso de la tabla."
            )

            return None

        recurso_id = int(seleccion[0])

        return self.recursos.get(recurso_id)

    # ==================================================
    # REGISTRO Y EDICIÓN DE RECURSOS
    # ==================================================

    def nuevo_recurso(self):

        # Abre un formulario vacío para registrar
        # un nuevo recurso en el catálogo.

        if self.verificar_permiso():
            self.abrir_formulario()

    def editar_recurso(self):

        # Recupera los datos del recurso seleccionado
        # y los carga en el formulario de edición.

        if not self.verificar_permiso():
            return

        recurso = self.obtener_seleccion()

        if recurso is not None:
            self.abrir_formulario(recurso)

    def abrir_formulario(self, recurso=None):

        # Toplevel crea una ventana secundaria sin cerrar
        # la pantalla principal de la aplicación.
        # El mismo formulario sirve para registrar y editar.

        formulario = tk.Toplevel(self.ventana)

        formulario.title(
            "Editar recurso" if recurso else "Nuevo recurso"
        )

        formulario.geometry("430x450")
        formulario.resizable(False, False)
        formulario.configure(bg=COLOR_BLANCO)

        # transient relaciona el formulario con la ventana
        # principal y grab_set evita interactuar con otras
        # pantallas mientras el formulario está abierto.

        formulario.transient(self.ventana)
        formulario.grab_set()

        campos = {}

        nombres = [
            ("codigo", "Código"),
            ("nombre", "Nombre"),
            ("categoria", "Categoría"),
            ("unidad", "Unidad de medida"),
            ("precio", "Precio unitario")
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

            if clave == "categoria":

                # readonly obliga a seleccionar una
                # categoría válida de la lista disponible.

                entrada = ttk.Combobox(
                    formulario,
                    values=self.categorias,
                    state="readonly",
                    font=FUENTE_ENTRADA
                )

            else:

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

        # Si estamos editando, carga la información
        # existente para que el usuario pueda modificarla.

        if recurso:

            campos["codigo"].insert(0, recurso[1])
            campos["nombre"].insert(0, recurso[2])
            campos["categoria"].set(recurso[3])
            campos["unidad"].insert(0, recurso[4])
            campos["precio"].insert(0, str(recurso[5]))

        else:
            campos["categoria"].current(0)

        tk.Label(
            formulario,
            text="Ingrese el precio sin separadores de miles.",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Arial", 9)
        ).pack(anchor="w", padx=25, pady=5)

        # Esta función interna obtiene y valida los datos
        # del formulario antes de enviarlos a SQLite.

        def guardar():

            if not self.verificar_permiso():
                return

            codigo = campos["codigo"].get().strip().upper()
            nombre = campos["nombre"].get().strip()
            categoria = campos["categoria"].get().strip()
            unidad = campos["unidad"].get().strip()
            precio_texto = campos["precio"].get().strip()

            # Evita registrar campos vacíos o que
            # contengan solamente espacios.

            if not all((
                codigo,
                nombre,
                categoria,
                unidad,
                precio_texto
            )):

                messagebox.showerror(
                    "Datos incompletos",
                    "Debe completar todos los campos.",
                    parent=formulario
                )

                return

            # Verifica que la categoría pertenezca
            # a las cuatro categorías permitidas.

            if categoria not in self.categorias:

                messagebox.showerror(
                    "Categoría inválida",
                    "Debe seleccionar una categoría válida.",
                    parent=formulario
                )

                return

            try:

                # Convierte el precio ingresado a un número.
                # Permite utilizar coma o punto decimal.

                precio = float(
                    precio_texto.replace(",", ".")
                )

            except ValueError:

                messagebox.showerror(
                    "Precio inválido",
                    "El precio debe ser un valor numérico.",
                    parent=formulario
                )

                return

            # isfinite rechaza valores especiales como
            # infinito y NaN, que no representan precios.
            # También se impide registrar valores negativos.

            if not math.isfinite(precio) or precio < 0:

                messagebox.showerror(
                    "Precio inválido",
                    "Debe ingresar un precio válido y no negativo.",
                    parent=formulario
                )

                return

            try:

                # Si existe un recurso seleccionado,
                # actualizamos sus datos mediante su ID.
                # De lo contrario, registramos uno nuevo.

                if recurso:

                    resultado = actualizar_recurso(
                        recurso[0],
                        codigo,
                        nombre,
                        categoria,
                        unidad,
                        precio
                    )

                else:

                    resultado = agregar_recurso(
                        codigo,
                        nombre,
                        categoria,
                        unidad,
                        precio
                    )

            except sqlite3.Error:

                messagebox.showerror(
                    "Error de base de datos",
                    "No fue posible guardar el recurso.",
                    parent=formulario
                )

                return

            # False indica que la operación no se realizó.
            # Puede ocurrir por un código duplicado u otra
            # restricción establecida en la base de datos.

            if not resultado:

                messagebox.showerror(
                    "No se pudo guardar",
                    "Verifique que el código no esté duplicado "
                    "y que los datos sean válidos.",
                    parent=formulario
                )

                return

            messagebox.showinfo(
                "Recursos",
                "El recurso se guardó correctamente.",
                parent=formulario
            )

            # Cierra el formulario y actualiza la tabla
            # para mostrar inmediatamente los cambios.

            formulario.destroy()
            self.cargar_recursos()

        tk.Button(
            formulario,
            text="Guardar recurso",
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

        # Solicita cambiar el estado del recurso a inactivo.

        self.cambiar_estado(0)

    def activar(self):

        # Solicita cambiar el estado del recurso a activo.

        self.cambiar_estado(1)

    def cambiar_estado(self, nuevo_estado):

        # Centraliza las operaciones de cambio de estado
        # para evitar repetir las mismas validaciones.

        if not self.verificar_permiso():
            return

        recurso = self.obtener_seleccion()

        if recurso is None:
            return

        recurso_id = recurso[0]
        nombre = recurso[2]
        estado_actual = recurso[6]

        # Evita realizar una operación innecesaria si
        # el recurso ya posee el estado solicitado.

        if estado_actual == nuevo_estado:

            messagebox.showinfo(
                "Recursos",
                "El recurso ya se encuentra en ese estado."
            )

            return

        accion = "activar" if nuevo_estado == 1 else "desactivar"

        # Solicita confirmación antes de modificar
        # la disponibilidad del recurso.

        confirmar = messagebox.askyesno(
            "Confirmar operación",
            f"¿Desea {accion} el recurso {nombre}?"
        )

        if not confirmar:
            return

        try:

            if nuevo_estado == 1:
                resultado = activar_recurso(recurso_id)
            else:
                resultado = desactivar_recurso(recurso_id)

        except sqlite3.Error:

            messagebox.showerror(
                "Recursos",
                "No fue posible modificar el estado."
            )

            return

        if resultado:

            self.cargar_recursos()

            messagebox.showinfo(
                "Recursos",
                "Estado actualizado correctamente."
            )

        else:

            messagebox.showerror(
                "Recursos",
                "No fue posible actualizar el recurso."
            )

    # ==================================================
    # NAVEGACIÓN ENTRE MÓDULOS
    # ==================================================

    # Las importaciones se realizan dentro de cada función
    # para evitar importaciones circulares entre pantallas.
    # Siempre se conserva el usuario y su rol original.

    def ir_obras(self):

        from .main_view import MainView

        MainView(
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
