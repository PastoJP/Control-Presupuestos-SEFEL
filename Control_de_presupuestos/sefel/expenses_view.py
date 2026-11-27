import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

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
    agregar_gasto,
    obtener_gastos,
    actualizar_gasto
)


class ExpensesView:

    def __init__(self, ventana, usuario, rol="administrador"):
        self.ventana = ventana
        self.usuario = usuario
        self.rol = rol
        self.obras = []

        # Guarda el ID del gasto que se está editando.
        self.gasto_editando_id = None

        # Relaciona cada fila de la tabla con el ID real del gasto.
        self.ids_gastos = {}

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

        # Define los módulos disponibles en el menú lateral.
        # Cada opción relaciona el nombre de una pantalla
        # con la función encargada de abrirla.
        #
        # Se incorpora Recursos para permitir consultar
        # el catálogo desde la pantalla de Gastos.
        #
        # None indica que Gastos es la pantalla actual.

        opciones = [
            ("Obras", self.ir_obras),
            ("Recursos", self.ir_recursos),
            ("Presupuestos", self.ir_presupuestos),
            ("Gastos", None),
            ("Comparar costos", self.ir_comparacion)
        ]

        for texto, comando in opciones:
            seleccionado = texto == "Gastos"

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
                font=(
                    FUENTE_NORMAL_NEGRITA
                    if seleccionado
                    else FUENTE_NORMAL
                )
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
            text="GASTOS",
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

    # FORMULARIO

    def crear_formulario(self, contenido):
        self.panel_formulario = tk.Frame(
            contenido,
            bg=COLOR_BLANCO,
            bd=1,
            relief="solid",
            padx=20,
            pady=20
        )

        self.panel_formulario.pack(
            fill="x",
            pady=(0, 20)
        )

        self.titulo_formulario = tk.Label(
            self.panel_formulario,
            text="Registrar gasto real",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=("Arial", 14, "bold")
        )

        self.titulo_formulario.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 15)
        )

        # OBRA

        tk.Label(
            self.panel_formulario,
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
            self.panel_formulario,
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

        # PARTIDA

        tk.Label(
            self.panel_formulario,
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
            self.panel_formulario,
            font=FUENTE_ENTRADA
        )

        self.entrada_partida.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=5,
            pady=(5, 10)
        )

        # CONCEPTO

        tk.Label(
            self.panel_formulario,
            text="Concepto",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=5
        )

        self.entrada_concepto = tk.Entry(
            self.panel_formulario,
            font=FUENTE_ENTRADA
        )

        self.entrada_concepto.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=5,
            pady=(5, 10)
        )

        # MONTO

        tk.Label(
            self.panel_formulario,
            text="Monto",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=5
        )

        self.entrada_monto = tk.Entry(
            self.panel_formulario,
            font=FUENTE_ENTRADA
        )

        self.entrada_monto.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=5,
            pady=(5, 10)
        )

        # FECHA

        tk.Label(
            self.panel_formulario,
            text="Fecha",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        ).grid(
            row=3,
            column=1,
            sticky="w",
            padx=5
        )

        self.entrada_fecha = tk.Entry(
            self.panel_formulario,
            font=FUENTE_ENTRADA
        )

        self.entrada_fecha.grid(
            row=4,
            column=1,
            sticky="ew",
            padx=5,
            pady=(5, 10)
        )

        self.entrada_fecha.insert(
            0,
            "18-11-2026"
        )

        # BOTONES

        self.frame_botones = tk.Frame(
            self.panel_formulario,
            bg=COLOR_BLANCO
        )

        self.frame_botones.grid(
            row=4,
            column=2,
            sticky="e",
            padx=5
        )

        self.boton_guardar = tk.Button(
            self.frame_botones,
            text="Guardar gasto",
            command=self.guardar_gasto,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            activebackground=COLOR_PRINCIPAL,
            activeforeground=COLOR_BLANCO,
            font=FUENTE_NORMAL_NEGRITA,
            cursor="hand2"
        )

        self.boton_guardar.pack(
            side="left",
            padx=(0, 5),
            ipadx=8,
            ipady=3
        )

        self.boton_cancelar = tk.Button(
            self.frame_botones,
            text="Cancelar edición",
            command=self.cancelar_edicion,
            bg="#dddddd",
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA,
            cursor="hand2"
        )

        # Este botón solo aparece mientras se edita.
        self.boton_cancelar.pack_forget()

        self.panel_formulario.columnconfigure(
            0,
            weight=1
        )

        self.panel_formulario.columnconfigure(
            1,
            weight=1
        )

        self.panel_formulario.columnconfigure(
            2,
            weight=1
        )

        self.cargar_obras()

    # TABLA

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

        fila_titulo = tk.Frame(
            panel_tabla,
            bg=COLOR_BLANCO
        )

        fila_titulo.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            fila_titulo,
            text="Gastos registrados",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=("Arial", 14, "bold")
        ).pack(
            side="left"
        )

        boton_editar = tk.Button(
            fila_titulo,
            text="Editar gasto seleccionado",
            command=self.editar_gasto_seleccionado,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            activebackground=COLOR_PRINCIPAL,
            activeforeground=COLOR_BLANCO,
            font=FUENTE_NORMAL_NEGRITA,
            cursor="hand2"
        )

        if self.rol != "gerencia":
            boton_editar.pack(
                side="right",
                ipadx=8,
                ipady=3
            )

        columnas = (
            "obra",
            "partida",
            "concepto",
            "monto",
            "fecha"
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
            "concepto",
            text="Concepto"
        )

        self.tabla.heading(
            "monto",
            text="Monto"
        )

        self.tabla.heading(
            "fecha",
            text="Fecha"
        )

        self.tabla.column(
            "obra",
            width=160
        )

        self.tabla.column(
            "partida",
            width=160
        )

        self.tabla.column(
            "concepto",
            width=220
        )

        self.tabla.column(
            "monto",
            width=120,
            anchor="e"
        )

        self.tabla.column(
            "fecha",
            width=110,
            anchor="center"
        )

        self.tabla.pack(
            fill="both",
            expand=True
        )

        if self.rol != "gerencia":
            self.tabla.bind(
                "<Double-1>",
            self.editar_gasto_seleccionado
        )

        if self.rol == "gerencia":
            texto_ayuda = "Modo consulta: puede revisar los gastos registrados."
        else:
            texto_ayuda = (
                "Seleccione un gasto y presione Editar gasto seleccionado "
                "o haga doble clic sobre él."
            )

        tk.Label(
            panel_tabla,
            text=texto_ayuda,
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Arial", 9)
        ).pack(
            anchor="w",
            pady=(10, 0)
        )
        self.cargar_gastos()

    # OBRAS

    def cargar_obras(self):
        self.obras = obtener_obras()

        nombres = [
            obra[1]
            for obra in self.obras
        ]

        self.combo_obra["values"] = nombres

    # VALIDACIONES

    def obtener_datos_formulario(self):
        indice = self.combo_obra.current()

        partida = self.entrada_partida.get().strip()
        concepto = self.entrada_concepto.get().strip()
        monto_texto = self.entrada_monto.get().strip()
        fecha = self.entrada_fecha.get().strip()

        # Validar obra
        if indice == -1:
            messagebox.showerror(
                "Datos incompletos",
                "Debe seleccionar una obra."
            )
            return None

        # Validar partida
        if partida == "":
            messagebox.showerror(
                "Datos incompletos",
                "Debe ingresar una partida."
            )
            return None

        # Validar concepto
        if concepto == "":
            messagebox.showerror(
                "Datos incompletos",
                "Debe ingresar un concepto."
            )
            return None

        # Validar monto vacío
        if monto_texto == "":
            messagebox.showerror(
                "Monto requerido",
                "Debe ingresar un monto."
            )
            return None

        # Validar que el monto sea numérico
        try:
            monto = float(
                monto_texto
            )

        except ValueError:
            messagebox.showerror(
                "Monto inválido",
                "El monto debe ser un valor numérico."
            )
            return None

        # Validar monto negativo
        if monto < 0:
            messagebox.showerror(
                "Monto inválido",
                "El monto no puede ser negativo."
            )
            return None

        # Validar monto igual a cero
        if monto == 0:
            messagebox.showerror(
                "Monto inválido",
                "El monto debe ser mayor que cero."
            )
            return None

        # Validar fecha vacía
        if fecha == "":
            messagebox.showerror(
                "Fecha requerida",
                "Debe ingresar una fecha."
            )
            return None

        # Validar formato y fecha real
        try:
            fecha_convertida = datetime.strptime(
                fecha,
                "%d-%m-%Y"
            )

        except ValueError:
            messagebox.showerror(
                "Fecha inválida",
                "La fecha debe tener el formato DD-MM-AAAA y corresponder a una fecha válida."
            )
            return None

        # Validar año mínimo
        if fecha_convertida.year < 2000:
            messagebox.showerror(
                "Fecha inválida",
                "El año de la fecha debe ser igual o posterior al año 2000."
            )
            return None

        obra_id = self.obras[indice][0]

        return (
            obra_id,
            partida,
            concepto,
            monto,
            fecha
        )

    # GUARDAR NUEVO GASTO

    def guardar_gasto(self):
        # Si estamos editando, el mismo botón guarda cambios.
        if self.gasto_editando_id is not None:
            self.guardar_cambios()
            return

        datos = self.obtener_datos_formulario()

        if datos is None:
            return

        obra_id = datos[0]
        partida = datos[1]
        concepto = datos[2]
        monto = datos[3]
        fecha = datos[4]

        agregar_gasto(
            obra_id,
            partida,
            concepto,
            monto,
            fecha
        )

        messagebox.showinfo(
            "Gasto registrado",
            "El gasto se guardó correctamente."
        )

        self.limpiar_formulario()

        self.cargar_gastos()

    # EDITAR GASTO

    def editar_gasto_seleccionado(self, event=None):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showerror(
                "Gasto no seleccionado",
                "Debe seleccionar un gasto para editar."
            )
            return

        fila = seleccion[0]

        gasto_id = self.ids_gastos.get(
            fila
        )

        if gasto_id is None:
            return

        valores = self.tabla.item(
            fila,
            "values"
        )

        if not valores:
            return

        nombre_obra = valores[0]
        partida = valores[1]
        concepto = valores[2]
        monto_texto = str(
            valores[3]
        )
        fecha = valores[4]

        # El monto de la tabla viene como "$ 100,000".
        monto_texto = (
            monto_texto
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

        self.gasto_editando_id = gasto_id

        # Seleccionar obra.
        nombres_obras = [
            obra[1]
            for obra in self.obras
        ]

        if nombre_obra in nombres_obras:
            indice_obra = nombres_obras.index(
                nombre_obra
            )

            self.combo_obra.current(
                indice_obra
            )

        # Cargar partida.
        self.entrada_partida.delete(
            0,
            tk.END
        )

        self.entrada_partida.insert(
            0,
            partida
        )

        # Cargar concepto.
        self.entrada_concepto.delete(
            0,
            tk.END
        )

        self.entrada_concepto.insert(
            0,
            concepto
        )

        # Cargar monto.
        self.entrada_monto.delete(
            0,
            tk.END
        )

        self.entrada_monto.insert(
            0,
            monto_texto
        )

        # Cargar fecha.
        self.entrada_fecha.delete(
            0,
            tk.END
        )

        self.entrada_fecha.insert(
            0,
            fecha
        )

        self.titulo_formulario.config(
            text="Editar gasto"
        )

        self.boton_guardar.config(
            text="Guardar cambios"
        )

        self.boton_cancelar.pack(
            side="left",
            padx=(5, 0),
            ipadx=8,
            ipady=3
        )

        self.entrada_concepto.focus()

    # GUARDAR CAMBIOS

    def guardar_cambios(self):
        if self.gasto_editando_id is None:
            return

        datos = self.obtener_datos_formulario()

        if datos is None:
            return

        obra_id = datos[0]
        partida = datos[1]
        concepto = datos[2]
        monto = datos[3]
        fecha = datos[4]

        actualizar_gasto(
            self.gasto_editando_id,
            obra_id,
            partida,
            concepto,
            monto,
            fecha
        )

        messagebox.showinfo(
            "Gasto actualizado",
            "Los cambios del gasto se guardaron correctamente."
        )

        self.cancelar_edicion()

        self.cargar_gastos()

    # CANCELAR EDICIÓN

    def cancelar_edicion(self):
        self.gasto_editando_id = None

        self.titulo_formulario.config(
            text="Registrar gasto real"
        )

        self.boton_guardar.config(
            text="Guardar gasto"
        )

        self.boton_cancelar.pack_forget()

        self.limpiar_formulario()

        # Quitar selección visual de la tabla.
        for fila in self.tabla.selection():
            self.tabla.selection_remove(
                fila
            )

    # LIMPIAR FORMULARIO

    def limpiar_formulario(self):
        self.combo_obra.set("")

        self.entrada_partida.delete(
            0,
            tk.END
        )

        self.entrada_concepto.delete(
            0,
            tk.END
        )

        self.entrada_monto.delete(
            0,
            tk.END
        )

        self.entrada_fecha.delete(
            0,
            tk.END
        )

        self.entrada_fecha.insert(
            0,
            "18-11-2026"
        )

    # CARGAR GASTOS

    def cargar_gastos(self):
        for registro in self.tabla.get_children():
            self.tabla.delete(
                registro
            )

        self.ids_gastos.clear()

        gastos = obtener_gastos()

        for gasto in gastos:
            gasto_id = gasto[0]
            nombre_obra = gasto[1]
            partida = gasto[2]
            concepto = gasto[3]
            monto = gasto[4]
            fecha = gasto[5]

            fila = self.tabla.insert(
                "",
                "end",
                values=(
                    nombre_obra,
                    partida,
                    concepto,
                    f"$ {monto:,.0f}",
                    fecha
                )
            )

            self.ids_gastos[fila] = gasto_id

    def ir_recursos(self):
        """
        Permite acceder al maestro de recursos desde
        el módulo de Gastos.
        """

        # Importa la clase que construye la interfaz
        # gráfica del maestro de recursos.
        # Se importa dentro de la función para evitar
        # dependencias circulares entre los módulos.

        from .resources_view import ResourcesView

        # Reutiliza la ventana principal de la aplicación.
        # Conserva el usuario que inició sesión y su rol,
        # evitando que los permisos cambien al navegar.

        ResourcesView(
            self.ventana,
            self.usuario,
            self.rol
        )

    # NAVEGACIÓN

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

    def ir_comparacion(self):
        from .compare_view import CompareView

        CompareView(
            self.ventana,
            self.usuario,
            self.rol
        )