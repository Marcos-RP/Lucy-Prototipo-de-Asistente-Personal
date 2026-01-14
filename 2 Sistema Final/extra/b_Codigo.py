# ============================
# Importación de librerías
# ============================

import json, os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM



# ============================
# Carga de clave maestra y versión
# ============================

LUCY_MASTER_KEY = os.getenv("LUCY_MASTER_KEY")
LUCY_KEY_VERSION = os.getenv("LUCY_KEY_VERSION")

if not all([LUCY_MASTER_KEY, LUCY_KEY_VERSION]):
    print("ERROR: Faltan variables de entorno. Verifica tus API KEYS.")
    exit()

LUCY_MASTER_KEY = bytes.fromhex(LUCY_MASTER_KEY)
LUCY_KEY_VERSION = LUCY_KEY_VERSION



# ============================
# Derivación de claves con HKDF
# ============================

def derivar_clave(contexto):

    clave_derivada = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=(contexto + LUCY_KEY_VERSION).encode(),
        backend=default_backend()
    ).derive(LUCY_MASTER_KEY)

    return clave_derivada



# ============================
# Cifrado y descifrado con AES-GCM
# ============================

def cifrado(datos, llave):
    nonce = os.urandom(12)
    aesgcm = AESGCM(llave)
    return nonce + aesgcm.encrypt(nonce, datos, None)

def descifrado(datos_cifrados, llave):
    nonce = datos_cifrados[:12]
    ciphertext = datos_cifrados[12:]
    aesgcm = AESGCM(llave)
    return aesgcm.decrypt(nonce, ciphertext, None)



# ============================
# Lectura y Guardado de archivos
# ============================

class Encriptacion:
    def __init__(self):
        self.datos_descifrados = {}


    def cargar_json(self, path, context):
        if path not in self.datos_descifrados:

            llave = derivar_clave(context)
            with open(path, "rb") as f:
                datos_cifrados = f.read()

            self.datos_descifrados[path] = json.loads(descifrado(datos_cifrados, llave).decode())

        return self.datos_descifrados[path]

    def cargar_csv(self, path, context):
        if path not in self.datos_descifrados:

            llave = derivar_clave(context)
            with open(path, "rb") as f:
                datos_cifrados = f.read()

            self.datos_descifrados[path] = descifrado(datos_cifrados, llave)

        return self.datos_descifrados[path]



    def guardar_json(self, path, context):
        datos = json.dumps(self.datos_descifrados[path], indent=2).encode()

        llave = derivar_clave(context)
        with open(path, "wb") as f:
            f.write(cifrado(datos, llave))

    def guardar_csv(self, path, context):

        llave = derivar_clave(context)
        with open(path, "wb") as f:
            f.write(cifrado(self.datos_descifrados[path], llave))