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
    # mod es un json con los archivos modificados
    
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
    
