import os
import requests
import Updater.updateConfig as up
import json

# Directorios
UPDATE_DIR = up.UPDATE_DIR

#Version actual del robot
try:
    with open(up.VERSION_DIR) as json_file:
        versionActual = json.load(json_file)
        print("Archivo de version cargado correctamente:", versionActual)
except Exception as e:
    print(f"No se ha podido cargar el archivo de version del robot: {e}")

# Función para obtener la lista de versiones en el servidor
def get_server_updates(modelo):
    url = os.path.join(up.urlServer, modelo).replace('\\','/')
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # Devuelve la lista de versiones
        else:
            print(f"Error al consultar actualizaciones del servidor para {modelo}: {response.text}")
            return []
    except requests.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")
        return []

# Función para descargar un archivo del servidor
def download_file(modelo, version):
    url = os.path.join(up.urlServer, modelo, version).replace('\\','/')
    # Crear la ruta completa para guardar el archivo en su carpeta correspondiente
    local_path = os.path.join(UPDATE_DIR, modelo, version)
    
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
            print(f"Error al descargar {modelo}-{version}: {response.text}")
    except requests.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")

# Función principal para sincronizar archivos
def sync_updates(modelo):
    print(f"Sincronizando archivos para el modelo {modelo}...")
    server_versions = get_server_updates(modelo)

    if not server_versions:
        print(f"No se encontraron archivos en el servidor para el tag {modelo}.")
        return

    local_files = []

    modelo_dir = os.path.join(UPDATE_DIR, modelo)

    # Obtener los archivos locales del directorio correspondiente
    if os.path.isdir(modelo_dir):
        local_files = os.listdir(modelo_dir)
    else:
        print(f"Directorio local no encontrado para {modelo}. Se crearán los archivos necesarios.")

    # Descargar solo las versiones faltantes
    for version in server_versions:
        if version not in local_files:
            print(f"Descargando archivo faltante: {version}")
            download_file(modelo, version)
        else:
            print(f"Archivo ya existe localmente: {version}")


def updater():
    sync_updates(versionActual["modelo"])
    print("Completado")

#def updater(modelo):
#    sync_updates(modelo)


