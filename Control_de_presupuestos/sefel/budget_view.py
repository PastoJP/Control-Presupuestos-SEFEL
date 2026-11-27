import tkinter as tk
from tkinter import ttk, messagebox

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

from .database import (
    obtener_obras,
    agregar_presupuesto,
    obtener_presupuestos
)


class BudgetView:

    def __init__(self,ventana,usuario,rol="administrador"):
        self.ventana = ventana
        self.usuario = usuario
        self.rol = rol
        self.obras = []

        self.limpiar()
        self.crear_interfaz()

    def limpiar(self):
        for widget in self.ventana.winfo_children():
            widget.destroy()

    def crear_interfaz(self):
        self.crear_barra_superior()

        cuerpo = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )

        cuerpo.pack(
            fill="both",
            expand=True
        )

        self.crear_menu(cuerpo)
        self.crear_contenido(cuerpo)

    def crear_barra_superior(self):
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
        ).pack(
            side="left",
            padx=25
        )

        tk.Label(
            barra,
            text="Aplicación de escritorio",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            font=("Arial", 9)
        ).pack(
            side="right",
            padx=25
        )

    def crear_menu(self, cuerpo):
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


        # Define las opciones de navegación del menú lateral.
        # Cada opción contiene el nombre del módulo y la
        # función que permite acceder a su pantalla.
        #
        # Se incorpora Recursos para mantener disponible
        # el catálogo desde el módulo de Presupuestos.

        opciones = [
            ("Obras", self.ir_obras),
            ("Recursos", self.ir_recursos),
            ("Presupuestos", None),
            ("Gastos", self.ir_gastos),
            ("Comparar costos", self.ir_comparacion)
        ]


        for texto, comando in opciones:
            seleccionado = texto == "Presupuestos"

            tk.Button(
                menu,
                text=texto,
                command=comando,
                bg="#F8E5E5" if seleccionado else COLOR_BLANCO,
                fg=COLOR_TEXTO,
                relief="flat",
                anchor="w",
                padx=20,
                pady=8,
                font=FUENTE_NORMAL_NEGRITA if seleccionado else FUENTE_NORMAL
            ).pack(fill="x")

    def crear_contenido(self, cuerpo):
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
            text="PRESUPUESTOS",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            font=FUENTE_TITULO
        ).pack(anchor="w")

        tk.Frame(
            contenido,
            bg=COLOR_LINEA,
            height=2
        ).pack(
            fill="x",
            pady=(8, 20)
        )

        if self.rol != "gerencia":
            self.crear_formulario(contenido)
        else:
            tk.Label(
                contenido,
                text="Modo consulta - Gerencia",
                bg=COLOR_FONDO,
                fg=COLOR_TEXTO_SECUNDARIO,
                font=FUENTE_NORMAL_NEGRITA
            ).pack(
                anchor="w",
                pady=(0, 15)
            )

        self.crear_tabla(contenido)

    def crear_formulario(self, contenido):
        panel = tk.Frame(
            contenido,
            bg=COLOR_BLANCO,
            bd=1,
            relief="solid",
            padx=20,
            pady=20
        )

        panel.pack(
            fill="x",
            pady=(0, 20)
        )

        tk.Label(
            panel,
            text="Registrar presupuesto",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=("Arial", 14, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 15)
        )

        tk.Label(
            panel,
            text="Obra",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=5
        )

        self.combo_obra = ttk.Combobox(
            panel,
            state="readonly",
            font=FUENTE_NORMAL
        )

        self.combo_obra.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=5,
            pady=(5, 10)
        )

        tk.Label(
            panel,
            text="Partida",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=5
        )

        self.entrada_partida = tk.Entry(
            panel,
            font=FUENTE_ENTRADA
        )

        self.entrada_partida.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=5,
            pady=(5, 10)
        )

        tk.Label(
            panel,
            text="Monto presupuestado",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=5
        )

        self.entrada_monto = tk.Entry(
            panel,
            font=FUENTE_ENTRADA
        )

        self.entrada_monto.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=5,
            pady=(5, 10)
        )

        tk.Button(
            panel,
            text="Guardar presupuesto",
            command=self.guardar_presupuesto,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            font=FUENTE_NORMAL_NEGRITA
        ).grid(
            row=3,
            column=2,
            sticky="e",
            padx=5,
            pady=(10, 0)
        )

        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)
        panel.columnconfigure(2, weight=1)

        self.cargar_obras()

    def crear_tabla(self, contenido):
        panel_tabla = tk.Frame(
            contenido,
            bg=COLOR_BLANCO,
            bd=1,
            relief="solid",
            padx=15,
            pady=15
        )

        panel_tabla.pack(
            fill="both",
            expand=True
        )

        columnas = (
            "obra",
            "partida",
            "monto"
        )

        self.tabla = ttk.Treeview(
            panel_tabla,
            columns=columnas,
            show="headings"
        )

        self.tabla.heading(
            "obra",
            text="Obra"
        )

        self.tabla.heading(
            "partida",
            text="Partida"
        )

        self.tabla.heading(
            "monto",
            text="Monto"
        )

        self.tabla.column(
            "obra",
            width=220
        )

        self.tabla.column(
            "partida",
            width=260
        )

        self.tabla.column(
            "monto",
            width=150,
            anchor="e"
        )

        self.tabla.pack(
            fill="both",
            expand=True
        )

        self.cargar_presupuestos()

    def cargar_obras(self):
        self.obras = obtener_obras()

        nombres = [
            obra[1]
            for obra in self.obras
        ]

        self.combo_obra["values"] = nombres

    def guardar_presupuesto(self):
        indice = self.combo_obra.current()

        partida = self.entrada_partida.get().strip()
        monto_texto = self.entrada_monto.get().strip()

        # Validar obra seleccionada
        if indice == -1:
            messagebox.showerror(
                "Datos incompletos",
                "Debe seleccionar una obra."
            )
            return

        # Validar partida
        if partida == "":
            messagebox.showerror(
                "Datos incompletos",
                "Debe ingresar una partida."
            )
            return

        # Validar monto vacío
        if monto_texto == "":
            messagebox.showerror(
                "Monto requerido",
                "Debe ingresar un monto."
            )
            return

        # Validar que el monto sea numérico
        try:
            monto = float(monto_texto)

        except ValueError:
            messagebox.showerror(
                "Monto inválido",
                "El monto debe ser un valor numérico."
            )
            return

        # Validar monto negativo
        if monto < 0:
            messagebox.showerror(
                "Monto inválido",
                "El monto no puede ser negativo."
            )
            return

        # Validar monto igual a cero
        if monto == 0:
            messagebox.showerror(
                "Monto inválido",
                "El monto debe ser mayor que cero."
            )
            return

        obra_id = self.obras[indice][0]

        agregar_presupuesto(
            obra_id,
            partida,
            monto
        )

        messagebox.showinfo(
            "Presupuesto registrado",
            "El presupuesto se guardó correctamente."
        )

        self.entrada_partida.delete(
            0,
            tk.END
        )

        self.entrada_monto.delete(
            0,
            tk.END
        )

        self.cargar_presupuestos()

    def cargar_presupuestos(self):
        for registro in self.tabla.get_children():
            self.tabla.delete(registro)

        presupuestos = obtener_presupuestos()

        for presupuesto in presupuestos:
            nombre_obra = presupuesto[1]
            partida = presupuesto[2]
            monto = presupuesto[3]

            self.tabla.insert(
                "",
                "end",
                values=(
                    nombre_obra,
                    partida,
                    f"$ {monto:,.0f}"
                )
            )

    def ir_recursos(self):
        """
        Permite acceder al maestro de recursos desde
        la pantalla de Presupuestos.
        """

        # Importamos la clase encargada de construir
        # la interfaz gráfica del maestro de recursos.
        # La importación se realiza dentro de la función
        # para evitar dependencias circulares.

        from .resources_view import ResourcesView

        # Reutilizamos la ventana principal y enviamos
        # el usuario y su rol actual para conservar
        # los permisos establecidos al iniciar sesión.

        ResourcesView(
            self.ventana,
            self.usuario,
            self.rol
        )

    def ir_obras(self):
        from .main_view import MainView

        MainView(
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