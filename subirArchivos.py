import os
import requests

# Directorio de actualizaciones
UPDATE_DIR = './static'

# Lista para almacenar las actualizaciones
updates = []

# Especificar los tags que deseas buscar
def deftags(nomb):
    global updates  # Usar la lista global de updates
    for tag in nomb:
        tag_dir = os.path.join(UPDATE_DIR, tag)
        if os.path.isdir(tag_dir):  # Verificar que el subdirectorio exista
            for filename in os.listdir(tag_dir):  # Recorrer archivos en el subdirectorio
                # Añadir el tag y el nombre completo del archivo
                updates.append({"tag": tag, "version": filename})

# Función para subir archivos al servidor
def upload_file(tag, file_name):
    url = f"http://127.0.0.1:8000/updates/{tag}/{file_name}"
    try:
        # Construir la ruta completa al archivo
        file_path = os.path.join(UPDATE_DIR, tag, file_name)
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.put(url, files=files)

            # Verificar si la respuesta es un JSON antes de intentar decodificarla
            try:
                response_data = response.json()
                print(f"Respuesta del servidor: {response_data}")
            except ValueError:
                print(f"Respuesta no válida del servidor: {response.text}")

            if response.status_code == 200:
                print(f"Archivo {file_name} subido correctamente.")
            else:
                print(f"Error al subir el archivo {file_name}: {response.text}")

    except FileNotFoundError:
        print(f"Archivo {file_name} no encontrado en {file_path}")
    except PermissionError:
        print(f"No se pudo acceder al archivo {file_name} debido a permisos insuficientes.")

# Inicializar tags y llenar updates
nomb = ["Vega22", "Vega11"]
deftags(nomb)

# Subir todos los archivos de la lista de actualizaciones
for update in updates:
    tag = update["tag"]
    file_name = update["version"]
    upload_file(tag, file_name)
