# ============================
# Importación de librerías
# ============================

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import speech_recognition as sr
from PyQt5.QtWidgets import (QMainWindow, QLabel, QWidget, QHBoxLayout, QPushButton, QFormLayout, QMessageBox, QScrollArea, QVBoxLayout, QFrame, QSpacerItem, QSizePolicy, QApplication)

from . import c_a_aplicacion_inicial, d_c_chat, z_estilos



# ============================
# Mensaje inicial de bienvenida
# ============================

MENSAJE_INICIAL = """
<b>Bienvenido a la funcionalidad adicional de Lucy.</b><br><br>
Lucy ofrece un chat interactivo, tanto por texto como por voz, que permite realizar cuatro acciones básicas:<br><br>
<ul>
    <li><b>Generación de imágenes:</b> Se pueden generar imágenes a partir de instrucciones proporcionadas.</li><br>
    <li><b>Envío de archivos al móvil:</b> Se permite el envío de archivos o mensajes al dispositivo móvil a través de la aplicación Telegram.</li><br>
    <li><b>Búsquedas en Google:</b> Se pueden realizar búsquedas en Google.</li><br>
    <li><b>Ejecución de comandos:</b> Se pueden ejecutar determinados comandos de forma automática en el ordenador.</li><br>
</ul>
"""



# =====================================
# Reconocimiento de voz y ejecución de la petición
# =====================================

def reconocer_voz():
    reconocedor = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            #print("Escuchando... (habla ahora)")
            try:
                reconocedor.adjust_for_ambient_noise(source, duration=0.5)
                audio = reconocedor.listen(source, timeout=5, phrase_time_limit=10)
                #print("Procesando audio...")
                texto = reconocedor.recognize_google(audio, language="es-ES")
                return texto
            except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
                return "Error"
    except:
        return "Error"



# ============================
# Esqueleto del la funcionalidad secundaria
# ============================

class MainWindow(QMainWindow):

    def __init__(self, width, height, nombre, id, encriptacion):

        super().__init__()

        self.width = width
        self.height = height
        self.nombre = nombre
        self.id = id
        self.encriptacion = encriptacion

        self.mensaje = False
        self.lucy = d_c_chat.Asistente()

        self.setWindowTitle("Lucy")
        self.setWindowIcon(QIcon("data/z_icon.png"))
        self.setStyleSheet(z_estilos.setStyleSheet)
        self.setGeometry(int(width * 0.125), int(height * 0.125), int(width * 0.75), int(height * 0.75))
        self.setMinimumSize(800, 500)

        self.initUI1()



    # ============================
    # Funciones para mostrar el mensaje de bienvenida
    # ============================

    def showEvent(self, event):
        super().showEvent(event)
        if not self.mensaje:
            self.mensaje = True
            self.mensaje_inicial()

    def mensaje_inicial(self):
        mensaje = QMessageBox(self)
        mensaje.setTextFormat(Qt.RichText)

        mensaje.setIcon(QMessageBox.NoIcon)
        mensaje.setWindowTitle("Lucy — Panel de Chat")
        mensaje.setText(MENSAJE_INICIAL)

        mensaje.setStandardButtons(QMessageBox.Ok)
        mensaje.button(QMessageBox.Ok).setText("Continuar")

        mensaje.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 18px;
                min-width: 800px;
                min-height: 360px;
                padding: 12px;
            }

            QPushButton {
                background-color: #2d89ef;
                color: white;
                padding: 8px 24px;
                border-radius: 6px;
                font-size: 18px;
            }

            QPushButton:hover {
                background-color: #3aa0ff;
            }
        """)

        mensaje.exec_()



    # ============================
    # Función para el cambio de pestaña
    # ============================

    def on_click(self):
        self.close()
        self.window = c_a_aplicacion_inicial.MainWindow(self.width, self.height, self.nombre, self.id, self.encriptacion)
        self.window.show()



    # ============================
    # Código para la comunicación usuario-modelo
    # ============================

    def peticion(self, conversacion, tipo):

        if tipo == "audio":
            conversacion = reconocer_voz()
            # print(f"Tú (Voz): {conversacion}")

        if tipo == "texto":
            if conversacion.text().strip() == "":
                QMessageBox.warning(self, "Datos incompletos", "Introduce una consulta.")
                return

        if conversacion != "Error":
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                QApplication.processEvents()
                if tipo == "texto":
                    peticion, respuesta = d_c_chat.ejecutar_peticion(self.lucy, conversacion.text().strip())
                else:
                    peticion, respuesta = d_c_chat.ejecutar_peticion(self.lucy, conversacion)
            finally:
                QApplication.restoreOverrideCursor()

            texto = QFrame()
            texto.setStyleSheet("""
                    QFrame {
                        background-color: #202C33; 
                        border-radius: 10px; 
                        padding: 5px;
                        margin-bottom: 5px;
                    }
                """)

            layout = QVBoxLayout(texto)

            peticion_label = z_estilos.crear_label(peticion, int(self.width * 0.35))
            peticion_label.setAlignment(Qt.AlignLeft)
            peticion_label.setStyleSheet("color: white; border: none;")

            respuesta_label = z_estilos.crear_label(respuesta, int(self.width * 0.35))
            respuesta_label.setAlignment(Qt.AlignLeft)
            respuesta_label.setStyleSheet("color: #00A884; border: none;")

            layout.addWidget(peticion_label)
            layout.addWidget(respuesta_label)

            self.messages_layout.insertWidget((self.messages_layout.count() - 1), texto)

            self.scroll.verticalScrollBar().rangeChanged.connect(
                lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())
            )

        if conversacion == "Error":
            QMessageBox.warning(self, "Error Micrófono", "No se ha detectado un micrófono.")

        self.initUI1()



    # ============================
    # Interfaz gráfica del chat interactivo
    # ============================

    def initUI1(self):
        container = QWidget()
        container.setStyleSheet(z_estilos.form_style)
        layout = z_estilos.crear_layout_vertical()
        layout.addWidget(z_estilos.crear_label("Historial de Conversación", 350), alignment=Qt.AlignCenter)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        inner_widget = QWidget()
        inner_widget.setStyleSheet("background: transparent;")

        self.messages_layout = z_estilos.crear_layout_vertical()
        self.messages_layout.setAlignment(Qt.AlignTop)

        inner_widget.setLayout(self.messages_layout)
        scroll.setWidget(inner_widget)

        spacer = QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.messages_layout.addSpacerItem(spacer)

        layout.addWidget(scroll)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(12)

        text_peticion = z_estilos.crear_line("Escribe un mensaje", 500)

        boton_enviar = QPushButton()
        boton_enviar.setIcon(QIcon("data/send.png"))
        boton_enviar.setIconSize(QSize(22, 22))
        boton_enviar.setFixedSize(42, 42)
        boton_enviar.setToolTip("Enviar")
        boton_enviar.setStyleSheet("""
                    QPushButton {
                        background-color: #00c3ff;
                        color: white;
                        font-size: 18px;
                        font-weight: bold;
                        border-radius: 21px;
                    }
                    QPushButton:hover {
                        background-color: #0084ff;
                    }
                """)
        boton_enviar.clicked.connect(lambda: self.peticion(text_peticion, "texto"))

        boton_audio = QPushButton()
        boton_audio.setIcon(QIcon("data/microfono.png"))
        boton_audio.setIconSize(QSize(22, 22))
        boton_audio.setFixedSize(42, 42)
        boton_audio.setToolTip("Enviar")

        boton_audio.setStyleSheet("""
                    QPushButton {
                        background-color: #ffbb00;
                        color: white;
                        font-size: 16px;
                        border-radius: 21px;
                    }
                    QPushButton:hover {
                        background-color: #ff7b00;
                    }
                """)
        boton_audio.clicked.connect(lambda: self.peticion(text_peticion, "audio"))

        # Layout horizontal para input + botones
        fila_chat = QHBoxLayout()
        fila_chat.setSpacing(6)
        fila_chat.addWidget(text_peticion)
        fila_chat.addWidget(boton_enviar)
        fila_chat.addWidget(boton_audio)

        form.addRow(QLabel("Chat:"), fila_chat)
        layout.addLayout(form)

        boton_atras = z_estilos.crear_boton("Atrás", 250)
        boton_atras.clicked.connect(self.on_click)

        layout.addWidget(boton_atras, alignment=Qt.AlignCenter)

        container.setLayout(layout)
        self.setCentralWidget(container)