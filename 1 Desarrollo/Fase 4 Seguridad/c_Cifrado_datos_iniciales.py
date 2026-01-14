# ============================
# Importación de librerías
# ============================

import json, os
import b_Codigo

encriptacion = b_Codigo.Encriptacion()



# =====================================
# Cifrado archivos json
# =====================================

os.makedirs("Datos", exist_ok=True)
archivos_json = [["Datos/sesion","sesion"], ["Datos/users","users"]]

for archivo_json in archivos_json:
    archivo = f"{archivo_json[0]}.json"

    if not os.path.exists(archivo):
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    with open(archivo, "r", encoding="utf-8") as f:
        encriptacion.datos_descifrados[f"Datos_Cifrados/{archivo_json[1]}_json.enc"] = json.load(f)

    encriptacion.guardar_json(f"Datos_Cifrados/{archivo_json[1]}_json.enc", context=f"{archivo_json[1]}_json")
    print(f"\n{archivo_json[1]}_json cifrado exitosamente.")



# =====================================
# Cifrado archivos csv
# =====================================

archivos_csv = [["../Fase 1 Datos/Parte 1/Puntuaciones/DatosPeliculasSeries", "DatosPeliculasSeries"],
                ["../Fase 1 Datos/Parte 3/Puntuaciones/general", "general"],
                ["../Fase 1 Datos/Parte 2/Puntuaciones/200949", "200949"],
                ["../Fase 1 Datos/Parte 2/Puntuaciones/200949_completo","200949_completo"]]


for archivo_csv in archivos_csv:
    with open(f"{archivo_csv[0]}.csv", "rb") as f:
        encriptacion.datos_descifrados[f"Datos_Cifrados/{archivo_csv[1]}_csv.enc"] = f.read()

    encriptacion.guardar_csv(f"Datos_Cifrados/{archivo_csv[1]}_csv.enc", context=f"{archivo_csv[1]}_csv")
    print(f"\n{archivo_csv[1]}_csv cifrado exitosamente.")
