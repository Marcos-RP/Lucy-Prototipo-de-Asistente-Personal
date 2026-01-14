# ============================
# Importación de librerías
# ============================

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import speech_recognition as sr
from PyQt5.QtWidgets import (QMainWindow, QLabel, QWidget, QFormLayout, QMessageBox, QScrollArea, QVBoxLayout, QFrame, QSpacerItem, QSizePolicy, QApplication)

import c_a_aplicacion_inicial, d_c_chat, z_estilos



# ============================
# Mensaje inicial de bienvenida
# ============================

MENSAJE_INICIAL = """
<b>Bienvenido a la funcionalidad secundaria de Lucy.</b><br><br>
Lucy permite tener un chat interactivo vía texto o vía voz que te permite hacer 4 acciones básicas:<br><br>
<ul>
    <li><b>Generación de imágenes:</b> Puedes generar imágenes en base a unas instrucciones.</li><br>
    <li><b>Envío de archivos al móvil:</b> Puedes enviar archivos o mensajes a tu móvil a través de la aplicación Telegram.</li><br>
    <li><b>Búsquedas en Google (Fase Beta):</b> Podrás realizar búsquedas en Google.</li><br>
    <li><b>Ejecución de comandos (Fase Beta):</b> Podrás ejecutar ciertos comandos de forma automática en tu ordenador.</li><br>
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
        self.setWindowIcon(QIcon("z_icon.png"))
        self.setStyleSheet(z_estilos.setStyleSheet)
        self.setGeometry(int(width * 0.25), int(height * 0.125), int(width * 0.5), int(height * 0.75))
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
        mensaje.setText(MENSAJE_INICIAL)

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
            #print(f"Tú (Voz): {conversacion}")

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
        layout.addWidget(z_estilos.crear_label("Chatea", 200), alignment=Qt.AlignCenter)

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

        text_peticion = z_estilos.crear_line("Escribe", 300)
        form.addRow(QLabel('Chat: '), text_peticion)

        layout.addLayout(form)

        botones1 = z_estilos.crear_layout_horizontal()

        boton_enviar = z_estilos.crear_boton("Enviar", 250)
        boton_enviar.clicked.connect(lambda: self.peticion(text_peticion, "texto"))
        boton_audio = z_estilos.crear_boton("Audio", 250)
        boton_audio.clicked.connect(lambda: self.peticion(text_peticion, "audio"))

        botones1.addWidget(boton_enviar)
        botones1.addWidget(boton_audio)

        layout.addLayout(botones1)

        boton_atras = z_estilos.crear_boton("Atrás", 250)
        boton_atras.clicked.connect(self.on_click)

        layout.addWidget(boton_atras, alignment=Qt.AlignCenter)

        container.setLayout(layout)
        self.setCentralWidget(container)