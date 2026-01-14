# =====================================
# Importación de librerías
# =====================================

import pandas as pd
import b_Codigo



# =====================================
# Importación de datos
# =====================================

print("Lectura name")
df_name = pd.read_csv('data/name.basics.tsv.gz', sep='\t', na_values="\\N", low_memory=False, compression="gzip")
print("Lectura akas")
df_akas = pd.read_csv('data/title.akas.tsv.gz', sep='\t', na_values="\\N", low_memory=False, compression="gzip")
print("Lectura basics")
df_basics = pd.read_csv('data/title.basics.tsv.gz', sep='\t', na_values="\\N", low_memory=False, compression="gzip")
print("Lectura crew")
df_crew = pd.read_csv('data/title.crew.tsv.gz', sep='\t', na_values="\\N", low_memory=False, compression="gzip")
print("Lectura principals")
df_principals = pd.read_csv('data/title.principals.tsv.gz', sep='\t', na_values="\\N", low_memory=False, compression="gzip")
print("Lectura ratings")
df_ratings = pd.read_csv('data/title.ratings.tsv.gz', sep='\t', na_values="\\N", low_memory=False, compression="gzip")



# =====================================
# Selección y renombrado de columnas
# =====================================

print("Seleccionando columnas relevantes y renombrando...")

df_ename = df_name[['nconst', 'primaryName']].rename(columns={'nconst': 'nid', 'primaryName': 'Nombre'})
df_eakas = df_akas[['titleId', 'title', 'region', 'language']].rename(columns={'titleId': 'tid', 'title': 'Titulo', 'region': 'Region', 'language': 'Idioma'})
df_ebasics = df_basics[['tconst', 'titleType', 'primaryTitle', 'startYear', 'runtimeMinutes', 'genres']].rename(
    columns={
        'tconst': 'tid',
        'titleType': 'Tipo',
        'primaryTitle': 'Titulo',
        'startYear': 'Año',
        'runtimeMinutes': 'Duracion',
        'genres': 'Generos'
    }
)
df_ecrew = df_crew[['tconst', 'directors']].rename(columns={'tconst': 'tid', 'directors': 'Directores'})
df_eprincipals = df_principals[['tconst', 'nconst', 'category']].rename(columns={'tconst': 'tid', 'nconst': 'nid', 'category': 'Categoria'})
df_eratings = df_ratings[['tconst', 'averageRating', 'numVotes']].rename(columns={'tconst': 'tid', 'averageRating': 'Puntuacion', 'numVotes': 'Num_Votos'})



# =====================================
# Filtrado inicial
# =====================================

print("Filtrando por tipo de título...")
df_ebasics = df_ebasics[df_ebasics["Tipo"].isin(["movie", "tvMovie", "tvSeries", "tvMiniSeries","tvSpecial"])].copy()
df_ebasics = df_ebasics.replace("tvMovie", "movie")

df_eprincipals = df_eprincipals[df_eprincipals["Categoria"].isin(["actor", "actress"])].copy()



# =====================================
# Conversión de datos numéricos
# =====================================

print("Convirtiendo tipos...")
if "Año" in df_ebasics.columns:
    df_ebasics["Año"] = pd.to_numeric(df_ebasics["Año"], errors="coerce", downcast="integer")
if "Duracion" in df_ebasics.columns:
    df_ebasics["Duracion"] = pd.to_numeric(df_ebasics["Duracion"], errors="coerce", downcast="integer")
if "Puntuacion" in df_ratings.columns:
    df_eratings["Puntuacion"] = pd.to_numeric(df_eratings["Puntuacion"], errors="coerce", downcast="float")
if "Num_Votos" in df_eratings.columns:
    df_eratings["Num_Votos"] = pd.to_numeric(df_eratings["Num_Votos"], errors="coerce", downcast="integer")



# =====================================
# Creación bases intermedias (actores / directores)
# =====================================

print("Creación database actores")
df_actores = pd.merge(df_eprincipals, df_ename, on='nid', how='outer')

print("Creación database directores")
df_ecrew['Directores'] = df_ecrew['Directores'].str.split(',')
df_ecrew['Directores'] = df_ecrew['Directores'].apply(lambda x: [i.strip() for i in x] if isinstance(x, list) else x)
df_ecrew_separado = df_ecrew.explode('Directores')

df_directores = pd.merge(df_ecrew_separado, df_ename, left_on='Directores', right_on='nid', how='outer')


print("Creación database actores agrupado")
df_actores_agrupado = (df_actores.groupby(['tid']).agg({'Nombre': lambda x: list(set(x))}))

print("Creación database directores agrupado")
df_directores_agrupado = (df_directores.groupby(['tid']).agg({'Nombre': lambda x: list(set(x))}))

print("Renombrado databases actores y directores agrupado")

df_actores_agrupado = df_actores_agrupado.rename(columns={"Nombre": "Actores"})
df_directores_agrupado = df_directores_agrupado.rename(columns={"Nombre": "Directores"})



# =====================================
# Creación bases intermedias (titulos en español)
# =====================================

print("Agrupando idiomas por 'tid' ...")
df_eakas_agrupado = (df_eakas.groupby('tid', as_index=False).agg({'Idioma': lambda x: list(set(x))}))

print("Filtrando títulos con región 'ES' ...")
df_eakas_es = df_eakas[df_eakas['Region'] == 'ES'][['tid', 'Titulo']]

print("Combinando títulos ES con los idiomas agrupados ...")
df_eakas_es_agrupado = pd.merge(df_eakas_es, df_eakas_agrupado, on='tid', how='right')

print("Rellenando títulos sin 'ES' con el título genérico ...")
titulo_generico = df_eakas.groupby('tid')['Titulo'].first()
df_eakas_es_agrupado['Titulo_ES'] = df_eakas_es_agrupado['Titulo'].fillna(df_eakas_es_agrupado['tid'].map(titulo_generico))



# =====================================
# Construcción progresiva de la base de datos
# =====================================

print("Creación database1 (basics + ratings)")
df_1 = pd.merge(df_ebasics, df_eratings, on='tid', how='left')

print("Creación database2 (actores agrupado + directores agrupado)")
df_2 = pd.merge(df_actores_agrupado, df_directores_agrupado, on='tid', how='left')

print("Creación database final (database1 + database2)")
df_3 = pd.merge(df_1, df_2, on='tid', how='left')

print("Creación database final + título español")
df_inicial = pd.merge(df_3, df_eakas_es_agrupado[['tid','Titulo_ES', 'Idioma']], on="tid", how="left")



# =====================================
# Filtrado y comprobación final
# =====================================

df_final = df_inicial[['tid', 'Tipo', 'Titulo', 'Titulo_ES', 'Año', 'Duracion', 'Generos', 'Puntuacion', 'Num_Votos', 'Actores', 'Directores', 'Idioma']].dropna().copy()

if "Año" in df_final.columns:
    df_final["Año"] = pd.to_numeric(df_final["Año"], errors="coerce", downcast="integer")
if "Duracion" in df_final.columns:
    df_final["Duracion"] = pd.to_numeric(df_final["Duracion"], errors="coerce", downcast="integer")
if "Puntuacion" in df_final.columns:
    df_final["Puntuacion"] = pd.to_numeric(df_final["Puntuacion"], errors="coerce", downcast="float")
if "Num_Votos" in df_final.columns:
    df_final["Num_Votos"] = pd.to_numeric(df_final["Num_Votos"], errors="coerce", downcast="integer")



# =====================================
# Guardado de la base de datos final
# =====================================

df_final = df_final[(df_final["Num_Votos"] >= 100)]

df_final.to_csv('data/DatosPeliculasSeries.csv', index=False)



# =====================================
# Cifrado archivos DatosPeliculasSeries.csv
# =====================================

encriptacion = b_Codigo.Encriptacion()


with open("data/DatosPeliculasSeries.csv", "rb") as f:
    encriptacion.datos_descifrados["../data/DatosPeliculasSeries_csv.enc"] = f.read()

encriptacion.guardar_csv("../data/DatosPeliculasSeries_csv.enc", context="DatosPeliculasSeries_csv")
print("\nDatosPeliculasSeries_csv cifrado exitosamente.")



