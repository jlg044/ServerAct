from fastapi import APIRouter, File, UploadFile, HTTPException
import os

upload_router = APIRouter()

# Directorio base para guardar actualizaciones
UPDATE_DIR:str = "./static"
os.makedirs(UPDATE_DIR, exist_ok=True)

@upload_router.post("/")
async def upload_update(tag: str, version: str, file: UploadFile = File(...)):
    """
    Sube un archivo de actualización, organizándolo por etiqueta y versión.
    """
    # Crear directorio para la etiqueta si no existe
    tag_dir:str = os.path.join(UPDATE_DIR, tag)
    os.makedirs(tag_dir, exist_ok=True)

    # Construir ruta para guardar el archivo
    file_path:str = os.path.join(tag_dir, f"{version}-{file.filename}")

    # Guardar el archivo
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    return {"message": "Archivo subido exitosamente", "path": file_path}
