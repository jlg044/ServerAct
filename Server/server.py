from datetime import date
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import updateConfig as up

#Main

app = FastAPI()

#Directorio donde se almacenarán las actualizaciones
UPDATE_DIR = up.UPDATE_DIR
os.makedirs(UPDATE_DIR, exist_ok=True)

# Montar directorio estático para servir archivos
app.mount(UPDATE_DIR, StaticFiles(directory=UPDATE_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


#Conections
    #Get Zone

    # Ruta para listar las versiones disponibles para un tag
@app.get("/updates/{tag}")
async def list_updates(tag: str):
    """Devuelve todas las versiones disponibles para un tag."""
    tag_dir = os.path.join(UPDATE_DIR, tag)
    if os.path.isdir(tag_dir):
        versions = os.listdir(tag_dir)
        return versions
    return []

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
# Ruta para subir un archivo de actualización
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
async def upload_update(tag: str, version: str, full_path: str, file: UploadFile = File(...)):

    """Sube un archivo al servidor y lo organiza por carpetas según el tag."""
    target_path = os.path.join(UPDATE_DIR, tag, version, full_path)
    os.makedirs(target_path, exist_ok=True)

    file_path = os.path.join(target_path, file.filename)
    
    # Guardar el archivo subido
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {"message": f"Archivo {version} subido correctamente en la carpeta {tag}."}

# Ruta para subir un archivo de actualización
@app.put("/updates/{tag}/{version}")
async def upload_update(tag: str, version: str, file: UploadFile = File(...)):

    """Sube un archivo al servidor y lo organiza por carpetas según el tag."""
    target_path = os.path.join(UPDATE_DIR, tag, version)
    os.makedirs(target_path, exist_ok=True)

    file_path = os.path.join(target_path, file.filename)
    
    # Guardar el archivo subido
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {"message": f"Archivo {version} subido correctamente en la carpeta {tag}."}


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

# Obtener Tags de la base de datos
def obtTags():
    tags = up.obtenerTags()
    return tags

# Subir Tags a la base de datos
def subTags(tags):
    up.subirTags(tags)

def compAct(tag, versAct):
    cambios = up.comprobarActualizacion(tag, versAct)    
    return cambios