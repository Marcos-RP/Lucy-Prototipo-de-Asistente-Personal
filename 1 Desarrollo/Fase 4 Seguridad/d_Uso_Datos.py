# ============================
# Importación de librerías
# ============================

import csv, io
from argon2 import PasswordHasher
import b_Codigo



# ============================
# Prueba de uso archivos .json
# ============================

encriptacion = b_Codigo.Encriptacion()

datos = encriptacion.cargar_json("Datos_Cifrados/users_json.enc", "users_json")

datos["200949"] = {
    "user_id": "Marcos",
    "password_hash": PasswordHasher().hash("1234")
}

PasswordHasher().verify(datos["200949"]["password_hash"], "1234")

encriptacion.guardar_json("Datos_Cifrados/users_json.enc", "users_json")

print(datos)
print("\nUsuario agregado exitosamente.")



# ============================
# Prueba de uso archivos .csv
# ============================

archivo_csv = "200949"
datos = encriptacion.cargar_csv(f"Datos_Cifrados/{archivo_csv}_csv.enc", f"{archivo_csv}_csv").decode("utf-8")

datos = list(csv.DictReader(io.StringIO(datos)))

for row in datos:
    if row["tid"] == "tt9999999":
        print(row["Mi Nota"])


datos.append({"userId": "200949", "tid": "tt9999999", "Mi Nota": "10"})

columnas = ["userId", "tid", "Mi Nota"]

datos_finales = io.StringIO()
writer = csv.DictWriter(datos_finales, fieldnames=columnas)
writer.writeheader()
writer.writerows(datos)

encriptacion.datos_descifrados[f"Datos_Cifrados/{archivo_csv}_csv.enc"] = datos_finales.getvalue().encode("utf-8")
encriptacion.guardar_csv(f"Datos_Cifrados/{archivo_csv}_csv.enc", context=f"{archivo_csv}_csv")

print("\nDatos agregado exitosamente.")

