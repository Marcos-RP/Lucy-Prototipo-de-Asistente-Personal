# =====================================
# Importación de librerías
# =====================================

import pandas as pd
import b_Codigo



# =====================================
# Importación de datos
# =====================================
df_peliculas = pd.read_csv("data/DatosPeliculasSeries.csv")
df_ratings = pd.read_csv("data/ratings.csv")
df_links = pd.read_csv("data/links.csv")

print("Lectura de archivos")


# =====================================
# Creación base de datos general
# =====================================

df = pd.merge(df_ratings, df_links, on='movieId', how='left')

df = df[["userId", "rating", "timestamp", "imdbId"]].rename(columns={'rating': 'Mi Nota', 'timestamp': 'Fecha', 'imdbId': 'tid'})

df['tid'] = 'tt' + df['tid'].astype(str).str.zfill(7)

df = df[df['tid'].isin(df_peliculas['tid'])].copy()

df["Mi Nota"] *= 2

df["Mi Nota"] = (
    df["Mi Nota"]
        .round()
        .clip(1, 10)
        .astype(int)
)

df['Fecha'] = pd.to_datetime(df['Fecha'], unit='s').dt.date

print("general creado")

# =====================================
# Guardado de las bases de datos iniciales
# =====================================

df_inicial = df.copy().drop(columns=["Fecha"])
df_inicial.to_csv("data/general.csv", index=False)

print("Guardado general.csv")

# =====================================
# Cifrado archivos general.csv
# =====================================

encriptacion = b_Codigo.Encriptacion()


with open("data/general.csv", "rb") as f:
    encriptacion.datos_descifrados["../data/general_csv.enc"] = f.read()

encriptacion.guardar_csv("../data/general_csv.enc", context="general_csv")
print("\ngeneral_csv cifrado exitosamente.")