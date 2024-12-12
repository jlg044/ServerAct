import server as sv
import Updater.updateConfig as up
import os
import requests

#Subir los tags
#tag es una tupla
#tag = "Vega22" , "Vega11"
#subirTags(tag)

#Descargar los tags
#tags = []
#tags = obtenerTags()
#print(tags)


#Obtener versiones actualizadas
def verNuevo():
    cambios = sv.compAct("Vega22", "Vega22_v1.0.0")
    if(cambios == 0):
        return "No se ha descargado nada"
    print("Cambios encontrados:")
    print(cambios)
    
    # Iterar sobre cada versión en el diccionario
    for data in cambios.items():
        tag = data.get('tag', '')
        print(f"Tag: {tag}")
        
        version_num = data.get('path', '').split('/')[1]  # Extraer el número de versión del path
        print(f"Versión: {version_num}")
        
        filename = data.get('filename', '')
        print(f"Filename: {filename}")
        
        path = up.UPDATE_DIR + data.get('path', '') + "/" + filename
        print(f"Path: {path}")
        
        # Descargar archivo
        download_file(tag, version_num, filename, path)

def download_file(modelo, version, filename, path):
    url = up.urlServer + "/" + path
    print(url)
    # Crear la ruta completa para guardar el archivo en su carpeta correspondiente
    local_path = os.path.join(up.DOWNLOAD_DIR, modelo, version, filename).replace('\\','/')
    print(local_path)
    # Asegurar que la carpeta correspondiente exista
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    try:
        response = requests.get(url, stream=True)  # Usar stream=True para archivos grandes
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):  # Escribir en partes
                    file.write(chunk)
            print(f"Archivo {filename} descargado correctamente en {local_path}.")
        else:
            print(f"Error al descargar {modelo}-{version}-{filename}: {response.text}")
    except requests.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")

# Main
if __name__ == '__main__':
    verNuevo()