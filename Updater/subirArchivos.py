import os
import requests
import argparse
import updateConfig as up

# Lista para almacenar las actualizaciones
url = up.urlServer
updates = []
modelos = up.etiquetaVersion

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
        upload_file(update)
    