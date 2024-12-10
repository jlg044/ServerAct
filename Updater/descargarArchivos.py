import os
import requests
import Updater.updateConfig as up
import json

# Directorios
DOWNLOAD_DIR = up.DOWNLOAD_DIR

#Version actual del robot


try:
    with open(up.VERSION_DIR) as json_file:
        versionActual = json.load(json_file)
        print("Archivo de version cargado correctamente:", versionActual)
except Exception as e:
    print(f"No se ha podido cargar el archivo de version del robot: {e}")


# Función para obtener la ultima version del servidor
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

def get_last_version(versiones_server):

    # Crear una lista de pares (original, Version)
    parsed_versions = [(v, (v.split('v')[1])) for v in versiones_server]
    # Ordenar por la versión (segundo elemento del par)
    parsed_versions.sort(key=lambda x: x[1], reverse=True)
    # Retornar la versión original que sea la última
    return parsed_versions[0][0]

def iteracionArchivos(dir,tag,updates):

    updates
    
    for filename in os.listdir(dir): #Para cada archivo en el directorio

        if os.path.isdir(os.path.join(dir, filename)):

            iteracionArchivos(os.path.join(dir, filename),tag)
                # Recorrer archivos en el subdirectorio
                # Añadir el tag y el nombre completo del archivo
        else:
            updates.append(

            {"tag": tag, 
            "path": dir,
            "filename": filename
            })



# Función para descargar un archivo del servidor
def download_file(modelo, version):
    url = os.path.join(up.urlServer, modelo, version).replace('\\','/')
    # Crear la ruta completa para guardar el archivo en su carpeta correspondiente
    local_path = os.path.join(DOWNLOAD_DIR, modelo, version)
    
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
    print(f"La ultima version para el modelo {modelo} es la version {get_last_version(server_versions)}")
    ultimaVersion = get_last_version(server_versions)
    
    if not server_versions:
        print(f"No se encontraron archivos en el servidor para el tag {modelo}.")
        return
    

    urlServerUltimaVersion = os.path.join(up.urlServer, modelo, ultimaVersion).replace('\\','/')
    print(urlServerUltimaVersion)


    try:
        response = requests.get(urlServerUltimaVersion)
        print(response.status_code)

            # Verificar el código de estado
        if response.status_code == 200:
            # Parsear el resultado como JSON
            updates = response.json()
            print("Updates recibidos:")
            for update in updates:
                print(f"Tag: {update['tag']}, Path: {update['path']}, Filename: {update['filename']}")
        else:
            print(f"Error: {response.status_code} - {response.json().get('error', 'Unknown error')}")

    except requests.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")


    
    #Recreacion del directorio local.
    local_files = []
    actualDir = os.path.join(DOWNLOAD_DIR, modelo)
    if os.path.isdir(actualDir):  # Verificar que el subdirectorio exista
        iteracionArchivos(actualDir,modelo,local_files)
    else: print(f"Directorio {actualDir} no existe")

    modelo_dir = os.path.join(DOWNLOAD_DIR, modelo)

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


