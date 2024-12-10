import os
import requests
import argparse
import updateConfig as up
import hashlib
import json

# Lista para almacenar las actualizaciones
url = up.urlServer
updates = []
modelos = up.etiquetaVersion
cambios = []


def tojson(cambios):

    # Ruta del archivo donde deseas guardar el JSON
    ruta_archivo = 'C:/Users/mario/sourceServer/ServerAct/Updater/updatesloc/Vega22/Vega22_v1.0.4/cambios.json'

    # Convertir el diccionario a JSON y guardarlo en el archivo
    with open(ruta_archivo, 'w') as archivo_json:
        json.dump(cambios, archivo_json, indent=4)

    print(f"El diccionario se ha guardado correctamente en {ruta_archivo}")

# Especificar los tags que deseas buscar
def deftags(nomb):
    
    for tag in nomb:
        tag_dir = os.path.join(path, tag)
        if os.path.isdir(tag_dir):  # Verificar que el subdirectorio exista
            iteracionArchivos(tag_dir,tag)
        else: print(f"Directorio {tag_dir} no existe")

def iteracionArchivos(dir,tag):

    global updates
    
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

def filesComparator(update):

    #Obtener la ultima version del programa.
    url = os.path.join(up.urlServer, update["tag"]).replace('\\','/')
    try:
        response = requests.get(url)
        if response.status_code == 200:
            versiones_server = response.json()  # Devuelve la lista de versiones
        else:
            print(f"Error al consultar actualizaciones del servidor para {update["tag"]}: {response.text}")
            return []
    except requests.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")
        return []
    
    # Crear una lista de pares (original, Version)
    parsed_versions = [(v, (v.split('v')[1])) for v in versiones_server]
    # Ordenar por la versión (segundo elemento del par)
    parsed_versions.sort(key=lambda x: x[1], reverse=True)
    # Retornar la versión original que sea la última
    ultimaVersion = parsed_versions[0][0]

    file_name = update["filename"]
    localPath = update["path"]

    interPath = localPath.split(update["tag"])
    interPath = interPath[-1].replace('\\','/').split("/")
    inter = ""

    urlFile = os.path.join(up.urlServer, update["tag"], ultimaVersion).replace('\\','/')
    i = 0

    for paths in interPath:

        if i!=0:
            inter = os.path.join(inter, paths).replace('\\','/')
        i = i+1



    urlFile = os.path.join(urlFile,inter,file_name).replace('\\','/')
    urlLocalFile = os.path.join(localPath,file_name).replace('\\','/')
    ruta_destino = "C:/Users/mario/sourceServer/ServerAct/temp/"
    ruta_destino = os.path.join(ruta_destino,inter).replace('\\','/')
    os.makedirs(ruta_destino, exist_ok=True)
    ruta_destino = os.path.join(ruta_destino,file_name).replace('\\','/')
 

    try:
        # Enviar solicitud GET al servidor
        response = requests.get(urlFile, stream=True)
        
        if response.status_code == 200:
            # Descargar y guardar el archivo en bloques
            with open(ruta_destino, "wb") as archivo_local:
                for chunk in response.iter_content(chunk_size=8192):  # Leer en bloques de 8 KB
                    if chunk:
                        archivo_local.write(chunk)
            print(f"Archivo descargado correctamente en {ruta_destino}")
        else:
            print(f"\n\nError al consultar el archivo del servidor para {urlFile}: {response.text}\n\n")
            return False
    except requests.RequestException as e:
        print(f"\n\nError al conectar con el servidor: {e}\n\n")
        return False


    pathLocal = os.path.join(localPath,file_name).replace('\\','/')
    hashLocal = HashCreator(pathLocal)
    hashVersion = HashCreator(ruta_destino)
    if (hashLocal == hashVersion):
        print("Correcto Funcionamiento")
    else:
        print(f"\n\n\nSe ha detectado una modificacion!!: {pathLocal}\n\n\n")
        cambios.append(

            {"tag": update["tag"], 
            "path": localPath.replace('\\','/'),
            "filename": file_name
            })




def HashCreator(archivo):
    """
    Calcula el hash de un archivo utilizando el algoritmo indicado.
    :param archivo: Ruta del archivo
    :param metodo: Algoritmo de hash (por defecto SHA-256)
    :return: Hash del archivo en formato hexadecimal
    """

    hash_func = hashlib.sha256()  # Puedes cambiar a otro algoritmo como md5 o sha1
    try:
        with open(archivo, "rb") as f:  # Asegúrate de leer en modo binario
            while chunk := f.read(8192):  # Leer en bloques de 8 KB
                hash_func.update(chunk)
        return hash_func.hexdigest()  # Devuelve el hash en formato hexadecimal
    except FileNotFoundError:
        return None
    



# Función para subir archivos al servidor
def upload_file(update):

    file_name = update["filename"]
    localPath = update["path"]

    for modelo in modelos:
        indice = localPath.find(modelo)
        if indice != -1:
            filePath = localPath[indice:]  # Extraer la subruta desde el modelo encontrado
            break  # Detener la búsqueda después del primer hallazgo
    

    urlFile = os.path.join(url, filePath).replace('\\','/')


    try:
        # Construir la ruta completa al archivo
        file_path = os.path.join(localPath, file_name).replace('\\','/')

        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.put(urlFile, files=files)

            # Verificar si la respuesta es un JSON antes de intentar decodificarla
            try:
                response_data = response.json()
                print(f"Respuesta del servidor: {response_data}")
            except ValueError:
                print(f"\n \nAlerta!!\nRespuesta no válida del servidor: {response.text}\n \n")

            if response.status_code == 200:
                print(f"Archivo {file_name} subido correctamente en {urlFile}.")
            else:
                print(f"\n \nAlerta!!\nError al subir el archivo {file_name}: {response.text}\n \n")

    except FileNotFoundError:
        print(f"\n \nAlerta!!\nArchivo {file_name} no encontrado en {file_path}\n \n")
    except PermissionError:
        print(f"\n \nAlerta!!\nNo se pudo acceder al archivo {file_name} debido a permisos insuficientes.\n \n")

# Main
if __name__ == '__main__':
    # Setup
    parser = argparse.ArgumentParser(description='Editar manualmente los sectores sobre un set de imágenes')
    parser.add_argument('set_path', type=str, help='Ruta al set de imágenes')
    args = parser.parse_args()
    path = args.set_path.replace('\\', '/')
    if path[-1] != '/':
        path += '/'
    if not os.path.exists(path):
        raise Exception('No existe el directorio')
    files = [file for file in os.listdir(path)]
    if not files:
        raise Exception('No hay archivos en el directorio')
    
    # Inicializar tags y llenar updates
    deftags(up.etiquetaVersion)

    # Subir todos los archivos de la lista de actualizaciones
    for update in updates:
        filesComparator(update)

    for update in updates:
        upload_file(update)
    tojson(cambios)
    print(cambios)
    