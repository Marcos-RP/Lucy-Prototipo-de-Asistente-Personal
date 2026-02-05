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

#LUCY_MASTER_KEY = os.getenv("LUCY_MASTER_KEY")
#LUCY_KEY_VERSION = os.getenv("LUCY_KEY_VERSION")

LUCY_MASTER_KEY = "da063b94ab7c57cdb8519d9429a8486eb88fce76807bc46377d70e21a2da4569"
LUCY_KEY_VERSION = "1"

#if not all([LUCY_MASTER_KEY, LUCY_KEY_VERSION]):
#    print("ERROR: Faltan variables de entorno. Verifica tus API KEYS.")
#    exit()

LUCY_MASTER_KEY = bytes.fromhex(LUCY_MASTER_KEY)
LUCY_KEY_VERSION = LUCY_KEY_VERSION



# ============================
# Derivación de claves con HKDF
# ============================

def derivar_clave(contexto, salt):

    clave_derivada = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=(contexto + LUCY_KEY_VERSION).encode(),
        backend=default_backend()
    ).derive(LUCY_MASTER_KEY)

    return clave_derivada



# ============================
# Cifrado y descifrado con AES-GCM
# ============================

def cifrado(datos, contexto):
    salt = os.urandom(16)
    nonce = os.urandom(12)

    llave = derivar_clave(contexto, salt)
    aesgcm = AESGCM(llave)

    ciphertext = aesgcm.encrypt(nonce, datos, None)
    return salt + nonce + ciphertext

def descifrado(datos_cifrados, contexto):
    salt = datos_cifrados[:16]
    nonce = datos_cifrados[16:28]
    ciphertext = datos_cifrados[28:]

    llave = derivar_clave(contexto, salt)
    aesgcm = AESGCM(llave)

    return aesgcm.decrypt(nonce, ciphertext, None)



# ============================
# Lectura y Guardado de archivos
# ============================

class Encriptacion:
    def __init__(self):
        self.datos_descifrados = {}


    def cargar_json(self, path, contexto):
        if path not in self.datos_descifrados:
            with open(path, "rb") as f:
                datos_cifrados = f.read()

            self.datos_descifrados[path] = json.loads(descifrado(datos_cifrados, contexto).decode())

        return self.datos_descifrados[path]

    def cargar_csv(self, path, contexto):
        if path not in self.datos_descifrados:
            with open(path, "rb") as f:
                datos_cifrados = f.read()

            self.datos_descifrados[path] = descifrado(datos_cifrados, contexto)

        return self.datos_descifrados[path]



    def guardar_json(self, path, contexto):
        datos = json.dumps(self.datos_descifrados[path], indent=2).encode()

        with open(path, "wb") as f:
            f.write(cifrado(datos, contexto))

    def guardar_csv(self, path, contexto):
        with open(path, "wb") as f:
            f.write(cifrado(self.datos_descifrados[path], contexto))