from fastapi import APIRouter, HTTPException
import os

fetch_router = APIRouter()

# Directorio base para buscar actualizaciones
UPDATE_DIR:str = "./static"

@fetch_router.get("/{tag}")
def get_updates(tag: str):
    """
    Lista las versiones disponibles para una etiqueta.
    """
    tag_dir:str = os.path.join(UPDATE_DIR, tag)
    if not os.path.exists(tag_dir):
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    
    versions:str = os.listdir(tag_dir)
    return {"tag": tag, "versions": versions}

@fetch_router.get("/{tag}/{version}")
def download_update(tag: str, version: str):
    """
    Genera la ruta de descarga para una versión específica.
    """
    tag_dir:str = os.path.join(UPDATE_DIR, tag)
    files = [f for f in os.listdir(tag_dir) if f.startswith(version)]
    if not files:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    # En este ejemplo, devolvemos solo el primer archivo coincidente
    file_path:str = os.path.join(tag_dir, files[0])
    return {"message": "Archivo listo para descarga", "path": file_path}
