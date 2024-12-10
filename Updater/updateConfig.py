from Lib.database import *

#TODAS LAS VARIABLES DEBERIAN SER CONSTANTES??????

#Configuración server
urlServer = "http://127.0.0.1:8000/updates"

#Configuración etiquetas de versiones VEGA
etiquetaVersion = obtenerTags()

#Configuracion de descarga
DOWNLOAD_DIR = './Downloads'

#Directorio del archivo json de version del Robot VEGA
VERSION_DIR = "./version.json"

#Directorio destino a la hora de descargar la ultima version del servidor
UPDATE_DIR = './updatesloc'

