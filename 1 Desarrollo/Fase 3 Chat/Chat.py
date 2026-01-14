# =====================================
# Importación de librerías y lecturas de las API Keys
# =====================================

from openai import OpenAI
import speech_recognition as sr
import subprocess, requests, datetime, json, os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not all([OPENAI_API_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID, BOT_TOKEN, CHAT_ID]):
    print("ERROR: Faltan variables de entorno. Verifica tus API KEYS.")
    exit()



# =====================================
# Definición de las herramientas
# =====================================

client = OpenAI(api_key=OPENAI_API_KEY)

Herramientas = [
    {
        "type": "function",
        "function": {
            "name": "generar_imagen",
            "description": "Genera una imagen con DALL-E 3 basada en una descripción.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instrucciones": {"type": "string", "description": "Prompt detallado para la imagen."}
                },
                "required": ["instrucciones"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "enviar_telegram",
            "description": "Envía un mensaje de texto o un archivo al Telegram del usuario.",
            "parameters": {
                "type": "object",
                "properties": {
                    "texto": {"type": "string", "description": "Texto del mensaje (opcional si hay archivo)."},
                    "archivo": {"type": "string", "description": "Ruta absoluta del archivo (opcional)."}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "busquedas_google",
            "description": "Busca información EXTERNA o ACTUAL (noticias, clima, datos específicos).",
            "parameters": {
                "type": "object",
                "properties": {
                    "instrucciones": {"type": "string", "description": "Consulta optimizada para Google."}
                },
                "required": ["instrucciones"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "comandos",
            "description": "Imprime un comando.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instrucciones": {"type": "string", "description": "Comando a imprimir."}
                },
                "required": ["instrucciones"],
            },
        },
    }
]



# =====================================
# Creación del agente y de las herramientas
# =====================================

class Asistente:
    def __init__(self):
        self.prompt = creacion_prompt()
        self.memoria = [{"role": "system", "content": self.prompt}]
        self.funciones = {
            "generar_imagen": self.generar_imagen,
            "enviar_telegram": self.enviar_telegram,
            "busquedas_google": self.busquedas_google,
            "comandos": self.comandos
        }

    def generar_imagen(self, instrucciones):
        print(f"Generando imagen: '{instrucciones}']")

        try:
            respuesta = client.images.generate(model="dall-e-3", prompt=instrucciones, size="1024x1024", quality="standard", n=1)
            hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"img_{hora}.png"

            with open(archivo, "wb") as f:
                f.write(requests.get(respuesta.data[0].url).content)

            print(f"Guardada en: {os.path.abspath(archivo)}]")
            return f"Imagen creada correctamente. Ruta del archivo: {os.path.abspath(archivo)}"

        except Exception as e:
            return f"Error: {str(e)}"


    def enviar_telegram(self, texto=None, archivo=None):
        print(f"Enviando a Telegram")

        try:
            if archivo:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
                with open(archivo, "rb") as f:
                    requests.post(url, data={"chat_id": CHAT_ID, "caption": texto}, files={"document": f})
                return "Archivo enviado con éxito."

            elif texto:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                requests.post(url, data={"chat_id": CHAT_ID, "text": texto})
                return "Mensaje de texto enviado."
            return "Error: Se requiere texto o archivo."

        except Exception as e:
            return f"Error: {str(e)}"


    def busquedas_google(self, instrucciones):
        print(f"Buscando en Google: '{instrucciones}'")

        url = "https://www.googleapis.com/customsearch/v1"
        try:
            params = {"q": instrucciones, "key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "num": 3}
            respuesta = requests.get(url, params=params)
            respuesta.raise_for_status()
            informacion = respuesta.json()

            if 'items' in informacion:
                respuesta = []
                for item in informacion["items"]:
                    respuesta.append(f"- {item['title']}: {item['snippet']}")

                return "\n".join(respuesta)
            return "No hay resultados relevantes."

        except Exception as e:
            return f"Error: {str(e)}"


    def comandos(self, instrucciones):
        print(f"Comando a ejecutar: {instrucciones}")

        try:
            if isinstance(instrucciones, list):
                if instrucciones[0].lower() == 'start':
                    comando = []
                    for instruccion in instrucciones:
                        if ' ' in instruccion:
                            comando.append(f'"{instruccion}"')
                        else:
                            comando.append(instruccion)

                    comando_final = ' '.join(comando)
                    subprocess.run(comando_final, shell=True, check=True)

                else:
                    subprocess.run(instrucciones, check=True)

            elif isinstance(instrucciones, str):
                subprocess.run(instrucciones, shell=True, check=True)

            else:
                return "Comando inválido."
            return "Comando ejecutado correctamente."

        except FileNotFoundError:
            return "No se encuentra el archivo o programa."
        except subprocess.CalledProcessError as e:
            return f"Error al ejecutar el comando: str{e}"


    def procesar_entrada(self, prompt):
        self.memoria.append({"role": "user", "content": prompt})

        while True:
            respuesta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.memoria,
                tools=Herramientas,
                tool_choice="auto"
            )

            mensaje = respuesta.choices[0].message
            self.memoria.append(mensaje)

            if not mensaje.tool_calls:
                return mensaje.content

            for herramienta in mensaje.tool_calls:

                if herramienta.function.name in self.funciones:
                    function_response = self.funciones[herramienta.function.name](**json.loads(herramienta.function.arguments))

                    self.memoria.append({
                        "tool_call_id": herramienta.id,
                        "role": "tool",
                        "name": herramienta.function.name,
                        "content": str(function_response),
                    })



# =====================================
# Creación del prompt
# =====================================

def creacion_prompt():

    prompt = (
        "### ROL E IDENTIDAD\n"
        "Eres Lucy, una asistente conversacional avanzada. Tu objetivo es ser extremadamente útil, directa y eficiente.\n\n"

        "### GESTIÓN DE CONOCIMIENTO (INTERNO VS. EXTERNO)\n"
        "1. **Conocimiento Interno:** Utilízalo SIEMPRE para preguntas de cultura general, historia, lógica, redacción de textos, chistes, cuentos o explicaciones teóricas. NO uses Google para esto.\n"
        "2. **Herramienta '':** Úsala ÚNICAMENTE si:\n"
        "   - La información requiere datos en TIEMPO REAL (noticias, clima, hora actual, resultados deportivos).\n"
        "   - El usuario busca un dato muy ESPECÍFICO o NICHO que tu conocimiento no cubre.\n"
        "   - Necesitas verificar un hecho factual reciente.\n\n"

        "### USO DE HERRAMIENTAS Y ACCIONES\n"
        "- **Mensajería:** Usa 'mensaje' o 'enviar_archivo' solo cuando el usuario te pida explícitamente enviar información o archivos a su móvil o Telegram.\n"
        "- **Comandos:** Usa 'comandos' si el usuario da una orden clara de ejecución o de abrir alguna aplicacion o enlace. Debes devolver **solo la lista de argumentos que se pasa dentro de `subprocess.run([...])`**, lista para ejecutar. Ejemplos:\n"
        "    - Apagar el ordenador → `['shutdown', '/s', '/t', '10']`\n"
        "    - Abrir una aplicación (por ejemplo, Steam) → `['start', 'steam://open/main']` o `['start', 'windowsdefender://']`\n"
        "    - Silenciar el sonido → 'powershell -Command (New-Object -ComObject WScript.Shell).SendKeys([char]173)' (o el comando equivalente del sistema)\n"
        "    - Cualquier otro comando → devuelve la lista de argumentos exacta necesaria para ejecutar la acción, **sin ningún texto adicional**.\n"
        "- **Generación de Imágenes:**\n"
        "   1. Si te piden crear una imagen, usa 'generar_imagen'.\n"
        "   2. El sistema te devolverá la ruta del archivo.\n"
        "   3. SI Y SOLO SI el usuario pidió enviarla también, usa 'enviar_archivo' con la ruta obtenida.\n\n"

        "### ESTILO DE RESPUESTA\n"
        "- Prioriza dar el dato solicitado directamente, sin rodeos.\n"
        "- Mantén un tono servicial pero conciso.\n"
        "- Cuando uses un comando, devuélvelo exactamente como debe ejecutarse, sin explicaciones innecesarias."
    )
    return prompt



# =====================================
# Reconocimiento de voz y ejecución de la petición
# =====================================

def reconocer_voz():
    reconocedor = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando... (habla ahora)")
        try:
            reconocedor.adjust_for_ambient_noise(source, duration=0.5)
            audio = reconocedor.listen(source, timeout=5, phrase_time_limit=10)
            print("Procesando audio...")
            texto = reconocedor.recognize_google(audio, language="es-ES")
            return texto
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return ""


def ejecutar_peticion(lucy, conversacion, tipo):

    if tipo == "audio":
        user_input = reconocer_voz()
        if not user_input:
            print( "No te escuché bien, intenta de nuevo.")
        print(f"Tú (Voz): {user_input}")
    else:
        user_input = conversacion

    try:
        respuesta = lucy.procesar_entrada(user_input)
        return f"Lucy: {respuesta}"
    except Exception as e:
        return f"Error crítico: {e}"



# =====================================
# Inicio del chat
# =====================================

def main():
    lucy = Asistente()

    while True:

        conversacion = input("\nEscribe texto o pulsa para hablar: ").strip()
        if conversacion == "":
            tipo = "audio"
        else:
            tipo = "texto"

        respuesta = ejecutar_peticion(lucy, conversacion, tipo)

        print(respuesta)


if __name__ == "__main__":
    main()