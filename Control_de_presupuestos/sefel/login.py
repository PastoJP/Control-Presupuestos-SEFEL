from .main_view import MainView

import tkinter as tk

from .database import verificar_usuario

from .styles import (
    COLOR_PRINCIPAL,
    COLOR_PRINCIPAL_ACTIVO,
    COLOR_FONDO,
    COLOR_BLANCO,
    COLOR_TEXTO,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_LINEA,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_NORMAL_NEGRITA,
    FUENTE_ENTRADA
)


class LoginView:

    def __init__(self, ventana):
        self.ventana = ventana

        self.intentos_fallidos = 0
        self.bloqueado = False

        self.ventana.title(
            "SEFEL - Control de presupuestos y gastos"
        )

        self.ventana.geometry("1000x650")
        self.ventana.configure(bg=COLOR_FONDO)

        self.crear_interfaz()

    def crear_interfaz(self):
        self.crear_barra_superior()
        self.crear_contenido()

    def crear_barra_superior(self):

        barra_superior = tk.Frame(
            self.ventana,
            bg=COLOR_PRINCIPAL,
            height=55
        )

        barra_superior.pack(fill="x")
        barra_superior.pack_propagate(False)

        titulo_sefel = tk.Label(
            barra_superior,
            text="SEFEL | Control de presupuestos y gastos",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            font=("Arial", 13, "bold")
        )

        titulo_sefel.pack(
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

    def crear_contenido(self):

        contenido = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )

        contenido.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=30
        )

        titulo = tk.Label(
            contenido,
            text="CONTROL DE ACCESO",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            font=FUENTE_TITULO
        )

        titulo.pack(anchor="w")

        linea = tk.Frame(
            contenido,
            bg=COLOR_LINEA,
            height=2
        )

        linea.pack(
            fill="x",
            pady=(8, 25)
        )

        subtitulo = tk.Label(
            contenido,
            text="Ingreso al sistema de SEFEL",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=FUENTE_SUBTITULO
        )

        subtitulo.pack(
            anchor="w",
            padx=20
        )

        self.crear_formulario(contenido)

        mensaje_inferior = tk.Label(
            contenido,
            text="Solo el personal autorizado puede acceder a la información.",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Arial", 9)
        )

        mensaje_inferior.pack()

    def crear_formulario(self, contenido):

        tarjeta = tk.Frame(
            contenido,
            bg=COLOR_BLANCO,
            bd=1,
            relief="solid",
            padx=35,
            pady=30
        )

        tarjeta.pack(pady=15)

        titulo_login = tk.Label(
            tarjeta,
            text="Inicio de sesión",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_TITULO
        )

        titulo_login.pack()

        descripcion = tk.Label(
            tarjeta,
            text="Ingrese sus credenciales para continuar",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=FUENTE_NORMAL
        )

        descripcion.pack(
            pady=(5, 20)
        )

        label_usuario = tk.Label(
            tarjeta,
            text="Usuario",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        )

        label_usuario.pack(anchor="w")

        self.entrada_usuario = tk.Entry(
            tarjeta,
            width=35,
            font=FUENTE_ENTRADA
        )

        self.entrada_usuario.pack(
            ipady=6,
            pady=(5, 15)
        )

        label_contrasena = tk.Label(
            tarjeta,
            text="Contraseña",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            font=FUENTE_NORMAL_NEGRITA
        )

        label_contrasena.pack(anchor="w")

        self.entrada_contrasena = tk.Entry(
            tarjeta,
            width=35,
            font=FUENTE_ENTRADA,
            show="*"
        )

        self.entrada_contrasena.pack(
            ipady=6,
            pady=(5, 10)
        )

        self.label_mensaje = tk.Label(
            tarjeta,
            text="",
            bg=COLOR_BLANCO,
            fg="red",
            font=("Arial", 9)
        )

        self.label_mensaje.pack(
            pady=(0, 10)
        )

        boton_ingresar = tk.Button(
            tarjeta,
            text="Ingresar al sistema",
            command=self.iniciar_sesion,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_BLANCO,
            activebackground=COLOR_PRINCIPAL_ACTIVO,
            activeforeground=COLOR_BLANCO,
            font=FUENTE_NORMAL_NEGRITA,
            width=22,
            cursor="hand2"
        )

        boton_ingresar.pack(ipady=6)

        self.entrada_contrasena.bind(
            "<Return>",
            lambda event: self.iniciar_sesion()
        )

    def iniciar_sesion(self):

        if self.bloqueado:
            return

        usuario = self.entrada_usuario.get().strip()
        contrasena = self.entrada_contrasena.get()

        if not usuario or not contrasena:
            self.label_mensaje.config(
                text="Debe ingresar usuario y contraseña."
            )
            return

        if verificar_usuario(usuario, contrasena):

            self.intentos_fallidos = 0

            MainView(
                self.ventana,
                usuario=usuario
            )

            return

        self.intentos_fallidos += 1

        intentos_restantes = 3 - self.intentos_fallidos

        self.entrada_contrasena.delete(
            0,
            tk.END
        )

        self.entrada_contrasena.focus()

        if self.intentos_fallidos >= 3:

            self.bloquear_login()

            return

        self.label_mensaje.config(
            text=(
                "Usuario o contraseña incorrectos. "
                f"Intentos restantes: {intentos_restantes}"
            )
        )

    def bloquear_login(self):

        self.bloqueado = True

        self.entrada_usuario.config(
            state="disabled"
        )

        self.entrada_contrasena.config(
            state="disabled"
        )

        self.label_mensaje.config(
            text="Acceso bloqueado por un minuto :C ."
        )

        self.ventana.after(
            60000,
            self.desbloquear_login
        )

    def desbloquear_login(self):

        self.bloqueado = False
        self.intentos_fallidos = 0

        self.entrada_usuario.config(
            state="normal"
        )

        self.entrada_contrasena.config(
            state="normal"
        )

        self.entrada_contrasena.delete(
            0,
            tk.END
        )

        self.label_mensaje.config(
            text=""
        )

        self.entrada_usuario.focus()