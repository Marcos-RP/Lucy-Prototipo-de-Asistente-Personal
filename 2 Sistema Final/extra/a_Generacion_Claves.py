# ============================
# Importación de librerías
# ============================

import subprocess, secrets, os



# ============================
# Inicialización de las Keys
# ============================

if __name__ == "__main__":

    if "LUCY_MASTER_KEY" not in os.environ:
        master_key = secrets.token_hex(32)  # 256 bits
        subprocess.run(f'setx LUCY_MASTER_KEY {master_key}', shell=True, check=True)
        print(f"Variable LUCY_MASTER_KEY creada con valor {master_key}.")
    else:
        master_key = os.environ["LUCY_MASTER_KEY"]
        print(f"Variable LUCY_MASTER_KEY ya existe con valor {master_key}.")

    if "LUCY_KEY_VERSION" not in os.environ:
        key_version = "1"
        subprocess.run(f'setx LUCY_KEY_VERSION {key_version}', shell=True, check=True)
        print(f"Variable LUCY_KEY_VERSION creada con valor {key_version}.")
    else:
        key_version = os.environ["LUCY_KEY_VERSION"]
        print(f"Variable LUCY_KEY_VERSION ya existe con valor {key_version}.")