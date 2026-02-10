# ============================
# Importación de librerías
# ============================

import datetime
import pandas as pd
from io import BytesIO

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices, QIntValidator
from PyQt5.QtWidgets import (QMainWindow, QLabel, QWidget, QHBoxLayout, QFormLayout, QComboBox, QMessageBox, QScrollArea, QVBoxLayout, QCheckBox, QGridLayout, QApplication)

from . import c_a_aplicacion_inicial, d_b_titulos, z_estilos



# ============================
# Mensaje inicial de bienvenida
# ============================

MENSAJE_INICIAL = """
<b>Bienvenido a la funcionalidad principal de Lucy.</b><br><br>
En esta pestaña se encuentran cinco acciones principales:<br><br>
<ul>
    <li><b>Recomendaciones:</b> Genera sugerencias de películas o series en función de los títulos evaluados previamente.</li><br>
    <li><b>Predicción:</b> Permite comprobar si una película o serie se ajusta a los hábitos de visualización.</li><br>
    <li><b>Puntuar Película:</b> Permite puntuar películas o series.</li><br>
    <li><b>Ver Puntuaciones:</b> Permite consultar los títulos que han sido evaluados.</li><br>
    <li><b>Búsqueda Personalizada:</b> Permite realizar búsquedas específicas de películas o series según nuevos parámetros.</li><br>
</ul>
"""




# ============================
# Función para abrir enlaces
# ============================

def abrir_url(url):
    QDesktopServices.openUrl(QUrl(url))



# ============================
# Esqueleto del la funcionalidad principal
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
        self.numero1 = 0
        self.numero2 = 0

        self.setWindowTitle("Lucy")
        self.setWindowIcon(QIcon("data/z_icon.png"))
        self.setStyleSheet(z_estilos.setStyleSheet)
        self.setGeometry(int(width * 0.125), int(height * 0.125), int(width * 0.75), int(height * 0.75))
        self.setMinimumSize(800, 500)

        self.general = pd.read_csv(BytesIO(self.encriptacion.cargar_csv("data/general_csv.enc", contexto="general_csv")))
        self.peliculas = pd.read_csv(BytesIO(self.encriptacion.cargar_csv("data/DatosPeliculasSeries_csv.enc", contexto="DatosPeliculasSeries_csv")))
        self.pun_com = pd.read_csv(BytesIO(self.encriptacion.cargar_csv(f"data/{id}_completo_csv.enc", contexto=f"{id}_completo_csv")))
        self.pun = pd.read_csv(BytesIO(self.encriptacion.cargar_csv(f"data/{id}_csv.enc", contexto=f"{id}_csv")))
        self.rows, self.columns = self.pun_com.shape

        self.usuario_peliculas = d_b_titulos.Pred_Rec(self.nombre, self.id, self.encriptacion, self.general, self.peliculas)
        self.usuario_peliculas.juntar_usuarios_comunes()

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
        mensaje.setWindowTitle("Lucy — Panel de Películas y Series")
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
    # Funciones para el cambio de pestaña
    # ============================

    def on_click(self):
        self.close()
        self.window = c_a_aplicacion_inicial.MainWindow(self.width, self.height, self.nombre, self.id, self.encriptacion)
        self.window.show()



    # ============================
    # Función para la gestión de las páginas
    # ============================

    def paginas(self, lista, cajon, tipo):
        if cajon == "recomendaciones":
            if tipo == "avanzar":
                if self.numero1 < ((len(lista) // 5) * 5):
                    self.numero1 += 5
            else:
                self.numero1 -= 5
                if self.numero1 < 1:
                    self.numero1 = 1
            self.initUI2(lista)
        else:
            if tipo == "avanzar":
                if self.numero2 < ((len(lista) // 5) * 5):
                    self.numero2 += 5
            else:
                self.numero2 -= 5
                if self.numero2 < 1:
                    self.numero2 = 1
            self.initUI5(lista)



    # ============================
    # Función realizar las recomendaciones o las búsquedas personalizadas
    # ============================

    def reco_bus(self, tipo, datos=None):

        if tipo == "recomendacion":
            if self.rows > 0:
                rec = self.usuario_peliculas.recomendacion()
            else:
                QMessageBox.warning(self, "Datos insuficientes", "Se requiere al menos una película o serie puntuada.")
                return
        else:
            rec = self.usuario_peliculas.busqueda_concreta(datos)

        contador = 0
        lista = []
        for index, row in rec.iterrows():
            contador += 1
            lista.append([contador, row["Titulo_ES"], row["Año"], row["Puntuacion"], f"https://www.imdb.com/title/{row.get('tid')}/"])

        self.numero1 = 1
        self.initUI2(lista)



    # ============================
    # Función para realizar las predicciones
    # ============================

    def prediccion(self, Titulo_ES, tid):
        if self.rows > 0:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                QApplication.processEvents()
                probabilidad = self.usuario_peliculas.predicciones(tid)
            finally:
                QApplication.restoreOverrideCursor()
        else:
            QMessageBox.warning(self, "Datos insuficientes", "Se requiere al menos una película o serie puntuada.")
            return

        mensaje = QMessageBox(self)
        mensaje.setWindowTitle("Predicción realizada")
        mensaje.setTextFormat(Qt.RichText)

        mensaje.setIcon(QMessageBox.NoIcon)
        mensaje.setText(f"La probabilidad de que la película o serie '{Titulo_ES}' sea de interés es de {probabilidad}%.")
        mensaje.setStandardButtons(QMessageBox.Ok)

        mensaje.exec_()

        self.initUI1()



    # ============================
    # Función buscar un título
    # ============================

    def buscar_titulo(self, datos, tipo_evaluacion):
        titulo = datos[0].text().strip()

        if datos[2] != 0:
            nota = int(datos[2].text().strip())
        else:
            nota = 1

        if datos[1].currentText().strip() == "Pelicula":
            tipo = "movie"
        elif datos[1].currentText().strip() == "Serie":
            tipo = "tvSeries"
        elif datos[1].currentText().strip() == "Mini-Serie":
            tipo = "tvMiniSeries"
        else:
            tipo = "tvSpecial"

        if not titulo or not nota:
            QMessageBox.warning(self, "Datos incompletos", "Complete todos los campos correctamente.")
            return

        puntuacion = round(nota / 10, 1)

        filtro = (
                (self.peliculas["Tipo"] == tipo) &
                (self.peliculas["Titulo_ES"].str.contains(datos[0].text().strip(), case=False, na=False))
        )

        rec = self.peliculas[filtro].sort_values(["Num_Votos", "Puntuacion"], ascending=False).head(10)

        eleccion = rec[["tid", "Titulo_ES", "Puntuacion", "Año"]]

        contador = 0
        lista_evaluaciones = []
        for index, row in eleccion.iterrows():
            contador += 1
            lista_evaluaciones.append([contador, row["Titulo_ES"], row["Año"], row["Puntuacion"], f"https://www.imdb.com/title/{row.get('tid')}/", row["tid"]])

        self.initUI4(lista_evaluaciones, puntuacion, tipo_evaluacion)



    # ============================
    # Función para evaluar un título
    # ============================

    def puntuar(self, tid, Titulo_ES, nota):

        informacion = self.peliculas[(self.peliculas["tid"] == tid) & (self.peliculas["Titulo_ES"] == Titulo_ES)].iloc[0]
        hoy = datetime.datetime.today().strftime("%Y-%m-%d")

        nueva_fila = {
            "userId": self.id,
            "tid": informacion["tid"],
            "Fecha": hoy,
            "Tipo": informacion["Tipo"],
            "Titulo": informacion["Titulo"],
            "Titulo_ES": informacion["Titulo_ES"],
            "Año": informacion["Año"],
            "Mi Nota": nota,
            "Duracion": informacion["Duracion"],
            "Generos": informacion["Generos"],
            "Puntuacion": informacion["Puntuacion"],
            "Num_Votos": informacion["Num_Votos"],
            "Actores": informacion["Actores"],
            "Directores": informacion["Directores"],
            "Idioma": informacion["Idioma"]
        }

        nueva_fila2 = {
            "userId": self.id,
            "Mi Nota": nota,
            "tid": informacion["tid"],
        }

        nota_nueva = round(nueva_fila2["Mi Nota"])
        nota_nueva = max(1, min(10, nota_nueva))
        nueva_fila2["Mi Nota"] = nota_nueva

        self.pun_com = pd.concat([self.pun_com, pd.DataFrame([nueva_fila])])
        self.encriptacion.datos_descifrados[f"data/{self.id}_completo_csv.enc"]= self.pun_com.to_csv(index=True).encode()
        self.encriptacion.guardar_csv(f"data/{self.id}_completo_csv.enc", contexto=f"{self.id}_completo_csv")

        self.pun = pd.concat([self.pun, pd.DataFrame([nueva_fila2])])
        self.encriptacion.datos_descifrados[f"data/{self.id}_csv.enc"] = self.pun.to_csv(index=False).encode()
        self.encriptacion.guardar_csv(f"data/{self.id}_csv.enc", contexto=f"{self.id}_csv")

        self.rows, self.columns = self.pun_com.shape

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            QApplication.processEvents()
            self.usuario_peliculas.juntar_usuarios_comunes()
        finally:
            QApplication.restoreOverrideCursor()

        mensaje = QMessageBox(self)
        mensaje.setWindowTitle("Puntuación Añadida")
        mensaje.setTextFormat(Qt.RichText)

        mensaje.setIcon(QMessageBox.NoIcon)
        mensaje.setText(f"La película o serie '{Titulo_ES}' ha sido calificada correctamente con una puntuación de {nota}.")
        mensaje.setStandardButtons(QMessageBox.Ok)

        mensaje.exec_()

        self.initUI1()



    # ============================
    # Función para procesar los datos de la búsqueda personalizada
    # ============================

    def datos_busqueda(self, botone, datos, botones, botoness):
        ano_minimo = datos[0].text().strip()
        ano_maximo = datos[1].text().strip()
        nota = datos[2].text().strip()

        tipos = []

        if botone[0].isChecked():
            tipos.append("movie")
        if botone[1].isChecked():
            tipos.append("tvSeries")
        if botone[2].isChecked():
            tipos.append("tvMiniSeries")
        if botone[3].isChecked():
            tipos.append("tvSpecial")

        sigeneros = []

        if botones[0].isChecked():
            sigeneros.append("Adventure")
        if botones[1].isChecked():
            sigeneros.append("Action")
        if botones[2].isChecked():
            sigeneros.append("Sci-Fi")
        if botones[3].isChecked():
            sigeneros.append("Mystery")
        if botones[4].isChecked():
            sigeneros.append("Animation")
        if botones[5].isChecked():
            sigeneros.append("Family")
        if botones[6].isChecked():
            sigeneros.append("Comedy")
        if botones[7].isChecked():
            sigeneros.append("Romance")
        if botones[8].isChecked():
            sigeneros.append("Drama")
        if botones[9].isChecked():
            sigeneros.append("Crime")
        if botones[10].isChecked():
            sigeneros.append("Western")
        if botones[11].isChecked():
            sigeneros.append("Biography")
            sigeneros.append("History")
        if botones[12].isChecked():
            sigeneros.append("Documentary")
        if botones[13].isChecked():
            sigeneros.append("Thriller")
        if botones[14].isChecked():
            sigeneros.append("Fantasy")
        if botones[15].isChecked():
            sigeneros.append("Musical")

        nogeneros = []

        if botoness[0].isChecked():
            nogeneros.append("Adventure")
        if botoness[1].isChecked():
            nogeneros.append("Action")
        if botoness[2].isChecked():
            nogeneros.append("Sci-Fi")
        if botoness[3].isChecked():
            nogeneros.append("Mystery")
        if botoness[4].isChecked():
            nogeneros.append("Animation")
        if botoness[5].isChecked():
            nogeneros.append("Family")
        if botoness[6].isChecked():
            nogeneros.append("Comedy")
        if botoness[7].isChecked():
            nogeneros.append("Romance")
        if botoness[8].isChecked():
            nogeneros.append("Drama")
        if botoness[9].isChecked():
            nogeneros.append("Crime")
        if botoness[10].isChecked():
            nogeneros.append("Western")
        if botoness[11].isChecked():
            nogeneros.append("Biography")
            nogeneros.append("History")
        if botoness[12].isChecked():
            nogeneros.append("Documentary")
        if botoness[13].isChecked():
            nogeneros.append("Thriller")
        if botoness[14].isChecked():
            nogeneros.append("Fantasy")
        if botoness[15].isChecked():
            nogeneros.append("Musical")


        if not ano_minimo or not nota or not tipos or not sigeneros or not nogeneros:
            QMessageBox.warning(self, "Datos incompletos", "Complete todos los campos correctamente.")
            return

        datos = {}

        ano_minimo = int(ano_minimo)
        nota = int(nota)

        if not (1900 <= ano_minimo <= datetime.datetime.now().year):
            QMessageBox.warning(self,"Datos incompletos",f"Introduzca un año mínimo de estreno entre 1900 y {datetime.datetime.now().year}.")
            return

        if not ano_maximo:
            datos["ano_maximo"] = datetime.datetime.now().year
        else:
            ano_maximo = int(ano_maximo)

            if not (1900 <= ano_maximo <= datetime.datetime.now().year):
                QMessageBox.warning(self,"Datos incompletos",f"Introduzca un año máximo de estreno entre 1900 y {datetime.datetime.now().year}.")
                return

            if ano_minimo > ano_maximo:
                QMessageBox.warning(self,"Datos incompletos","El año mínimo no puede ser mayor que el año máximo.")
                return
            datos["ano_maximo"] = ano_maximo

        if not (1 <= nota <= 100):
            QMessageBox.warning(self,"Datos incompletos","Introduzca una puntuación mínima entre 1 y 100.")
            return

        datos["tipos"] = tipos
        datos["ano_minimo"] = ano_minimo
        datos["puntuacion_minima"] = round(nota / 10, 1)
        datos["sigeneros"] = sigeneros
        datos["nogeneros"] = nogeneros

        self.reco_bus("busqueda", datos)



    # ============================
    # Interfaz gráfica base de la funcional principal
    # ============================

    def initUI1(self):
        container = QWidget()
        layout = z_estilos.crear_layout_vertical()
        layout.addWidget(z_estilos.crear_label("Seleccione la acción a realizar", 650), alignment=Qt.AlignCenter)

        botones1 = z_estilos.crear_layout_grid()

        btn_rec = z_estilos.crear_boton("Recomendaciones", 350)
        btn_rec.clicked.connect(lambda: self.reco_bus("recomendacion"))
        btn_pre = z_estilos.crear_boton("Predicción", 350)
        btn_pre.clicked.connect(lambda: self.initUI3("prediccion"))
        btn_puntuar = z_estilos.crear_boton("Realizar Puntuación", 350)
        btn_puntuar.clicked.connect(lambda: self.initUI3("puntuar"))
        btn_ver = z_estilos.crear_boton("Ver Puntuaciones", 350)
        btn_ver.clicked.connect(lambda: self.initUI5(self.pun_com))
        btn_busqueda = z_estilos.crear_boton("Búsqueda Personalizada", 350)
        btn_busqueda.clicked.connect(self.initUI6)

        botones1.addWidget(btn_rec, 0, 0)
        botones1.addWidget(btn_pre, 0, 1)
        botones1.addWidget(btn_puntuar, 1, 0)
        botones1.addWidget(btn_ver, 1, 1)

        layout.addLayout(botones1)
        layout.addWidget(btn_busqueda, alignment=Qt.AlignCenter)

        boton_atras = z_estilos.crear_boton("Atrás", 250)
        boton_atras.clicked.connect(self.on_click)

        layout.addWidget(boton_atras, alignment=Qt.AlignCenter)

        container.setLayout(layout)
        self.setCentralWidget(container)



    # ============================
    # Interfaz gráfica de las recomendaciones realizadas
    # ============================

    def initUI2(self, lista_recomendacion):
        container = QWidget()
        layout = z_estilos.crear_layout_vertical()
        layout.addWidget(z_estilos.crear_label("Recomendaciones realizadas", 650), alignment=Qt.AlignCenter)

        for i in lista_recomendacion:
            if (i[0] >= self.numero1) and (i[0] < self.numero1 + 5):
                layout2 = QHBoxLayout()

                label = z_estilos.crear_label(f"Recomendación {i[0]}: {i[1]} -- {i[2]} ({i[3]})", 800)
                button = z_estilos.crear_boton("Más información", 250)
                button.clicked.connect(lambda checked, url=i[4]: abrir_url(url))

                layout2.addWidget(label)
                layout2.addWidget(button)
                layout.addLayout(layout2)

        botones = z_estilos.crear_layout_horizontal()

        boton1 = z_estilos.crear_boton("Retroceder", 250)
        boton1.clicked.connect(lambda: self.paginas(lista_recomendacion, "recomendaciones", "retroceder"))
        boton2 = z_estilos.crear_boton("Avanzar", 250)
        boton2.clicked.connect(lambda: self.paginas(lista_recomendacion, "recomendaciones", "avanzar"))

        botones.addWidget(boton1)
        botones.addWidget(boton2)

        layout.addLayout(botones)

        boton3 = z_estilos.crear_boton("Atrás", 250)
        boton3.clicked.connect(self.initUI1)

        layout.addSpacing(9)
        layout.addWidget(boton3, alignment=Qt.AlignHCenter)

        container.setLayout(layout)
        self.setCentralWidget(container)



    # ============================
    # Interfaz gráfica para la evaluación o predicción de un título (Parte 1)
    # ============================

    def initUI3(self, tipo):

        container = QWidget()
        container.setStyleSheet(z_estilos.form_style)
        layout = z_estilos.crear_layout_vertical()
        if tipo == "puntuar":
            layout.addWidget(z_estilos.crear_label("Introduzca el título, el tipo de contenido a evaluar y la puntuación", 650),alignment=Qt.AlignCenter)
        else:
            layout.addWidget(z_estilos.crear_label("Introduzca el título y el tipo de contenido para realizar la predicción", 650),alignment=Qt.AlignCenter)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(12)

        text_nombre = z_estilos.crear_line("Introduzca el título", 450)

        combo = QComboBox()
        combo.addItems(["Película", "Serie", "Mini-serie", "Especiales de TV"])
        combo.setFixedWidth(450)
        combo.setStyleSheet(z_estilos.combo_style)

        form.addRow(QLabel('Título:'), text_nombre)

        text_nota = 0
        if tipo == "puntuar":
            text_nota = z_estilos.crear_line("Introduzca la puntuación entre 1 y 100", 450, validator=QIntValidator())
            form.addRow(QLabel('Puntuación:'), text_nota)

        form.addRow(QLabel('Tipo: '), combo)

        layout.addLayout(form)

        botones = z_estilos.crear_layout_horizontal()

        boton_atras = z_estilos.crear_boton("Atrás", 250)
        boton_atras.clicked.connect(self.initUI1)
        boton_enviar = z_estilos.crear_boton("Evaluar", 250)
        boton_enviar.clicked.connect(lambda: self.buscar_titulo([text_nombre, combo, text_nota], tipo))


        botones.addWidget(boton_atras)
        botones.addWidget(boton_enviar)

        layout.addLayout(botones)

        container.setLayout(layout)
        self.setCentralWidget(container)



    # ============================
    # Interfaz gráfica para la evaluación o predicción de un título (Parte 2)
    # ============================

    def initUI4(self, lista_evaluaciones, nota, tipo):

        container = QWidget()
        layout = z_estilos.crear_layout_vertical()
        layout.addWidget(z_estilos.crear_label("Seleccione la película o serie correcta", 650), alignment=Qt.AlignCenter)

        if lista_evaluaciones:
            for i in lista_evaluaciones:
                botones = QHBoxLayout()

                label = z_estilos.crear_label(f"Opción {i[0]}: {i[1]} -- {i[2]} ({i[3]})", 800)

                button1 = z_estilos.crear_boton("Seleccionar", 250)
                if tipo == "puntuar":
                    button1.clicked.connect(lambda checked=False, tid=i[5], Titulo_ES=i[1]: self.puntuar(tid, Titulo_ES, nota))
                else:
                    button1.clicked.connect(lambda checked=False, tid=i[5], Titulo_ES=i[1]: self.prediccion(Titulo_ES, tid))

                button2 = z_estilos.crear_boton("Más información", 250)
                button2.clicked.connect(lambda checked, url=i[4]: abrir_url(url))

                botones.addWidget(label)
                botones.addWidget(button1)
                botones.addWidget(button2)
                layout.addLayout(botones)
        else:
            label = z_estilos.crear_label("No ha habido coincidencias", 350)
            layout.addWidget(label)

        boton = z_estilos.crear_boton("Atrás", 250)
        boton.clicked.connect(lambda: self.initUI3(tipo))

        layout.addSpacing(9)
        layout.addWidget(boton, alignment=Qt.AlignHCenter)

        container.setLayout(layout)
        self.setCentralWidget(container)



    # ============================
    # Interfaz gráfica para ver los títulos evaluados
    # ============================

    def initUI5(self, lista_puntuadas):
        container = QWidget()
        layout = z_estilos.crear_layout_vertical()
        layout.addWidget(z_estilos.crear_label("Puntuaciones realizadas", 650), alignment=Qt.AlignCenter)

        for idx, row in lista_puntuadas.iterrows():
            if self.numero2 <= idx < self.numero2 + 5:
                label = z_estilos.crear_label(f'{row["Titulo_ES"]} ({row["Año"]}) -- Nota: {row["Mi Nota"]} -- ({row["Fecha"]})', 800)
                layout.addWidget(label)

        botones = z_estilos.crear_layout_horizontal()

        boton1 = z_estilos.crear_boton("Retroceder", 250)
        boton1.clicked.connect(lambda: self.paginas(lista_puntuadas, "puntuadas", "retroceder"))
        boton2 = z_estilos.crear_boton("Avanzar", 250)
        boton2.clicked.connect(lambda: self.paginas(lista_puntuadas, "puntuadas", "avanzar"))

        botones.addWidget(boton1)
        botones.addWidget(boton2)

        layout.addLayout(botones)

        boton3 = z_estilos.crear_boton("Atrás", 250)
        boton3.clicked.connect(self.initUI1)

        layout.addSpacing(9)
        layout.addWidget(boton3, alignment=Qt.AlignHCenter)

        container.setLayout(layout)
        self.setCentralWidget(container)



    # ============================
    # Interfaz gráfica para las búsquedas personalizadas
    # ============================

    def initUI6(self):

        container = QWidget()
        container.setStyleSheet(z_estilos.form_style)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        inner_widget = QWidget()
        layout = z_estilos.crear_layout_vertical()
        inner_widget.setLayout(layout)
        scroll.setWidget(inner_widget)

        layout.addWidget(z_estilos.crear_label("Seleccione el tipo de título de su preferencia", 650), alignment=Qt.AlignCenter)
        layout.addSpacing(9)

        tipos_texto = ["Películas", "Series", "Mini-Series", "Especiales de TV"]
        tipos_checks = []

        tipos = QHBoxLayout()
        for texto in tipos_texto:
            check_box = QCheckBox(texto)
            check_box.setStyleSheet(z_estilos.checkbox_style)
            tipos_checks.append(check_box)
            tipos.addWidget(check_box)

        layout.addLayout(tipos)
        layout.addSpacing(9)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(12)

        ano_actual = datetime.datetime.now().year

        text_ano_min = z_estilos.crear_line(f"Introduzca un año entre 1900 y {ano_actual}", 450, validator=QIntValidator())
        text_ano_max = z_estilos.crear_line(f"Introduzca un año entre 1900 y, por defecto, {ano_actual}", 450, validator=QIntValidator())
        text_puntuacion = z_estilos.crear_line("Introduzca una puntuación entre 1 y 100", 450, validator=QIntValidator(1, 100))

        form.addRow("Año mínimo de estreno:", text_ano_min)
        form.addRow("Año máximo de estreno:", text_ano_max)
        form.addRow("Puntuación mínima en IMDB:", text_puntuacion)

        layout.addLayout(form)
        layout.addSpacing(9)

        def crear_grid_generos(titulo):
            layout.addWidget(
                z_estilos.crear_label(titulo, 650),
                alignment=Qt.AlignCenter
            )

            generos = [
                "Aventura", "Acción", "Sci-Fi", "Misterio",
                "Animación", "Familiar", "Comedia", "Romance",
                "Drama", "Crimen", "Western", "Biográfica / Histórica",
                "Documental", "Thriller", "Fantasia", "Musical"
            ]

            grid = QGridLayout()
            checks = []

            for i, genero in enumerate(generos):
                chk = QCheckBox(genero)
                chk.setStyleSheet(z_estilos.checkbox_style)
                checks.append(chk)
                grid.addWidget(chk, i // 4, i % 4)

            layout.addLayout(grid)
            layout.addSpacing(9)
            return checks

        generos_si = crear_grid_generos("Seleccione los géneros que SON de su preferencia")
        generos_no = crear_grid_generos("Seleccione los géneros que NO SON de su preferencia")

        botones = z_estilos.crear_layout_horizontal()

        boton_atras = z_estilos.crear_boton("Atrás", 250)
        boton_atras.clicked.connect(self.initUI1)
        boton_enviar = z_estilos.crear_boton("Siguiente", 250)
        boton_enviar.clicked.connect(lambda: self.datos_busqueda(tipos_checks, [text_ano_min, text_ano_max, text_puntuacion], generos_si, generos_no))

        botones.addWidget(boton_atras)
        botones.addWidget(boton_enviar)

        layout.addLayout(botones)
        layout.addSpacing(9)

        main_layout = QVBoxLayout(container)
        main_layout.addWidget(scroll)

        self.setCentralWidget(container)