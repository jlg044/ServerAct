import os
import requests
import argparse
import updateConfig as up
import asyncio
import zipfile

#Recoge el modelo en funcion de la version del programa. Formato Ej: Vega22_v1.0.0
def getModel():

    pathModel = path.replace('\\', '/').split("/")
    if pathModel[-1] == '':
        pathModel = pathModel[-2].split("_")
    else:
        pathModel = pathModel[-1].split("_")
    return pathModel[0]

def crear_zip(carpeta_origen, archivo_zip_destino):
    with zipfile.ZipFile(archivo_zip_destino, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Recorre todos los archivos y subcarpetas en la carpeta origen
        for root, dirs, files in os.walk(carpeta_origen):
            for file in files:
                # Ruta completa del archivo actual
                ruta_completa = os.path.join(root, file)
                # Ruta relativa para el archivo ZIP
                ruta_relativa = os.path.relpath(ruta_completa, carpeta_origen)
                # Añade el archivo al ZIP
                zipf.write(ruta_completa, ruta_relativa)

#Itera un directorio recursivamente y almacena en updates todos los archivos que almacena
def iteracionArchivos(dir,tag,updates):
    
    for filename in os.listdir(dir): #Para cada archivo en el directorio

        if os.path.isdir(os.path.join(dir, filename)):

            iteracionArchivos(os.path.join(dir, filename),tag,updates)
                # Recorrer archivos en el subdirectorio
                # Añadir el tag y el nombre completo del archivo
        else:
            updates.append(

            {"tag": tag, 
            "path": dir,
            "filename": filename
            })

# Función para subir archivos al servidor
async def upload_file(update, end=False):
    file_name = update["filename"]
    localPath = update["path"]
    modelo = update["tag"]

    formatted_path = localPath.replace('\\','/').split(modelo, 1)[1].split("/")
    version = None
    encontrado = any(palabra.startswith(modelo) for palabra in formatted_path)
    if encontrado:
        print(f"Existe una palabra que empieza por {modelo}.")
    else:
        print(f"No hay ninguna palabra que empiece por {modelo}.")

        versionP = localPath.split("/")
        encontrado = any(palabra.startswith(modelo) for palabra in versionP)
        if encontrado:
            print(f"Existe una palabra que empieza por {modelo}.")
            version=modelo+formatted_path[0]
            print(f"La version del archivo es: {version}")
        else:
            print(f"No hay ninguna version en la ruta proporcionada {modelo}.")
            return
        
    print(localPath)

    

    middle = ""
    i = 0
    for paths in formatted_path:
        if version is not None and i == 0:
            middle = os.path.join(middle, version).replace('\\','/')
            print(f"Se ha incorporado la version a middle: ")
        if i!=0:
            middle = os.path.join(middle, paths).replace('\\','/')
        i = i+1

    urlFile = os.path.join(up.urlServer, modelo, middle).replace('\\','/')
    url_with_end = f"{urlFile}?end={end}"

    version = middle.split("/")[0]
    path_zip = "./" + version + ".zip"
    
    crear_zip(path, path_zip)

    try:
        # Construir la ruta completa al archivo
        file_path = os.path.join(localPath, file_name).replace('\\','/')
        print(file_path)
        print(url_with_end)

        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.put(url_with_end, files=files)

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

async def main(path):
    
    
    
    #Comienzo actualizacion.
    model = getModel()
    print("C")
    updates = []
    version_dir = os.path.join(path)
    if os.path.isdir(version_dir):  # Verificar que el subdirectorio exista
        iteracionArchivos(version_dir,model,updates)
    else: print(f"Directorio {version_dir} no existe")

    for update in updates:

        if (update == updates[-1]):
            await upload_file(update,end = True)
            break
        await upload_file(update)

# Main
if __name__ == '__main__':
 
    # Setup Solicita ruta para actualizacion Formato Ej: Vega22_v0.0.0
    parser = argparse.ArgumentParser(description='Editar manualmente los sectores sobre un set de imágenes')
    parser.add_argument('set_path', type=str, help='Ruta al set de imágenes')
    args = parser.parse_args()
    path = args.set_path.replace('\\', '/')
    if path[-1] != '/':
        path += '/'
    #Comprueba que existe el directorio
    if not os.path.exists(path):
        raise Exception('No existe el directorio')
    # Comprueba si hay archivos dentro del directorio.
    files = [file for file in os.listdir(path)]
    if not files:
        raise Exception('No hay archivos en el directorio')

    asyncio.run(main(path))
   