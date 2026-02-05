# ============================
# Importación de librerías
# ============================

import glob, os
from argon2 import PasswordHasher, exceptions

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QLabel, QWidget, QMessageBox, QFormLayout)

import c_a_aplicacion_inicial, z_estilos



# ============================
# Mensaje inicial de bienvenida
# ============================

MENSAJE_REGISTRO = """
<b>Bienvenido a Lucy:</b><br><br>
Este sistema cuenta con dos funcionalidades básicas:<br><br>
<ul>
    <li><b>Películas</b>: Te permitirá puntuar películas y series en base a lo que se te harán recomendaciones personalizadas y predicciones sobre si te va a gustar un determinado titulo o no.</li><br>
    <li><b>Chat</b>: Te permitirá mantener una conversación con una IA Generativa que te permitirá crear imágenes, enviar archivos via Telegram, realizar búsquedas en Google y ejecutar comandos en tu ordenador.</li><br>
</ul>
"""



# ============================
# Esqueleto del registro e inicio de sesión
# ============================

class MainWindow(QMainWindow):

    def __init__(self, width, height, nombre, id, encriptacion):

        super().__init__()

        self.width = width
        self.height = height
        self.encriptacion = encriptacion

        self.nombre = nombre
        self.id = id

        self.setWindowTitle("Lucy")
        self.setWindowIcon(QIcon("z_icon.png"))
        self.setStyleSheet(z_estilos.setStyleSheet)
        self.setGeometry(int(width * 0.25), int(height * 0.125), int(width * 0.5), int(height * 0.75))
        self.setMinimumSize(800, 500)

        self.initUI1()



    # ============================
    # Mensaje de registro
    # ============================

    def mensaje_registro(self):

        mensaje = QMessageBox(self)
        mensaje.setTextFormat(Qt.RichText)

        mensaje.setIcon(QMessageBox.NoIcon)
        mensaje.setText(MENSAJE_REGISTRO)

        mensaje.setStandardButtons(QMessageBox.Ok)
        mensaje.setStyleSheet("""
            QLabel {
                font-size: 14px;
                min-width: 750px;
                min-height: 300px;
            }
        """)

        mensaje.exec_()



    # ============================
    # Función para el inicio de sesión
    # ============================

    def inicioaplicacion(self):

        self.encriptacion.datos_descifrados["Datos_Cifrados/sesion_json.enc"]["usuario"] = {
            'nombre': self.nombre
        }

        self.encriptacion.guardar_json("Datos_Cifrados/sesion_json.enc", contexto="sesion_json")

        self.window = c_a_aplicacion_inicial.MainWindow(self.width, self.height, self.nombre, self.id, self.encriptacion)
        self.window.show()
        self.close()



    # ============================
    # Función para comprobar contraseñas
    # ============================

    def comprobarusuario(self, datos):

        nombre = datos[0].text().strip()
        contrasena = datos[1].text().strip()

        if not nombre and not contrasena:
            QMessageBox.warning(self, "Datos incompletos", "Introduce un nombre y contraseña.")
            return

        existe = False
        for user in self.encriptacion.datos_descifrados["Datos_Cifrados/users_json.enc"].values():
            if user['nombre'] == datos[0].text().strip():

                try:
                    if PasswordHasher().verify(user["password_hash"], datos[1].text().strip()):
                        existe = True
                        self.nombre = user['nombre']
                        self.id = user['id']
                        self.inicioaplicacion()

                except exceptions.VerifyMismatchError:
                    pass

        if not existe:
            QMessageBox.warning(self, "Datos Erróneos", "Usuario o contraseña Incorrectos")
            return



    # ============================
    # Función para registrar un nuevo usuario
    # ============================

    def registrarusuario(self, datos):

        nombre = datos[0].text().strip()
        contrasena = datos[1].text().strip()
        contrasena2 = datos[2].text().strip()


        if not nombre or not contrasena or not contrasena2:
            QMessageBox.warning(self, "Datos incompletos", "Rellena todos los campos correctamente.")
            return

        if nombre in {u["nombre"] for u in self.encriptacion.datos_descifrados["Datos_Cifrados/users_json.enc"].values()}:
            QMessageBox.warning(self, "Datos incompletos", "Usuario ya existente.")
            return

        if contrasena != contrasena2:
            QMessageBox.warning(self, "Datos incorrectos", "Las contraseñas deben de coincidir.")
            return

        if len(contrasena) < 6:
            QMessageBox.warning(self, "Datos incorrectos", "Las contraseña debe de tener al menos 6 caracteres.")
            return

        archivos = glob.glob(os.path.join("Datos_Cifrados", "*_completo_csv.enc"))
        numero = str(max((int(os.path.basename(a).split("_")[0]) for a in archivos), default=0) + 1)

        self.encriptacion.datos_descifrados["Datos_Cifrados/users_json.enc"][numero] = {
            "nombre": nombre,
            "id": numero,
            "password_hash": PasswordHasher().hash(contrasena)
        }

        self.generacion_archivos(numero)

        self.nombre = nombre
        self.id = numero

        self.mensaje_registro()

        self.inicioaplicacion()
        print("Usuario registrado:", self.nombre)



    # ============================
    # Función para generar archivos iniciales
    # ============================

    def generacion_archivos(self, numero):
        self.encriptacion.guardar_json("Datos_Cifrados/users_json.enc", contexto="users_json")

        csv_header = "userId,Mi Nota,tid\n"
        self.encriptacion.datos_descifrados[f"Datos_Cifrados/{numero}_csv.enc"] = csv_header.encode()
        self.encriptacion.guardar_csv(f"Datos_Cifrados/{numero}_csv.enc", contexto=f"{numero}_csv")

        csv_header_completo = "userId,tid,Fecha,Tipo,Titulo,Titulo_ES,Año,Mi Nota,Duracion,Generos,Puntuacion,Num_Votos,Actores,Directores,Idioma\n"
        self.encriptacion.datos_descifrados[f"Datos_Cifrados/{numero}_completo_csv.enc"] = csv_header_completo.encode()
        self.encriptacion.guardar_csv(f"Datos_Cifrados/{numero}_completo_csv.enc", contexto=f"{numero}_completo_csv")



    # ============================
    # Interfaz gráfica de la elección de registro o inicio
    # ============================

    def initUI1(self):
        container = QWidget()
        layout = z_estilos.crear_layout_vertical()
        layout.addWidget(z_estilos.crear_label("Seleciona que quieres hacer", 450), alignment=Qt.AlignCenter)

        botones = z_estilos.crear_layout_horizontal()

        btn_registro = z_estilos.crear_boton("Nuevo Usuario", 250)
        btn_registro.clicked.connect(self.initUI2)
        btn_inicio = z_estilos.crear_boton("Iniciar Sesión", 250)
        btn_inicio.clicked.connect(self.initUI3)

        botones.addWidget(btn_registro)
        botones.addWidget(btn_inicio)
        layout.addLayout(botones)

        container.setLayout(layout)
        self.setCentralWidget(container)



    # ============================
    # Interfaz gráfica del registro de nuevo usuario
    # ============================

    def initUI2(self):
        container = QWidget()
        container.setStyleSheet(z_estilos.form_style)
        layout = z_estilos.crear_layout_vertical()
        layout.addWidget(z_estilos.crear_label("Completa los campos", 450), alignment=Qt.AlignCenter)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(12)

        text_nombre = z_estilos.crear_line("Introduce tu nombre de usuario", 400)
        text_contrasena = z_estilos.crear_line("Introduce tu contraseña de mínimo 6 caracteres", 400, password=True)
        text_contrasena_2 = z_estilos.crear_line("Confirma la contraseña", 400, password=True)

        form.addRow(QLabel('Nombre: '), text_nombre)
        form.addRow(QLabel('Contraseña:'), text_contrasena)
        form.addRow(QLabel('Confirmar Contraseña:'), text_contrasena_2)

        layout.addLayout(form)

        botones = z_estilos.crear_layout_horizontal()

        boton_atras = z_estilos.crear_boton("Atrás", 250)
        boton_atras.clicked.connect(self.initUI1)
        boton_registrar = z_estilos.crear_boton("Registrar Usuario", 250)
        boton_registrar.clicked.connect(lambda: self.registrarusuario([text_nombre, text_contrasena, text_contrasena_2]))

        botones.addWidget(boton_atras)
        botones.addWidget(boton_registrar)
        layout.addLayout(botones)

        container.setLayout(layout)
        self.setCentralWidget(container)



    # ============================
    # Interfaz gráfica del inicio de sesión
    # ============================

    def initUI3(self):
        container = QWidget()
        container.setStyleSheet(z_estilos.form_style)
        layout = z_estilos.crear_layout_vertical()
        layout.addWidget(z_estilos.crear_label("Completa los campos", 450), alignment=Qt.AlignCenter)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(12)

        text_nombre = z_estilos.crear_line("Introduce tu nombre de usuario", 300)
        text_contrasena = z_estilos.crear_line("Introduce tu contraseña", 300, password=True)

        form.addRow(QLabel('Nombre: '), text_nombre)
        form.addRow(QLabel('Contraseña:'), text_contrasena)

        layout.addLayout(form)

        botones = z_estilos.crear_layout_horizontal()

        boton_atras = z_estilos.crear_boton("Atrás", 250)
        boton_atras.clicked.connect(self.initUI1)
        boton_iniciar = z_estilos.crear_boton("Iniciar Sesión", 250)
        boton_iniciar.clicked.connect(lambda: self.comprobarusuario([text_nombre, text_contrasena]))

        botones.addWidget(boton_atras)
        botones.addWidget(boton_iniciar)
        layout.addLayout(botones)

        container.setLayout(layout)
        self.setCentralWidget(container)