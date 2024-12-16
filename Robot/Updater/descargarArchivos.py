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
        print(versionActual)
        print("Archivo de version cargado correctamente:", versionActual)
except Exception as e:
    print(f"No se ha podido cargar el archivo de version del robot: {e}")


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
def download_file(modelo, version, path, filename):
    urlPath = os.path.join(up.urlServer, modelo, version, path,).replace('\\','/')
    urlFilePath = os.path.join(urlPath, filename).replace('\\','/')

    # Asegurar que la carpeta correspondiente exista
    os.makedirs(os.path.dirname(urlFilePath), exist_ok=True)
    
    try:
        response = requests.get(urlFilePath, stream=True)  # Usar stream=True para archivos grandes
        if response.status_code == 200:
            with open(urlFilePath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):  # Escribir en partes
                    file.write(chunk)
            print(f"Archivo {version} descargado correctamente en {urlFilePath}.")
        else:
            print(f"Error al descargar {modelo}-{version}: {response.text}")
    except requests.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")

# Función principal para sincronizar archivos
def download_lastVersionChanges(modelo):

    versionRobot = modelo["modelo"]+"_"+modelo["version"]

    urlServerUltimaVersion = os.path.join(up.urlServer, modelo, versionRobot).replace('\\','/')
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

    
    for update in updates:

        os.makedirs(os.path.join(up.DOWNLOAD_DIR, update["path"]).replace('\\','/'), exist_ok=True)

        urlFile = os.path.join(up.urlServer, update["path"],update['filename']).replace('\\','/')
        try:
            # Enviar solicitud GET al servidor
            response = requests.get(urlFile, stream=True)
            
            if response.status_code == 200:
                # Descargar y guardar el archivo en bloques
                with open(os.path.join(up.DOWNLOAD_DIR, update["path"],update["filename"]).replace('\\','/'), "wb") as archivo_local:
                    for chunk in response.iter_content(chunk_size=8192):  # Leer en bloques de 8 KB
                        if chunk:
                            archivo_local.write(chunk)
                print(f"Archivo descargado correctamente en {update['path']}")
            else:
                print(f"\n\nError al consultar el archivo del servidor para {urlFile}: {response.text}\n\n")
                return False
        except requests.RequestException as e:
            print(f"\n\nError al conectar con el servidor: {e}\n\n")
            return False


def updater():
    download_lastVersionChanges(versionActual)
    print("Completado")

#def updater(modelo):
#    sync_updates(modelo)