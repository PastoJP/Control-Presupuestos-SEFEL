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

from .database import (
    obtener_resumen_costos,
    obtener_resumen_partidas_obra
)

COLOR_DEFICIT = "#f37681"


class CompareView:

    def __init__(
        self,
        ventana,
        usuario,
        rol="administrador",
        obra_seleccionada=None
    ):
        self.ventana = ventana
        self.usuario = usuario
        self.rol = rol
        self.obra_seleccionada = obra_seleccionada

        self.ids_obras = {}

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
        cuerpo.pack(fill="both", expand=True)

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
        ).pack(side="left", padx=25)

        tk.Label(
            barra,
            text="Aplicación de escritorio",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            font=("Arial", 9)
        ).pack(side="right", padx=25)

    def crear_menu(self, cuerpo):
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
        ).pack(anchor="w", padx=20, pady=(20, 10))

        opciones = [
            ("Obras", self.ir_obras),
            ("Presupuestos", self.ir_presupuestos),
            ("Gastos", self.ir_gastos),
            ("Comparar costos", None)
        ]

        for texto, comando in opciones:
            seleccionado = texto == "Comparar costos"

            tk.Button(
                menu,
                text=texto,
                command=comando,
                bg="#e8f1f5" if seleccionado else COLOR_BLANCO,
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
            text="COMPARACIÓN DE COSTOS",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            font=FUENTE_TITULO
        ).pack(anchor="w")

        tk.Frame(
            contenido,
            bg=COLOR_LINEA,
            height=2
        ).pack(fill="x", pady=(8, 20))

        self.crear_panel_resumen(contenido)
        self.crear_panel_detalle(contenido)
        self.cargar_comparacion()

    def crear_panel_resumen(self, contenido):
        panel = tk.Frame(
            contenido,
            bg=COLOR_BLANCO,
            bd=1,
            relief="solid",
            padx=15,
            pady=15
        )
        panel.pack(fill="x", pady=(0, 15))

        tk.Label(
            panel,
            text="Resumen por obra",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            panel,
            text="Buscar obra",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        ).pack(anchor="w")

        self.entrada_busqueda = tk.Entry(
            panel,
            font=FUENTE_ENTRADA
        )
        self.entrada_busqueda.pack(fill="x", pady=(5, 15), ipady=5)
        self.entrada_busqueda.bind("<KeyRelease>", self.filtrar_comparacion)

        columnas = (
            "obra",
            "presupuesto",
            "gastos",
            "diferencia",
            "estado"
        )

        self.tabla = ttk.Treeview(
            panel,
            columns=columnas,
            show="headings",
            height=5
        )

        self.tabla.heading("obra", text="Obra")
        self.tabla.heading("presupuesto", text="Presupuesto")
        self.tabla.heading("gastos", text="Gastos")
        self.tabla.heading("diferencia", text="Diferencia")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("obra", width=280, anchor="w")
        self.tabla.column("presupuesto", width=160, anchor="center")
        self.tabla.column("gastos", width=160, anchor="center")
        self.tabla.column("diferencia", width=160, anchor="center")
        self.tabla.column("estado", width=130, anchor="center")

        self.tabla.pack(fill="x")

        self.tabla.tag_configure(
            "deficit",
            background=COLOR_DEFICIT,
            foreground="black"
        )

        self.tabla.tag_configure(
            "normal",
            background=COLOR_BLANCO,
            foreground="black"
        )

        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_obra)

        tk.Label(
            panel,
            text="Seleccione una obra para revisar el detalle por partida.",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=FUENTE_NORMAL
        ).pack(anchor="w", pady=(10, 0))


    def crear_panel_detalle(self, contenido):
        panel = tk.Frame(
            contenido,
            bg=COLOR_BLANCO,
            bd=1,
            relief="solid",
            padx=15,
            pady=15
        )
        panel.pack(fill="both", expand=True)

        self.titulo_detalle = tk.Label(
            panel,
            text="Detalle por partida",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=("Arial", 14, "bold")
        )
        self.titulo_detalle.pack(anchor="w", pady=(0, 10))

        columnas = (
            "partida",
            "presupuesto",
            "gastos",
            "diferencia"
        )

        self.tabla_detalle = ttk.Treeview(
            panel,
            columns=columnas,
            show="headings",
            height=7
        )

        self.tabla_detalle.heading("partida", text="Partida")
        self.tabla_detalle.heading("presupuesto", text="Presupuesto")
        self.tabla_detalle.heading("gastos", text="Gastos acumulados")
        self.tabla_detalle.heading("diferencia", text="Diferencia")

        self.tabla_detalle.column("partida", width=300, anchor="w")
        self.tabla_detalle.column("presupuesto", width=180, anchor="center")
        self.tabla_detalle.column("gastos", width=180, anchor="center")
        self.tabla_detalle.column("diferencia", width=180, anchor="center")

        self.tabla_detalle.pack(fill="both", expand=True)

        self.tabla_detalle.tag_configure(
            "deficit",
            background=COLOR_DEFICIT,
            foreground="black"
        )

        self.tabla_detalle.tag_configure(
            "normal",
            background=COLOR_BLANCO,
            foreground="black"
        )

        self.label_totales = tk.Label(
            panel,
            text="Seleccione una obra para visualizar sus partidas.",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=FUENTE_NORMAL_NEGRITA,
            padx=8,
            pady=6
        )
        self.label_totales.pack(anchor="e", pady=(10, 0))

    def cargar_comparacion(self, filtro=""):
        for registro in self.tabla.get_children():
            self.tabla.delete(registro)

        self.ids_obras.clear()

        datos = obtener_resumen_costos()
        filtro = filtro.lower().strip()

        primera_fila = None
        fila_seleccionada = None

        for dato in datos:
            obra_id = dato[0]
            nombre = dato[1]
            presupuesto = dato[2]
            gastos = dato[3]

            if filtro and filtro not in nombre.lower():
                continue

            diferencia = presupuesto - gastos

            if diferencia < 0:
                estado = "Déficit"
                etiqueta = "deficit"
            elif diferencia > 0:
                estado = "Superávit"
                etiqueta = "normal"
            else:
                estado = "Equilibrado"
                etiqueta = "normal"

            fila = self.tabla.insert(
                "",
                "end",
                values=(
                    nombre,
                    f"$ {presupuesto:,.0f}",
                    f"$ {gastos:,.0f}",
                    f"$ {diferencia:,.0f}",
                    estado
                ),
                tags=(etiqueta,)
            )

            self.ids_obras[fila] = obra_id

            if primera_fila is None:
                primera_fila = fila

            if self.obra_seleccionada is not None and nombre == self.obra_seleccionada:
                fila_seleccionada = fila

        fila_a_seleccionar = fila_seleccionada if fila_seleccionada else primera_fila

        if fila_a_seleccionar:
            self.tabla.selection_set(fila_a_seleccionar)
            self.tabla.focus(fila_a_seleccionar)
            self.tabla.see(fila_a_seleccionar)
            self.seleccionar_obra()

    def seleccionar_obra(self, event=None):
        seleccion = self.tabla.selection()

        if not seleccion:
            return

        fila = seleccion[0]
        obra_id = self.ids_obras.get(fila)

        if obra_id is None:
            return

        valores = self.tabla.item(fila, "values")
        nombre_obra = valores[0]

        self.cargar_detalle_partidas(obra_id, nombre_obra)

    def cargar_detalle_partidas(self, obra_id, nombre_obra):
        for registro in self.tabla_detalle.get_children():
            self.tabla_detalle.delete(registro)

        datos = obtener_resumen_partidas_obra(obra_id)

        self.titulo_detalle.config(
            text=f"Detalle por partida - {nombre_obra}"
        )

        if not datos:
            self.label_totales.config(
                text="La obra no tiene partidas registradas.",
                bg=COLOR_BLANCO,
                fg=COLOR_TEXTO_SECUNDARIO
            )
            return

        total_presupuesto = 0
        total_gastos = 0

        for dato in datos:
            partida = dato[0]
            presupuesto = dato[1]
            gastos = dato[2]

            diferencia = presupuesto - gastos

            total_presupuesto += presupuesto
            total_gastos += gastos

            etiqueta = "deficit" if diferencia < 0 else "normal"

            self.tabla_detalle.insert(
                "",
                "end",
                values=(
                    partida,
                    f"$ {presupuesto:,.0f}",
                    f"$ {gastos:,.0f}",
                    f"$ {diferencia:,.0f}"
                ),
                tags=(etiqueta,)
            )

        diferencia_total = total_presupuesto - total_gastos

        fondo_total = COLOR_DEFICIT if diferencia_total < 0 else COLOR_BLANCO

        self.label_totales.config(
            text=(
                f"Presupuesto total: $ {total_presupuesto:,.0f}   |   "
                f"Gastos totales: $ {total_gastos:,.0f}   |   "
                f"Diferencia: $ {diferencia_total:,.0f}"
            ),
            bg=fondo_total,
            fg="black"
        )

    def filtrar_comparacion(self, event=None):
        texto = self.entrada_busqueda.get()
        self.cargar_comparacion(texto)

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