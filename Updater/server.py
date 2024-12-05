from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import json
import updateConfig as up

app = FastAPI()

# Directorio donde se almacenarán las actualizaciones
UPDATE_DIR = up.UPDATE_DIR
os.makedirs(UPDATE_DIR, exist_ok=True)

# Montar directorio estático para servir archivos
app.mount("/updatesloc", StaticFiles(directory=UPDATE_DIR), name="static")

# Archivo de índice para registrar versiones
INDEX_FILE = os.path.join(UPDATE_DIR, "index.json")

# Inicializar el archivo de índice si no existe
if not os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, 'w') as f:
        json.dump({}, f)

# Cargar índice desde archivo
def load_index():
    with open(INDEX_FILE, 'r') as f:
        return json.load(f)

# Guardar índice en archivo
def save_index(index):
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=4)

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
    """Descarga un archivo específico."""
    file_path = os.path.join(UPDATE_DIR, tag, version)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Archivo no encontrado"}

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

    # Actualizar el índice (opcional, ya que ahora usamos carpetas)
    index = load_index()
    if tag not in index:
        index[tag] = []
    if version not in index[tag]:
        index[tag].append(version)
        save_index(index)

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

    # Actualizar el índice (opcional, ya que ahora usamos carpetas)
    index = load_index()
    if tag not in index:
        index[tag] = []
    if version not in index[tag]:
        index[tag].append(version)
        save_index(index)

    return {"message": f"Archivo {version} subido correctamente en la carpeta {tag}."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
