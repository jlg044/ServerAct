# ServerAct — Sistema de actualizaciones OTA para robot

Sistema cliente-servidor para distribuir y aplicar actualizaciones remotas (OTA, *Over-The-Air*) de software a un robot, identificando qué archivos han cambiado mediante hash antes de desplegarlos.

---

## Arquitectura

El proyecto se organiza en tres roles independientes:

- **Server/** — Servidor FastAPI que almacena las versiones subidas (organizadas por *tag*, ej. `Vega22`) y una base de datos MariaDB con el historial de versiones y los cambios de cada una.
- **Usuario/** — Herramienta que empaqueta una carpeta local en un `.zip` y la sube al servidor como nueva versión.
- **Robot/** — Cliente que se ejecuta en el robot: consulta al servidor si hay una versión más reciente que la instalada (`version.json`) y descarga solo los archivos necesarios.

```
ServerAct/
├── Server/
│   ├── server.py            # API FastAPI: listar, subir y descargar versiones
│   └── Updater/
│       └── database.py      # Acceso a MariaDB (versiones, etiquetas, cambios)
├── Usuario/
│   └── Updater/
│       └── subirArchivos.py # Empaqueta y sube una nueva versión al servidor
└── Robot/
    ├── use.py
    └── Updater/
        └── descargarArchivos.py # Descarga la última versión disponible
```

---

## Cómo funciona

1. El **usuario** empaqueta el proyecto actualizado en un `.zip` y lo sube al servidor con una etiqueta (`tag`) y número de versión.
2. El **servidor** descomprime el archivo, calcula el hash SHA-256 de cada fichero y lo compara con la versión anterior para saber exactamente qué cambió, y lo registra en MariaDB.
3. El **robot** consulta periódicamente al servidor si existe una versión más reciente que la suya (comparando con su `version.json` local).
4. Si hay una versión nueva, el robot descarga únicamente los archivos modificados desde el servidor.

---

## Tecnologías

- Python
- FastAPI (servidor)
- MariaDB (registro de versiones y cambios)
- Hashing SHA-256 para detección de cambios

---

## Configuración

Cada rol tiene su propio `Updater/updateConfig.py` con la URL del servidor y las rutas de trabajo. El servidor además necesita credenciales de conexión a MariaDB (`UserDB`, `PasswordDB`, `hostDB`, `PortDB`, `DB`) — sustituye los valores de ejemplo por los de tu propia base de datos antes de ejecutarlo.
