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

# Añadir al server los archivos modificados
def subirVersion(vers, camb):
    # vers es el nombre de la versión 
    # camb es un formato JSON o un objeto serializable
    
    print(camb)  # Debug para verificar qué se está intentando insertar

    try:
        # Serialización JSON y asegurarte de que sea una cadena
        camb_json = json.dumps(camb)
    except TypeError as e:
        print(f"Error al serializar JSON: {e}")
        return {"error": "Error al procesar los cambios."}

    conn.begin()
    try:
        cur.executemany(
            "INSERT INTO versiones (version, cambios, fecha) VALUES (?, ?, ?)", 
            [(vers, camb_json, date.today())]  # Asegúrate de que sea una lista de tuplas
        )
    except mariadb.Error as e: 
        print(f"Gran Error: {e}")
        conn.rollback()
        return {"message": "Error al insertar la nueva version."}


    # Obtener id de la versión insertada
    id_version = ObtenerIdVersion(vers)

    # Subir la relación de la nueva etiqueta con su tag
    tagArray = vers.split("_v")

    id_tag = ObtenerIdTag(tagArray[0])

    try:
        cur.executemany(
            "INSERT INTO version_etiqueta (id_versiones, id_tag) VALUES (?, ?)",
            [(id_version, id_tag[0])]
        )
    except mariadb.Error as e: 
        print(f"Super Error: {e}")
        conn.rollback()
        return {"message": "Error al insertar las ids de version_etiqueta."}
    
    conn.commit()

    return {"message": "Versión y etiquetas insertadas correctamente."}, 200

    
#------------------------------------------------------------------------------------------------------------#

# Downloads Tools

def ObtenerIdVersion(vers):
    print(vers)
    cur.execute("SELECT id FROM versiones WHERE version = ?", (vers,))
    id_version = cur.fetchone()

    id_version = id_version[0]
    print(id_version)
    return id_version

def ObtenerIdTag(tag):
    cur.execute("SELECT id FROM etiquetas WHERE etiqueta = ?", (tag,))
    id_tag = cur.fetchone()  # Usamos fetchone() porque esperamos un único resultado

    if id_tag == None:
        subirTags(tag)
        cur.execute("SELECT id FROM etiquetas WHERE etiqueta = ?", (tag,))
        id_tag = cur.fetchone()  # Usamos fetchone() porque esperamos un único resultado

    return id_tag

# Obtiene los tags que se encuentran en la base de datos
def obtenerTags():
    tags = []  # Initialize a list to store tags
    cur.execute("SELECT etiqueta FROM etiquetas")
    for etiqueta in cur:
        tags.append(etiqueta[0])  # Append the first element of the row (the tag)
    return tags

#Obtiene las versiones que se encuentran en el servidor para un tag concreto
def listVersions(tag):
    version = []  # Initialize a list to store tags
    id_t = ObtenerIdTag(tag)

    # Comprobar si hay nuevas actualizaciones
    cur.execute("SELECT v.version FROM versiones v "
                "JOIN version_etiqueta ve ON v.id = ve.id_versiones "
                "JOIN etiquetas e ON ve.id_tag = e.id WHERE e.id = ?", id_t)

    versiones = cur.fetchall()  # Obtenemos todas las versiones correspondientes a la etiqueta

    for vers in versiones:
        version.append(vers)

    return version

#Comprueba si hay actualizaciones
def comprobarActualizacion(tag, versAct):
    versionesNuevas = []
    print(versAct)
    print(tag)
    # Obtener ids de la version actual del robot   
    versiones = listVersions(tag)
    print(versiones)

    for vers in versiones:
        if versAct < vers[0]:  # Comparar las versiones
            print(versAct)
            print(vers[0])
            print(versAct < vers[0])
            versionesNuevas.append(vers)
    
    # Mostrar las versiones nuevas
    if versionesNuevas:
        print("Versiones nuevas encontradas:")
        for v in versionesNuevas:
            print(v[0])
    else:
        print("No se encontraron versiones nuevas.")

    cambios = ObtenerJsonVersiones(versionesNuevas)

    return cambios

#Obtiene el json de las versiones disponibles para actualizar
def ObtenerJsonVersiones(versionesNuevas):
    data = {}  # Diccionario para almacenar todos los JSONs

    for version in versionesNuevas:
        # Ejecutar la consulta para obtener los cambios relacionados con la versión
        cur.execute("SELECT cambios FROM versiones WHERE version =?", (version[0],))
        json_resultados = cur.fetchall()  # Obtener los resultados de los cambios
        
        for j in json_resultados:
            # Verificar que j no sea None
            if j:
                # Limpiar la cadena y convertir a un diccionario
                json_string = j[0].strip()
                try:
                    json_data = json.loads(json_string)  # Convertir cadena JSON a diccionario
                    # Fusionar JSON al diccionario utilizando el valor de la versión como clave
                    if version[0] in data:
                        data[version[0]].update(json_data)
                    else:
                        data[version[0]] = json_data  # Si la clave no existe, crearla
                except json.JSONDecodeError as e:
                    print(f"Error al procesar JSON: {str(e)}")

    return data