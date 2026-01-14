# =====================================
# Importación de librerías
# =====================================

import random
import pandas as pd
from datetime import datetime, timedelta



# =====================================
# Selección de géneros que no gustan
# =====================================

df = pd.read_csv('../Parte 1/Puntuaciones/DatosPeliculasSeries.csv')

terror = df['Generos'].str.contains('Horror', case=False) | df['Generos'].str.contains('Thriller', case=False)
autor = (df['Generos'].str.contains('Drama') | df['Generos'].str.contains('History')) & (~df['Generos'].str.contains('Action')) & (~df['Generos'].str.contains('Sci-Fi'))



# =====================================
# Generación de 200 muestras de títulos malos
# =====================================

malas = df[(df['Generos'].str.contains('Romance') & (df['Año'] < 1990)) | (autor & (df['Año'] < 1990))]
if len(malas) < 200:
    malas = df[(df['Generos'].str.contains('Romance'))]
lista_malas = malas.sample(n=200, replace=True).to_dict('records')



# =====================================
# Generación de 200 muestras de títulos no tan malos
# =====================================

no_tan_malas = df[terror | ((df['Generos'].str.contains('Romance')) & ~(df['Año'] < 1990)) | (autor & ~(df['Año'] < 1990))]
no_tan_malas = no_tan_malas[~no_tan_malas['tid'].isin([x['tid'] for x in lista_malas])]
lista_no_tan_malas = no_tan_malas.sample(n=200, replace=True).to_dict('records')



# =====================================
# Generación de 200 muestras de títulos medios
# =====================================

medias = df[(df['Generos'].str.contains('Action') & (df['Año'] < 1990)) | (df['Generos'].str.contains('Comedy')) | (terror & (df['Año'] >= 2010))]
repetidos = [x['tid'] for x in lista_malas] + [x['tid'] for x in lista_no_tan_malas]
medias = medias[~medias['tid'].isin(repetidos)]
lista_medias = medias.sample(n=200, replace=True).to_dict('records')



# =====================================
# Impresión de las 600 muestras
# =====================================

def fecha_random_2025():
    inicio = datetime(2025, 1, 1)
    fecha = inicio + timedelta(days=random.randint(0, 365))
    return fecha.strftime("%Y-%m-%d")

for item in lista_malas:
    print(f"{fecha_random_2025()},{item['Titulo_ES']},{int(item['Año'])},{random.choice([1, 2])}")

for item in lista_no_tan_malas:
    print(f"{fecha_random_2025()},{item['Titulo_ES']},{int(item['Año'])},{random.choice([3, 4])}")

for item in lista_medias:
    print(f"{fecha_random_2025()},{item['Titulo_ES']},{int(item['Año'])},{random.choice([5, 6])}")