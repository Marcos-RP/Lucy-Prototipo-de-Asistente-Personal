# ============================
# Importación de librerías
# ============================

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication

from . import b_sesion, c_b_titulos, c_c_chat, z_estilos



# ============================
# Esqueleto del inicial sistema
# ============================

class MainWindow(QMainWindow):

    def __init__(self, width, height, nombre, id, encriptacion):

        super().__init__()

        self.width = width
        self.height = height
        self.nombre = nombre
        self.id = id
        self.encriptacion = encriptacion

        self.setWindowTitle("Lucy")
        self.setWindowIcon(QIcon("data/z_icon.png"))
        self.setStyleSheet(z_estilos.setStyleSheet)
        self.setGeometry(int(width * 0.25), int(height * 0.125), int(width * 0.5), int(height * 0.75))
        self.setMinimumSize(800, 500)

        #print("Inicio sesión:", self.nombre)
        self.initUI1()



    # ============================
    # Funciones para el cambio de pestaña
    # ============================

    def cambiar_ventana(self, ventana):
        self.window = ventana(self.width, self.height, self.nombre, self.id, self.encriptacion)
        self.window.show()
        self.close()


    def on_click1(self):
        self.encriptacion.datos_descifrados["data/sesion_json.enc"]["usuario"] = {
            'nombre': None
        }

        self.encriptacion.guardar_json("data/sesion_json.enc", contexto="sesion_json")

        self.cambiar_ventana(b_sesion.MainWindow)


    def chat(self):
        self.cambiar_ventana(c_c_chat.MainWindow)


    def peliculas(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            QApplication.processEvents()
            self.cambiar_ventana(c_b_titulos.MainWindow)
        finally:
            QApplication.restoreOverrideCursor()



    # ============================
    # Interfaz gráfica de la selección de que realizar
    # ============================

    def initUI1(self):
        container = QWidget()
        layout = z_estilos.crear_layout_vertical()
        layout.addWidget(z_estilos.crear_label("Seleciona que quieres hacer", 450), alignment=Qt.AlignCenter)

        botones = z_estilos.crear_layout_grid()

        btn_titulos = z_estilos.crear_boton("Películas", 250)
        btn_titulos.clicked.connect(self.peliculas)
        btn_chat = z_estilos.crear_boton("Chat", 250)
        btn_chat.clicked.connect(self.chat)
        btn_sesion = z_estilos.crear_boton("Cambio Sesión", 250)
        btn_sesion.clicked.connect(self.on_click1)
        boton_cerrar = z_estilos.crear_boton("Cerrar", 250)
        boton_cerrar.clicked.connect(self.close)

        botones.addWidget(btn_titulos, 0, 0)
        botones.addWidget(btn_chat, 1, 0)
        botones.addWidget(btn_sesion, 0, 1)
        botones.addWidget(boton_cerrar, 1, 1)

        layout.addLayout(botones)

        container.setLayout(layout)
        self.setCentralWidget(container)