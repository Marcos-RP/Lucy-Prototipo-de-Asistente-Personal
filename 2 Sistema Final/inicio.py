# ============================
# Importación de librerías
# ============================

import json, sys
from PyQt5.QtWidgets import QApplication
from src import b_sesion, c_a_aplicacion_inicial, d_a_cripto


# ============================
# Función principal del sistema
# ============================

def main():
    encriptacion = d_a_cripto.Encriptacion()

    try:
        users = encriptacion.cargar_json("data/users_json.enc", context="users_json")
        if not isinstance(users, dict):
            users = {}
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    try:
        sesion = encriptacion.cargar_json("data/sesion_json.enc", context="sesion_json")
        if not isinstance(sesion, dict):
            sesion = {}
    except (FileNotFoundError, json.JSONDecodeError):
        sesion = {}

    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    ancho = screen.size().width()
    alto = screen.size().height()

    if not users or not sesion:
        window = b_sesion.MainWindow(ancho, alto, None, None, encriptacion)
        window.show()

    else:

        encontrado = False
        for user in users.values():
            if user['nombre'] == sesion["usuario"]["nombre"]:

                nombre = user['nombre']
                id = user['id']
                encontrado = True

                window = c_a_aplicacion_inicial.MainWindow(ancho, alto, nombre, id, encriptacion)
                window.show()

        if not encontrado:
            window = b_sesion.MainWindow(ancho, alto, None, None, encriptacion)
            window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()