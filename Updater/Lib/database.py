import mariadb
import sys
from datetime import date

#Conexión a la base de datos
try:
    conn = mariadb.connect(
        user="root",
        password="1881",
        host="localhost",
        port=3306,
        database="servact"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

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

# Obtiene los tags que se encuentran en la base de datos
def obtenerTags():
    tags = []  # Initialize a list to store tags
    cur.execute("SELECT etiqueta FROM etiquetas")
    for etiqueta in cur:
        tags.append(etiqueta[0])  # Append the first element of the row (the tag)
    return tags

# Comprobar archivos modificados y añadirlos al server
def pre_subir(vers, mod, id_tag):
    
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
            print(v)
    else:
        print("No se encontraron versiones nuevas.")

    return versionesNuevas

    
