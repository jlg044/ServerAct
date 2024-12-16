from datetime import date
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import Updater.updateConfig as up
import Updater.database as db
import hashlib
import logging

# Configurar logging básico

logging.basicConfig(
    level=logging.DEBUG,  # Nivel de log: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Muestra los logs en la terminal
    ]
)

logger = logging.getLogger(__name__)

#Main

app = FastAPI()
cambios = []

#Directorio donde se almacenarán las actualizaciones
UPDATE_DIR = up.UPDATE_DIR
os.makedirs(UPDATE_DIR, exist_ok=True)
updateMount = UPDATE_DIR.split(".")[1]
# Montar directorio estático para servir archivos
app.mount(updateMount, StaticFiles(directory=UPDATE_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True, log_level="debug")  # Nivel de logs

#Conections
    #Get Zone

    # Ruta para listar las versiones disponibles para un tag
@app.get("/updates/{tag}")
async def list_updates(tag: str):
    """Devuelve todas las versiones disponibles para un tag."""
    versiones = []
    versiones = db.listVersions(tag)
    return versiones
    
    #tag_dir = os.path.join(UPDATE_DIR, tag)
    #if os.path.isdir(tag_dir):
    #    versions = os.listdir(tag_dir)
    #    return versions
    #return []

# Ruta para descargar una versión específica de un tag
@app.get("/updates/{tag}/{version}")
async def download_update(tag: str, version: str):
    updates = []
    file_path = os.path.join(UPDATE_DIR, tag, version)
    if os.path.exists(file_path):


        if os.path.isdir(file_path):  # Verificar que el subdirectorio exista
            iteracionArchivos(file_path,tag, updates)
        else: print(f"Directorio {file_path} no existe")
        upd = updates
        return upd
        
            #return FileResponse(file_path)
    return {"error": "Archivo no encontrado"}



    """Devolver diccionario con rutas a descargar."""
# Ruta para descargar un archivo de actualización
@app.get("/updates/{tag}/{version}/{full_path:path}")
async def download_file(tag: str, version: str, full_path: str):
    """Descarga un archivo específico."""
    file_path = os.path.join(UPDATE_DIR, tag, version,full_path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Archivo no encontrado"}


    #Put Zone

# Ruta para subir un archivo de actualización
@app.put("/updates/{tag}/{version}/{full_path:path}")
async def upload_update(tag: str, version: str, full_path: str, file: UploadFile = File(...), end: bool=False):

    """Sube un archivo al servidor y lo organiza por carpetas según el tag."""
    logger.info(f"Iniciando subida de archivo: {file.filename}, tag: {tag}, version: {version}, path: {full_path}, end: {end}")
    global cambios
    try:
        # Crear el directorio si no existe
        target_path = os.path.join(UPDATE_DIR, tag, version, full_path)
        logger.debug(f"Creando directorio en: {target_path}")
        os.makedirs(target_path, exist_ok=True)

        # Construir la ruta completa del archivo
        file_path = os.path.join(target_path, file.filename)
        logger.debug(f"Ruta completa del archivo: {file_path}")

        # Guardar el archivo subido
        with open(file_path, "wb") as f:
            logger.info(f"Guardando archivo {file.filename} en: {file_path}")
            f.write(await file.read())

        logger.info(f"Archivo {file.filename} guardado correctamente.")

        # Comparar el archivo subido con las versiones anteriores
        logger.debug(f"Iniciando comparación de archivos para: {file.filename}")
        #filesComparator(tag, file.filename, full_path,version)

        if end:
            logger.info(f"Marcando como finalizada la subida para la versión {version}. Actualizando base de datos.")
            insertUploadOnDB(version)
            cambios = []  # Reiniciar cambios
            logger.debug(f"Cambios reiniciados.")

        return {"message": f"Archivo {version} subido correctamente en la carpeta {tag}."}

    except Exception as e:
        logger.error(f"Error durante la subida del archivo {file.filename}: {e}")
        return {"error": "Ocurrió un error durante la subida."}


# Ruta para subir un archivo de actualización
@app.put("/updates/{tag}/{version}")
async def upload_update(tag: str, version: str, file: UploadFile = File(...), end: bool=False):

    """Sube un archivo al servidor y lo organiza por carpetas según el tag."""
    logger.info(f"Inicio de la subida: tag={tag}, version={version}, end={end}")
    global cambios
    try:
        # Crear el directorio si no existe
        target_path = os.path.join(UPDATE_DIR, tag, version)
        logger.info(f"targetPath: {target_path}")
        os.makedirs(target_path, exist_ok=True)
        logger.debug(f"Directorio creado/existente en: {target_path}")

        # Construir la ruta completa del archivo
        file_path = os.path.join(target_path, file.filename)
        logger.debug(f"Ruta completa del archivo: {file_path}")

        # Guardar el archivo subido
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"Archivo guardado correctamente en: {file_path}")

        # Llamar al comparador de archivos
        full_path = ""
        filesComparator(tag, file.filename, full_path,version)
        logger.debug(f"Comparación de archivos completada para: {file.filename}")

        # Si es la última iteración, actualizar la base de datos
        if end:
            insertUploadOnDB(version)
            cambios = []  # Reiniciar cambios
            logger.info(f"Base de datos actualizada para la versión: {version}")

        return {"message": f"Archivo {version} subido correctamente en la carpeta {tag}."}

    except Exception as e:
        logger.error(f"Error durante la subida del archivo: {e}")
        return {"error": "Ocurrió un error durante la subida."}


#Utilities Tools

#Iterar directorios para guardar todos los archivos en UPDATES.
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

def insertUploadOnDB(version):
    global cambios
    db.subirVersion(version, cambios)

def filesComparator(tag,filename,path,versionAct):


    #Get ultima version
    ultimaVersion = db.listVersions(tag)
    if ultimaVersion == []:
        if path == "":
            pathCambios = os.path.join(tag,versionAct).replace('\\','/')
        else:
            pathCambios = os.path.join(tag,versionAct,path).replace('\\','/')
        cambios.append(

            {"tag": tag, 
            "path": pathCambios,
            "filename": filename
            })
        return 
    else:
        ultimaVersion = ultimaVersion[-1]
        nuevaVersion = versionAct

    if path == "":
    
        pathUV =  os.path.join(up.UPDATE_DIR,tag,ultimaVersion,filename).replace('\\','/')
    
        pathCambios = os.path.join(tag,ultimaVersion).replace('\\','/')
    
        pathNV = os.path.join(up.UPDATE_DIR,tag,nuevaVersion,filename).replace('\\','/')
    else:

        pathUV =  os.path.join(up.UPDATE_DIR,tag,ultimaVersion,path,filename).replace('\\','/')
    
        pathCambios = os.path.join(tag,ultimaVersion,path).replace('\\','/')
    
        pathNV = os.path.join(up.UPDATE_DIR,tag,nuevaVersion,path,filename).replace('\\','/')

    hashUV = HashCreator(pathUV)
    hashNV = HashCreator(pathNV)
    if (hashUV == hashNV):
        print("Correcto Funcionamiento")
    else:
        print(f"\n\n\nSe ha detectado una modificacion!!: {pathNV}\n\n\n")
        cambios.append(

            {"tag": tag, 
            "path": pathCambios,
            "filename": filename
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


# Obtener Tags de la base de datos
def obtTags():
    tags = db.obtenerTags()
    return tags

# Subir Tags a la base de datos
def subTags(tags):
    db.subirTags(tags)

def compAct(tag, versAct):
    cambios = db.comprobarActualizacion(tag, versAct)    
    return cambios