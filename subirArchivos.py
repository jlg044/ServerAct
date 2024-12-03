import os
import requests
import argparse

# Lista para almacenar las actualizaciones
url = "http://127.0.0.1:8000/updates"

# Especificar los tags que deseas buscar
def deftags(nomb):

    updates = []  # Usar la lista global de updates
    
    for tag in nomb:
        tag_dir = os.path.join(path, tag)
        if os.path.isdir(tag_dir):  # Verificar que el subdirectorio exista
            for filename in os.listdir(tag_dir):  # Recorrer archivos en el subdirectorio
                # Añadir el tag y el nombre completo del archivo
                updates.append({"tag": tag, "version": filename})
        else: print(f"Directorio {tag_dir} no existe")
    return updates



# Función para subir archivos al servidor
def upload_file(tag, file_name):
    urlFile = os.path.join(url, tag, file_name).replace('\\','/')
    try:
        # Construir la ruta completa al archivo
        file_path = os.path.join(path, tag, file_name).replace('\\','/')

        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.put(urlFile, files=files)

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
    nomb = ["Vega22", "Vega11"]
    updates = deftags(nomb)

    # Subir todos los archivos de la lista de actualizaciones
    for update in updates:
        tag = update["tag"]
        file_name = update["version"]
        upload_file(tag, file_name)
    