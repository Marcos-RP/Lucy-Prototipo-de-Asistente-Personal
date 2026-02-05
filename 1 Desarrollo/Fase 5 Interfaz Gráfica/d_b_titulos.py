# ============================
# Importación de librerías
# ============================

import os
import pandas as pd
from glob import glob
from io import BytesIO
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import RobustScaler



# =====================================
# Funcionalidad principal de Lucy
# =====================================

class Pred_Rec:
    def __init__(self, nombre, id, encriptacion, general, peliculas):

        super().__init__()

        self.nombre = nombre
        self.id = id
        self.encriptacion = encriptacion
        self.general = general
        self.peliculas = peliculas

        self.usuarios_comunes = None
        self.pun_com = None
        self.pun = None



    # =====================================
    # Recolección puntuaciones de usuarios parecidos
    # =====================================

    def juntar_usuarios_comunes(self):
        archivos = glob(os.path.join("Datos_Cifrados", "*_csv.enc"))

        matriz = self.general
        self.pun_com = pd.read_csv(BytesIO(self.encriptacion.cargar_csv(f"Datos_Cifrados/{self.id}_completo_csv.enc", contexto=f"{self.id}_completo_csv")))
        self.pun = pd.read_csv(BytesIO(self.encriptacion.cargar_csv(f"Datos_Cifrados/{self.id}_csv.enc", contexto=f"{self.id}_csv")))

        for archivo in archivos:
            nombre_base = os.path.basename(archivo)
            partes = nombre_base.split("_")

            if len(partes) == 2 and partes[0].isdigit() and partes[1] == "csv.enc":
                archivo = pd.read_csv(BytesIO(self.encriptacion.cargar_csv(f"Datos_Cifrados/{partes[0]}_csv.enc", contexto=f"{partes[0]}_csv")))
                matriz = pd.concat([matriz, archivo])

        self.pun = self.pun.rename(columns={"Mi Nota": "Nota Usuario"})

        df_juntos = matriz.merge(
            self.pun[["tid", "Nota Usuario"]],
            on="tid",
            how="right"
        )
        df_juntos["parecido"] = ((df_juntos["Mi Nota"] - df_juntos["Nota Usuario"]).abs() <= 2)

        similitud = (
            df_juntos
            .groupby("userId")
            .agg(
                coincidencias=("parecido", "sum"),
                comunes=("Mi Nota", lambda x: (x != -1).sum())
            )
        )

        similitud = similitud[similitud["coincidencias"] >= (similitud["comunes"] * 0.5)]
        similitud = similitud[similitud["comunes"] >= (len(self.pun) * 0.5)]
        similitud = similitud.reset_index()

        print(similitud)

        if similitud.empty:
            self.usuarios_comunes = None

        else:
            puntuaciones = similitud.merge(matriz, on="userId", how="left")
            puntuaciones = puntuaciones.groupby("tid", as_index=False)["Mi Nota"].mean()
            puntuaciones["Mi Nota"] = (
                puntuaciones["Mi Nota"]
                .round()
                .clip(1, 10)
                .astype(int)
            )

            puntuaciones_datos = puntuaciones.merge(
                self.peliculas,
                on="tid",
                how="left"
            )

            self.usuarios_comunes = puntuaciones_datos[['tid', 'Tipo', 'Titulo', 'Titulo_ES', 'Año', 'Mi Nota', 'Duracion', 'Generos', 'Puntuacion', 'Num_Votos', 'Actores', 'Directores', 'Idioma']]



    # =====================================
    # Realización de recomendaciones
    # =====================================

    def recomendacion(self):

        final = self.usuarios_comunes
        recomendacion = []

        if final is not None:

            recomendacion = final.merge(self.pun["tid"], on="tid", how='left', indicator=True)
            recomendacion = recomendacion[recomendacion['_merge'] == 'left_only'].drop(columns=['_merge'])
            recomendacion = recomendacion[recomendacion['Mi Nota'] >= 7.5]
            recomendacion = recomendacion.sort_values(["Mi Nota", "Num_Votos", "Puntuacion"], ascending=False)

        if len(recomendacion) == 0:
            print("Personal")

            tipos = self.pun_com["Tipo"].value_counts().index.tolist()

            tipo1 = tipos[0]
            tipo2 = tipos[1] if len(tipos) > 1 else tipo1

            tipos = "|".join([tipo1, tipo2])

            conteo_anos_5 = self.pun_com["Año"].value_counts().head(5).index.tolist()

            ano_minimo = min(conteo_anos_5)
            ano_maximo = max(conteo_anos_5) + 5
            puntuacion_minima = self.pun_com["Puntuacion"].min()

            conteo_generos = (
                self.pun_com["Generos"]
                .str.split(",")
                .explode()
                .str.strip()
                .value_counts()
            )

            rows, columns = self.pun_com.shape

            generos_mas15 = conteo_generos[conteo_generos > (rows * 0.15)]

            sigeneross = generos_mas15.index.tolist()
            sigeneros = "|".join(sigeneross)

            nogeneross = ["None"]
            nogeneros = "|".join(nogeneross)


            recomendacion = self.peliculas[
                (self.peliculas.Tipo.str.contains(tipos)) &
                (self.peliculas.Año >= ano_minimo) &
                (self.peliculas.Año <= ano_maximo) &
                (self.peliculas.Puntuacion >= puntuacion_minima) &
                (self.peliculas.Generos.str.contains(sigeneros, case=False, na=False)) &
                (~self.peliculas.Generos.str.contains(nogeneros, case=False, na=False))
                ]

            recomendacion = recomendacion.merge(self.pun_com["tid"], on="tid", how='left', indicator=True)
            recomendacion = recomendacion[recomendacion['_merge'] == 'left_only'].drop(columns=['_merge'])
            recomendacion = recomendacion.sort_values(["Num_Votos", "Puntuacion"], ascending=False)

        return recomendacion.head(100)



    # =====================================
    # Realización de predicción
    # =====================================

    def predicciones(self, tid):

        final = self.usuarios_comunes

        conteo = int((final["Mi Nota"].value_counts().min()) * 1.5)

        def eleccion_clases(df, conteo):
            n = len(df)
            if n > conteo:
                return df.sample(n=conteo, random_state=100496072)
            else:
                return df

        df_balanceado = (
            final
            .groupby("Mi Nota", group_keys=False)
            .apply(eleccion_clases, conteo)
        )


        df_datos_reg = df_balanceado[['Tipo', 'Año', 'Duracion', 'Puntuacion', 'Num_Votos', 'Generos', 'Mi Nota']].copy()
        dummies = df_datos_reg["Generos"].str.get_dummies(sep=",")
        dummies2 = df_datos_reg["Tipo"].str.get_dummies(sep=",")
        df_datos_reg = df_datos_reg.join(dummies2).drop(columns=["Tipo"])
        df_datos_reg = df_datos_reg.join(dummies).drop(columns=["Generos"])
        df_datos_reg['Mi Nota'] /= 10


        col_gen = ['Año', 'Duracion', 'Puntuacion', 'Num_Votos', 'Mi Nota', 'movie', 'tvSeries', 'tvMiniSeries',
                   'tvSpecial', 'Thriller', 'Horror', 'Documentary', 'Sci-Fi', 'Romance', 'Drama', 'Sport', 'War', 'Biography',
                   'Musical', 'Crime', 'Music', 'Action', 'Short', 'History', 'Comedy', 'Mystery', 'Animation', 'Adventure',
                   'Family', 'Fantasy', 'Game-Show', 'Adult', 'Western', 'Talk-Show', 'Film-Noir']

        for col in col_gen:
            if col not in df_datos_reg.columns:
                df_datos_reg[col] = 0

        df_datos_reg = df_datos_reg[col_gen]

        X_reg = df_datos_reg.drop("Mi Nota", axis=1)
        y_reg = df_datos_reg["Mi Nota"]


        modelo = Pipeline([
            ('scaler', RobustScaler()),
            ('modelo', RandomForestRegressor(min_samples_leaf=2, min_samples_split=5, random_state=100496072))
        ])

        modelo.fit(X_reg, y_reg)

        informacion = self.peliculas[(self.peliculas["tid"] == tid)]

        a_predecir = informacion[['Tipo', 'Año', 'Duracion', 'Puntuacion', 'Num_Votos', 'Generos']].copy()

        dummies = a_predecir["Generos"].str.get_dummies(sep=",")
        dummies2 = a_predecir["Tipo"].str.get_dummies(sep=",")
        a_predecir = a_predecir.join(dummies2).drop(columns=["Tipo"])
        a_predecir = a_predecir.join(dummies).drop(columns=["Generos"])

        a_predecir = pd.DataFrame(a_predecir)

        col_gen = ['Año', 'Duracion', 'Puntuacion', 'Num_Votos', 'movie', 'tvSeries', 'tvMiniSeries',
                   'tvSpecial', 'Thriller', 'Horror', 'Documentary', 'Sci-Fi', 'Romance', 'Drama', 'Sport', 'War', 'Biography',
                   'Musical', 'Crime', 'Music', 'Action', 'Short', 'History', 'Comedy', 'Mystery', 'Animation', 'Adventure',
                   'Family', 'Fantasy', 'Game-Show', 'Adult', 'Western', 'Talk-Show', 'Film-Noir']

        missing = [c for c in col_gen if c not in a_predecir.columns]
        if missing:
            for c in missing:
                a_predecir[c] = 0

        a_predecir = a_predecir[col_gen]

        prediccion = modelo.predict(a_predecir)
        return int(prediccion[0] * 100)



    # =====================================
    # Realización de búsquedas concretas
    # =====================================

    def busqueda_concreta(self, datos):

        tipos = "|".join(datos["tipos"])
        ano_minimo = int(datos["ano_minimo"])
        ano_maximo = int(datos["ano_maximo"])
        puntuacion_minima = float(datos["puntuacion_minima"])
        sigeneros = "|".join(datos["sigeneros"])
        nogeneros = "|".join(datos["nogeneros"])

        busqueda_concreta = self.peliculas[
            (self.peliculas.Tipo.str.contains(tipos)) &
            (self.peliculas.Año >= ano_minimo) &
            (self.peliculas.Año <= ano_maximo) &
            (self.peliculas.Puntuacion >= puntuacion_minima) &
            (self.peliculas.Generos.str.contains(sigeneros, case=False, na=False)) &
            (~self.peliculas.Generos.str.contains(nogeneros, case=False, na=False))
        ]

        busqueda_concreta = busqueda_concreta.sort_values(["Num_Votos", "Puntuacion"], ascending=False)

        busqueda_concreta = busqueda_concreta.merge(self.pun["tid"], on="tid", how='left', indicator=True)
        busqueda_concreta = busqueda_concreta[busqueda_concreta['_merge'] == 'left_only'].drop(columns=['_merge'])

        return busqueda_concreta.head(100)