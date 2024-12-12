import mariadb
import sys
from datetime import date
import json
import Updater.updateConfig as up

#------------------------------------------------------------------------------------------------------------#

#Conexion to the database

try:
    conn = mariadb.connect(
        user= up.UserDB,
        password=up.PasswordDB,
        host=up.hostDB,
        port=up.PortDB,
        database=up.DB

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

#------------------------------------------------------------------------------------------------------------#

# Uploads Tools

# Añadir etiquetas a la base de datos
def subirTags(tags):
    # Ensure `tags` is a list of tuples, where each tuple contains a single tag
    if isinstance(tags, str):  # Handle the case where a single string is passed
        tags = [(tags,)]
    else:
        tags = [(tag,) for tag in tags]
    try:
        cur.executemany(
            "INSERT INTO etiquetas (etiqueta) VALUES (?)", 
            tags  # Pass list of tuples
        )
    except mariadb.Error as e: 
        print(f"Error: {e}")
    
    conn.commit() 
    print(f"Last Inserted ID: {cur.lastrowid}")

# Comprobar archivos modificados y añadirlos al server
def subirVersion(vers, mod, id_tag):
    
    # vers es el nombre de la version 
    # mod es un formato json con el nombre de los archivos modificados
    
    try:
        cur.executemany(
            "INSERT INTO versiones (version, archivo, fecha) VALUES (?)", 
            (vers, mod, date())  # Pass list of tuples
        )

    except mariadb.Error as e: 
        print(f"Error: {e}")
        conn.commit() 


    try:
        cur.executemany("INSERT INTO version_etiqueta (id_versiones, id_tag) VALUES (?)",
            (cur.execute("SELECT id FROM versiones WHERE version = ?", (vers)), id_tag)
        )
        
    except mariadb.Error as e: 
        print(f"Error: {e}")
        
        conn.commit() 
    
#------------------------------------------------------------------------------------------------------------#

# Downloads Tools

# Obtiene los tags que se encuentran en la base de datos
def obtenerTags():
    tags = []  # Initialize a list to store tags
    cur.execute("SELECT etiqueta FROM etiquetas")
    for etiqueta in cur:
        tags.append(etiqueta[0])  # Append the first element of the row (the tag)
    return tags

def comprobarActualizacion(tag, versAct):
    # Obtener ids de la version actual del robot
    cur.execute("SELECT id FROM etiquetas WHERE etiqueta = ?", (tag,))
    id_t = cur.fetchone()  # Usamos fetchone() porque esperamos un único resultado

    if not id_t:  # Verificar si los resultados son válidos
        print("No se encontraron registros para la etiqueta o versión")
        return

    # Comprobar si hay nuevas actualizaciones
    cur.execute("SELECT v.* FROM versiones v "
                "JOIN version_etiqueta ve ON v.id = ve.id_versiones "
                "JOIN etiquetas e ON ve.id_tag = e.id WHERE e.id = ?", id_t)

    versiones = cur.fetchall()  # Obtenemos todas las versiones correspondientes a la etiqueta
    versionesNuevas = []

    for vers in versiones:
        if versAct < vers[1]:  # Comparar las versiones
            versionesNuevas.append(vers)
    
    # Mostrar las versiones nuevas
    if versionesNuevas:
        print("Versiones nuevas encontradas:")
        for v in versionesNuevas:
            print(v[1])
    else:
        print("No se encontraron versiones nuevas.")

    respuesta = input("¿Quieres descargarlas actualizaciones? (s/n): ").strip().lower()
    if respuesta in ['s', 'n', '']:
        if respuesta == 's' or respuesta == '':
            print("Iniciando la descarga...")
            cambios = descargarActualizaciones(versionesNuevas)
        else:
            print("Descarga cancelada.")
            return 0
    else:
        print("Respuesta no válida. Por favor, ingresa 'S' para sí o 'n' para no.")

    return cambios

def descargarActualizaciones(versionesNuevas):
    data = {}  # Diccionario para almacenar todos los JSONs

    for version in versionesNuevas:
        # Ejecutar la consulta para obtener los cambios relacionados con la versión
        cur.execute("SELECT cambios FROM versiones WHERE version =?", (version[1],))
        json_resultados = cur.fetchall()  # Obtener los resultados de los cambios
        
        for j in json_resultados:
            # Verificar que j no sea None
            if j:
                # Limpiar la cadena y convertir a un diccionario
                json_string = j[0].strip()
                try:
                    json_data = json.loads(json_string)  # Convertir cadena JSON a diccionario
                    # Fusionar JSON al diccionario utilizando el valor de la versión como clave
                    if version[1] in data:
                        data[version[1]].update(json_data)
                    else:
                        data[version[1]] = json_data  # Si la clave no existe, crearla
                except json.JSONDecodeError as e:
                    print(f"Error al procesar JSON: {str(e)}")

    return data