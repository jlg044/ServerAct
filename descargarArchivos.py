import os
import requests

# Directorios
UPDATE_DIR = './Downloads'

# Función para obtener la lista de versiones en el servidor
def get_server_updates(tag):
    url = f"http://127.0.0.1:8000/updates/{tag}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # Devuelve la lista de versiones
        else:
            print(f"Error al consultar actualizaciones del servidor para {tag}: {response.text}")
            return []
    except requests.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")
        return []

# Función para descargar un archivo del servidor
def download_file(tag, version):
    url = f"http://127.0.0.1:8000/updates/{tag}/{version}"
    # Crear la ruta completa para guardar el archivo en su carpeta correspondiente
    local_path = os.path.join(UPDATE_DIR, tag, version)
    
    # Asegurar que la carpeta correspondiente exista
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    try:
        response = requests.get(url, stream=True)  # Usar stream=True para archivos grandes
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):  # Escribir en partes
                    file.write(chunk)
            print(f"Archivo {version} descargado correctamente en {local_path}.")
        else:
            print(f"Error al descargar {tag}-{version}: {response.text}")
    except requests.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")

# Función principal para sincronizar archivos
def sync_updates(tag):
    print(f"Sincronizando archivos para el tag {tag}...")
    server_versions = get_server_updates(tag)
    if not server_versions:
        print(f"No se encontraron archivos en el servidor para el tag {tag}.")
        return

    local_files = []
    tag_dir = os.path.join(UPDATE_DIR, tag)

    # Obtener los archivos locales del directorio correspondiente
    if os.path.isdir(tag_dir):
        local_files = os.listdir(tag_dir)
    else:
        print(f"Directorio local no encontrado para {tag}. Se crearán los archivos necesarios.")

    # Descargar solo las versiones faltantes
    for version in server_versions:
        if version not in local_files:
            print(f"Descargando archivo faltante: {version}")
            download_file(tag, version)
        else:
            print(f"Archivo ya existe localmente: {version}")

# Tags que deseas sincronizar
tags = ["Vega22", "Vega11"]

# Sincronizar archivos para cada tag
for tag in tags:
    sync_updates(tag)
