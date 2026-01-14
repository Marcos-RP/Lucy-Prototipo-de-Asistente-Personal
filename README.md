# 🎬 Lucy: Asistente Personal y Sistema de Recomendación Híbrido

> **Trabajo de Fin de Grado (TFG) - Ingeniería Informática**
> *Universidad Carlos III de Madrid*

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python)
![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?logo=scikit-learn)
![OpenAI](https://img.shields.io/badge/GenAI-OpenAI-412991?logo=openai)
![Status](https://img.shields.io/badge/Status-Finalizado-success)

**Lucy** es un sistema inteligente que combina un **Motor de Recomendación Predictivo (ML)** que aprende de tus gustos con un **Asistente Conversacional (GenAI)** capaz de realizar tareas complejas.

---

## 📖 Análisis del Problema
El objetivo principal de este proyecto es automatizar y optimizar la toma de decisiones de ocio. Lucy delega la elección de qué ver a un sistema que conoce los hábitos del usuario, analizando películas y series evaluadas previamente para entrenar un modelo que predice matemáticamente la probabilidad de disfrutar un nuevo título.

## ✨ Funcionalidades

### 1. Funcionalidad Principal: Motor de Recomendación
* **Análisis de Historial:** Procesa películas y series evaluadas por el usuario.
* **Modelo Predictivo (ML):** Entrena un algoritmo (basado en técnicas como KNN/Random Forest) que calcula el % de afinidad con títulos no vistos.
* **Filtrado Inteligente:** Solo recomienda contenido con alta probabilidad de éxito.

### 2. Funcionalidad Secundaria: Asistente General (IA Generativa)
Lucy integra un chat interactivo conectado a OpenAI capaz de:
* **Conversar:** Respuestas naturales a cualquier consulta.
* **Búsqueda Web:** Acceso a Google Search para información en tiempo real (ej. "¿Qué tiempo hace en Tokio?").
* **Generación de Imágenes:** Creación de contenido visual bajo demanda.
* **Integración Móvil:** Envío automático de archivos y mensajes al smartphone del usuario (vía Telegram).

---

## 🛠️ Tecnologías y Herramientas

### Desarrollo y Entorno
* **Python 3.10.11:** Lenguaje base del proyecto.
* **GitHub:** Control de versiones.
* **PyCharm & Jupyter Notebook:** IDEs utilizados para el desarrollo modular y el análisis de datos interactivo.

### Ciencia de Datos e IA
* **Scikit-learn:** Entrenamiento de modelos de Machine Learning.
* **Pandas & JSON:** Lectura y manipulación de datasets masivos.
* **RAM:** Uso intensivo de memoria para carga rápida de matrices de datos.

### Interfaz y Seguridad
* **PyQt5:** Interfaz gráfica de usuario (GUI) de escritorio.
* **Cryptography:** Cifrado y descifrado de credenciales y datos sensibles.

---

## ⚙️ Instalación y Configuración

Sigue estos pasos estrictamente para desplegar el sistema.

### 1. Clonar y preparar entorno
```bash
git clone https://github.com/Marcos-RP/TFG-Desarrollo-de-un-Asistente-Personal.git
cd Lucy-TFG
pip install -r requirements.txt
```

### 2. Descarga de Datos (Crítico)
Debido al tamaño de los datasets, estos no se incluyen en el repositorio.
1.  Descarga los archivos base del sistema desde: **[Datasets IMDb](https://datasets.imdbws.com/)**
2.  Descarga el dataset `ml-32m.zip` desde: **[MovieLens 32M](https://grouplens.org/datasets/movielens/32m/)**
3.  Descomprime el zip.
4.  Mueve **todos** los archivos obtenidos a la carpeta del proyecto:
    `./2 Sistema Final/extra/data/`

### 3. Inicialización de la Base de Datos
Ejecuta los scripts de preparación (puede tardar debido al volumen de datos):

* **Paso A: Crear Base de Datos** (~15-30 min)
```bash
python "2 Sistema Final/extra/c_CreacionBaseDatos.py"
```

* **Paso B: Generar Matriz General** (~2 min)
```bash
python "2 Sistema Final/extra/d_CreaciónMatrizGeneral.py"
```

### 4. Configuración de APIs (Solo para el Chat)
Para activar la búsqueda web, generación de imágenes y notificaciones móviles:
1.  Consigue tus claves de **OpenAI**, **Google Search (ID + Key)** y **Telegram Bot**.
2.  Edita el archivo: `2 Sistema Final/src/d_c_chat.py`
3.  Sustituye las variables correspondientes:
```python
OPENAI_API_KEY = "tu-clave-aqui"
GOOGLE_API_KEY = "tu-clave-aqui"
GOOGLE_CSE_ID = "tu-id-aqui"
BOT_TOKEN = "tu-token-aqui"
CHAT_ID = "tu-id-aqui"
```

---

## ▶️ Guía de Uso Rápida

Para iniciar el sistema:
```bash
python "2 Sistema Final/inicio.py"
```

### Flujo de Usuario Típico
1.  **Registro:** Crea un perfil de "Nuevo Usuario".
2.  **Cold Start:** Ve a la sección **Películas** y puntúa al menos un título (ej. "Juego de Tronos": 89) para activar el algoritmo.
3.  **Recomendación:** Pulsa "Recomendaciones". El sistema sugerirá títulos afines (ej. "El Caballero Oscuro") basándose en tu puntuación.
4.  **Asistente:** Ve a la sección **Chat** para pedir información, imágenes o enviar alertas a tu móvil.
5.  **Multiusuario:** Usa el botón "Cambio de Sesión" para que otra persona use Lucy con sus propias preferencias sin afectar a tu perfil.

---

## 👤 Autor

**Marcos Romo Poveda**
* [LinkedIn](https://www.linkedin.com/in/marcosrpv)
* [GitHub](https://github.com/Marcos-RP)

> Este proyecto fue desarrollado como parte del Grado en Ingeniería Informática (2025-2026).
