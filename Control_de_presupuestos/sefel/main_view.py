import tkinter as tk
from tkinter import ttk

from .styles import (
    COLOR_PRINCIPAL,
    COLOR_FONDO,
    COLOR_BLANCO,
    COLOR_TEXTO,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_LINEA,
    FUENTE_TITULO,
    FUENTE_NORMAL,
    FUENTE_NORMAL_NEGRITA,
    FUENTE_ENTRADA
)

from .obra_form import ObraForm

from .database import (
    obtener_obras,
    obtener_total_presupuesto_obra,
    obtener_total_gastos_obra
)


class MainView:

    def __init__(self,ventana,usuario="Administración",rol="administrador"):
        self.ventana = ventana
        self.usuario = usuario
        self.rol = rol

        self.limpiar_ventana()
        self.crear_interfaz()

    def limpiar_ventana(self):
        for widget in self.ventana.winfo_children():
            widget.destroy()

    def crear_interfaz(self):
        self.crear_barra_superior()
        self.crear_cuerpo()

    def crear_barra_superior(self):
        barra_superior = tk.Frame(
            self.ventana,
            bg=COLOR_PRINCIPAL,
            height=55
        )

        barra_superior.pack(fill="x")
        barra_superior.pack_propagate(False)

        titulo = tk.Label(
            barra_superior,
            text="SEFEL | Control de presupuestos y gastos",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            font=("Arial", 13, "bold")
        )

        titulo.pack(
            side="left",
            padx=25
        )

        texto_app = tk.Label(
            barra_superior,
            text="Aplicación de escritorio",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            font=("Arial", 9)
        )

        texto_app.pack(
            side="right",
            padx=25
        )

    def crear_cuerpo(self):
        cuerpo = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )

        cuerpo.pack(
            fill="both",
            expand=True
        )

        self.crear_menu_lateral(cuerpo)
        self.crear_contenido_principal(cuerpo)

    def crear_menu_lateral(self, cuerpo):

        menu = tk.Frame(
            cuerpo,
            bg=COLOR_BLANCO,
            width=170
        )

        menu.pack(
            side="left",
            fill="y"
        )

        menu.pack_propagate(False)

        titulo_menu = tk.Label(
            menu,
            text="MENÚ PRINCIPAL",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Arial", 8, "bold")
        )

        titulo_menu.pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )


        # Define los módulos disponibles en el menú lateral.
        # Administración y Gerencia pueden acceder a las
        # mismas pantallas, pero cada módulo restringe sus
        # operaciones según el rol del usuario.
        #
        # Recursos permite acceder al catálogo centralizado
        # de materiales, mano de obra, equipos y herramientas.

        opciones = [
            ("Obras", None),
            ("Recursos", self.ir_recursos),
            ("Partidas", self.ir_partidas),
            ("Presupuestos", self.ir_presupuestos),
            ("Gastos", self.ir_gastos),
            ("Comparar costos", self.ir_comparacion)
        ]


        for texto, comando in opciones:

            bg = "#F8E5E5" if texto == "Obras" else COLOR_BLANCO

            fuente = (
                FUENTE_NORMAL_NEGRITA
                if texto == "Obras"
                else FUENTE_NORMAL
            )

            boton = tk.Button(
                menu,
                text=texto,
                command=comando,
                bg=bg,
                fg=COLOR_TEXTO,
                activebackground="#F8E5E5",
                relief="flat",
                anchor="w",
                font=fuente,
                padx=20,
                pady=8
            )

            boton.pack(
                fill="x"
            )

        espacio = tk.Frame(
            menu,
            bg=COLOR_BLANCO
        )

        espacio.pack(
            fill="both",
            expand=True
        )

        linea = tk.Frame(
            menu,
            bg=COLOR_LINEA,
            height=1
        )

        linea.pack(
            fill="x",
            padx=15
        )

        usuario = tk.Label(
            menu,
            text=f"Usuario: {self.usuario}",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Arial", 8)
        )

        usuario.pack(
            anchor="w",
            padx=20,
            pady=(10, 5)
        )

        # Botón que permite finalizar la sesión actual
        # desde la pantalla principal de Obras.
        #
        # Utilizamos tk.Button para mantener el mismo
        # diseño y funcionamiento que en los demás módulos.

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

    def crear_contenido_principal(self, cuerpo):
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

        titulo = tk.Label(
            contenido,
            text="PANTALLA PRINCIPAL · OBRAS",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            font=FUENTE_TITULO
        )

        titulo.pack(
            anchor="w"
        )

        linea = tk.Frame(
            contenido,
            bg=COLOR_LINEA,
            height=2
        )

        linea.pack(
            fill="x",
            pady=(8, 8)
        )

        subtitulo = tk.Label(
            contenido,
            text="Listado de obras registradas",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=FUENTE_NORMAL
        )

        subtitulo.pack(
            anchor="w",
            pady=(0, 20)
        )

        self.crear_panel_obras(contenido)

    def crear_panel_obras(self, contenido):
        panel = tk.Frame(
            contenido,
            bg=COLOR_BLANCO,
            bd=1,
            relief="solid",
            padx=20,
            pady=20
        )

        panel.pack(
            fill="both",
            expand=True
        )

        label_buscar = tk.Label(
            panel,
            text="Buscar obra",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        )

        label_buscar.pack(
            anchor="w"
        )

        fila_busqueda = tk.Frame(
            panel,
            bg=COLOR_BLANCO
        )

        fila_busqueda.pack(
            fill="x",
            pady=(5, 20)
        )

        self.entrada_busqueda = tk.Entry(
            fila_busqueda,
            font=FUENTE_ENTRADA
        )

        self.entrada_busqueda.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=5
        )

        self.entrada_busqueda.bind(
            "<KeyRelease>",
            self.filtrar_obras
        )

        boton_nueva_obra = tk.Button(
            fila_busqueda,
            text="+ Nueva obra",
            command=self.abrir_nueva_obra,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            activebackground=COLOR_PRINCIPAL,
            activeforeground=COLOR_BLANCO,
            font=FUENTE_NORMAL_NEGRITA,
            cursor="hand2",
            width=15
        )

        if self.rol != "gerencia":
            boton_nueva_obra.pack(
                side="right",
                padx=(20, 0),
                ipady=5
            )

        columnas = (
            "obra",
            "presupuesto",
            "gastos",
            "accion"
        )

        self.tabla = ttk.Treeview(
            panel,
            columns=columnas,
            show="headings",
            height=12
        )

        self.tabla.heading(
            "obra",
            text="Obra"
        )

        self.tabla.heading(
            "presupuesto",
            text="Presupuesto inicial"
        )

        self.tabla.heading(
            "gastos",
            text="Gastos registrados"
        )

        self.tabla.heading(
            "accion",
            text="Acción"
        )

        self.tabla.column(
            "obra",
            width=220
        )

        self.tabla.column(
            "presupuesto",
            width=180,
            anchor="center"
        )

        self.tabla.column(
            "gastos",
            width=180,
            anchor="center"
        )

        self.tabla.column(
            "accion",
            width=120,
            anchor="center"
        )

        self.tabla.pack(
            fill="both",
            expand=True
        )

        # Doble clic sobre una obra para ver sus costos
        self.tabla.bind(
            "<Double-1>",
            self.ver_costos
        )

        mensaje = tk.Label(
            panel,
            text="Seleccione una obra y haga doble clic para consultar sus costos.",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Arial", 9)
        )

        mensaje.pack(
            anchor="w",
            pady=(10, 0)
        )

        self.cargar_obras()

    def abrir_nueva_obra(self):
        ObraForm(
            self.ventana,
            self.usuario,
            self.cargar_obras
        )

    def cargar_obras(self, filtro=""):

        for registro in self.tabla.get_children():
            self.tabla.delete(registro)

        obras = obtener_obras()

        filtro = filtro.lower().strip()

        for obra in obras:

            obra_id = obra[0]
            nombre = obra[1]

            if filtro == "" or filtro in nombre.lower():

                presupuesto = obtener_total_presupuesto_obra(
                    obra_id
                )

                gastos = obtener_total_gastos_obra(
                    obra_id
                )

                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        nombre,
                        f"$ {presupuesto:,.0f}",
                        f"$ {gastos:,.0f}",
                        "Ver costos"
                    )
                )

    def filtrar_obras(self, event=None):

        texto_busqueda = self.entrada_busqueda.get()

        self.cargar_obras(texto_busqueda)

    def ver_costos(self, event=None):

        seleccion = self.tabla.selection()

        if not seleccion:
            return

        item = self.tabla.item(
            seleccion[0]
        )

        valores = item["values"]

        if not valores:
            return

        nombre_obra = valores[0]

        from .compare_view import CompareView

        CompareView(
            self.ventana,
            self.usuario,
            rol=self.rol,
            obra_seleccionada=nombre_obra
        )


    def ir_recursos(self):
        """
        Abre la pantalla del maestro de recursos.

        Permite acceder al catálogo desde el menú lateral,
        conservando la sesión y los permisos del usuario.
        """

        # Importamos ResourcesView dentro de la función
        # para evitar dependencias circulares entre módulos.

        from .resources_view import ResourcesView

        # Enviamos la ventana actual para reutilizarla
        # sin abrir una nueva instancia de la aplicación.
        #
        # self.usuario conserva la identidad del usuario.
        # self.rol conserva sus permisos de acceso.
        # Esto evita que Gerencia obtenga permisos de
        # administrador al cambiar de pantalla.

        ResourcesView(
            self.ventana,
            self.usuario,
            self.rol
        )
    def ir_partidas(self):

        # Importamos la pantalla del maestro de partidas
        # dentro de la función para evitar importaciones
        # circulares entre los diferentes módulos.

        from .partidas_view import PartidasView

        # Abrimos el maestro de partidas conservando
        # la ventana principal, el usuario y su rol.
        # Esto evita que Gerencia obtenga permisos
        # de administrador durante la navegación.

        PartidasView(
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

    # ==================================================
    # CIERRE DE SESIÓN
    # ==================================================

    def cerrar_sesion(self):

        # Importamos la pantalla de inicio de sesión
        # dentro de la función para evitar dependencias
        # circulares entre los módulos.

        from .login import LoginView

        # Elimina los componentes gráficos de la pantalla
        # principal sin cerrar la aplicación ni eliminar
        # los datos almacenados en la base de datos.

        self.limpiar_ventana()

        # Regresa a la pantalla de inicio de sesión
        # para permitir el ingreso de otro usuario.

        LoginView(self.ventana)