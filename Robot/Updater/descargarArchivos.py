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

    versionRobot = modelo["modelo"] + "_" + modelo["version"]

    urlServerUltimaVersion = os.path.join(up.urlServer, modelo["modelo"], versionRobot).replace('\\', '/')
    print(urlServerUltimaVersion)

    try:
        response = requests.get(urlServerUltimaVersion)
        print(response.status_code)

        # Verificar el c贸digo de estado
        if response.status_code == 200:
            # Consumir y almacenar el JSON inmediatamente
            updates = response.json()
            print("Updates recibidos:")

            # Iterar sobre cada versi贸n (clave) y sus actualizaciones
            i = 0
            for version, update_list in reversed(updates.items()):
                print(f"\nVersi贸n: {version}")
                for update in update_list:  # Iterar sobre la lista de actualizaciones para esta versi贸n
                    tag = update['tag']
                    path = update['path']
                    filename = update['filename']
                    if(i == 0):
                        ultimaVersion = path.replace("\\","/").split("/")[1]
                        i=i+1

                    path = path.replace("\\","/").split("/")
                    path[1]=ultimaVersion

                    pathLastVersion = ""
                    pathDownload = ""
                    x=0
                    for paths in path:
                        pathLastVersion = os.path.join(pathLastVersion, paths).replace('\\', '/')
                        if(x>1):
                            pathDownload = os.path.join(pathDownload, paths).replace('\\', '/')
                        x=x+1
                    print(f"Tag: {tag}, Path: {pathLastVersion}, Filename: {filename}")
                    print(pathLastVersion)
                    pathDownload
                    # Crear directorios si no existen
                    ruta_directorio = os.path.join(up.DOWNLOAD_DIR, pathDownload).replace('\\', '/')
                    os.makedirs(ruta_directorio, exist_ok=True)
                    ruta_archivo = os.path.join(ruta_directorio, filename).replace('\\', '/')
                    # Construir URL del archivo
                    urlFile = os.path.join(up.urlServer, pathLastVersion, filename).replace('\\', '/')
                    if os.path.isfile(ruta_archivo):
                        
                        temp_directory = os.path.join(up.TEMP_DIR,pathDownload)
                        os.makedirs(temp_directory, exist_ok=True)
                        temp_directory = os.path.join(temp_directory, filename).replace('\\', '/')

                        
                        # Guardar cambios en el temp directory.
                        with open(ruta_archivo, 'r') as file:
                            data = json.load(file)  # Cargar el contenido del JSON como un diccionario

                        # Modificar el valor de la clave "version"
                        data["version"] = ultimaVersion

                        # Guardar los cambios en el archivo JSON
                        with open(temp_directory, 'w') as file:
                            json.dump(data, file, indent=4)  # Guardar el archivo con formato legible


                    # Descargar el archivo
                    try:
                        file_response = requests.get(urlFile, stream=True)

                        if file_response.status_code == 200:
                            # Descargar y guardar el archivo

                            with open(ruta_archivo, "wb") as archivo_local:
                                for chunk in file_response.iter_content(chunk_size=8192):  # Leer en bloques de 8 KB
                                    if chunk:
                                        archivo_local.write(chunk)
                            print(f"Archivo descargado correctamente en {ruta_archivo}")
                        else:
                            print(f"\n\nError al consultar el archivo del servidor para {urlFile}: {file_response.text}\n\n")
                            return False

                    except requests.RequestException as e:
                        print(f"\n\nError al conectar con el servidor: {e}\n\n")
                        return False

                                # Leer el archivo version.json
            # Leer el archivo JSON
            with open(up.VERSION_DIR, 'r') as file:
                data = json.load(file)  # Cargar el contenido del JSON como un diccionario

            # Modificar el valor de la clave "version"
            data["version"] = ultimaVersion

            # Guardar los cambios en el archivo JSON
            with open(up.VERSION_DIR, 'w') as file:
                json.dump(data, file, indent=4)  # Guardar el archivo con formato legible
        else:
            print(f"Error: {response.status_code} - {response.text}")

    except requests.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")


def updater():
    download_lastVersionChanges(versionActual)
    print("Completado")

#def updater(modelo):
#    sync_updates(modelo)