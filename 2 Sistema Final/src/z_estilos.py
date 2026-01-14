# ============================
# Importación de librerías
# ============================

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit)



# ============================
# Importación de librerías
# ============================

def crear_layout_vertical(spacing=20, margins=(40,40,40,40)):
    layout = QVBoxLayout()
    layout.setSpacing(spacing)
    layout.setContentsMargins(*margins)
    layout.setAlignment(Qt.AlignCenter)
    return layout

def crear_layout_horizontal(spacing=25, margins=(40,40,40,40)):
    layout = QHBoxLayout()
    layout.setSpacing(spacing)
    layout.setContentsMargins(*margins)
    layout.setAlignment(Qt.AlignCenter)
    return layout

def crear_layout_grid(spacing=25, margins=(40,40,40,40)):
    layout = QGridLayout()
    layout.setSpacing(spacing)
    layout.setContentsMargins(*margins)
    layout.setAlignment(Qt.AlignCenter)
    return layout

def crear_boton(texto, ancho):
    btn = QPushButton(texto)
    btn.setFixedWidth(ancho)
    btn.setStyleSheet(button_style)
    return btn

def crear_label(texto, ancho):
    label = QLabel(texto)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet(label_style)
    label.setFixedWidth(ancho)
    return label

def crear_line(texto, ancho, password=False, validator=None):
    line = QLineEdit()
    line.setPlaceholderText(texto)
    line.setClearButtonEnabled(True)
    line.setFixedWidth(ancho)
    if password:
        line.setEchoMode(QLineEdit.Password)
    if validator:
        line.setValidator(validator)
    return line



# ============================
# Importación de librerías
# ============================

setStyleSheet = (
    "background: qlineargradient("
    "x1:0, y1:0, x2:1, y2:1,"
    "stop:0 #F2E9D8, "
    "stop:1 #D6C4B5"
    ");"
)


button_style = """
QPushButton {
    background-color: #C7A78B;
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #B08972;
}
QPushButton:pressed {
    background-color: #8E6D59;
}
"""


label_style = (
    "padding: 6px 14px;"
    "border-radius: 5px;"
    "font-size: 14px;"
    "min-height: 25px;"
    "color:  #333;"
    "font-weight: bold;"
)


combo_style = ("font-size: 14px;"
               "padding: 8px 10px;"
               " border: 2px solid #D6C9BE;"
               "border-radius: 6px;"
               "background: #FAFAFA;"
               "color: #000;"
               )


form_style = """
QLabel {
    padding: 6px 14px;
    border-radius: 5px;
    font-size: 14px;    
    min-height: 25px;
    color: #333;
    font-weight: bold;
}

QLineEdit {
    font-size: 14px;
    min-height: 24px;
    padding: 8px 10px;
    border: 2px solid #D6C9BE;
    border-radius: 6px;
    background: #FAFAFA;
    color: #000;
}

QLineEdit:focus {
    border: 2px solid #B08972;
    background: #FFFFFF;
}

QLineEdit:hover {
    border: 2px solid #C7A78B;
}


QFormLayout {
    margin-top: 10px;
}
"""

checkbox_style = ("padding: 6px 14px;"
                  "border-radius: 5px;"
                  "font-size: 14px;"
                  "color: #333;")