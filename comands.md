# Guía de Comandos de `tidmon`

Esta es una guía de referencia para todos los comandos disponibles en `tidmon`.

---

## Comandos Principales

*   `tidmon [OPCIONES] COMANDO [ARGS]...`

**Opciones Globales:**

*   `--version`: Muestra la versión de `tidmon`.
*   `-v`, `--verbose`: Muestra mensajes de información detallados (INFO).
*   `-d`, `--debug`: Muestra mensajes de depuración (DEBUG).
*   `--help`: Muestra la ayuda para un comando.

---

## `auth`: Autenticación

Gestiona la conexión y el inicio de sesión con tu cuenta de TIDAL.

*   **`tidmon auth`**: Inicia el proceso de autenticación interactivo a través del navegador.
*   **`tidmon logout`**: Elimina las credenciales de autenticación guardadas.
*   **`tidmon whoami`**: Muestra información sobre la sesión actual (usuario, país y tiempo de expiración del token).

---

## `monitor`: Gestionar Artistas y Playlists

El núcleo de `tidmon`. Permite añadir, eliminar y listar los artistas y playlists que quieres supervisar.

*   **`tidmon monitor add [IDENTIFICADORES...] [-f ARCHIVO]`**: Añade uno o más artistas/playlists.
    *   Acepta nombres de artista (ej. "Daft Punk"), IDs de artista, URLs de artista y URLs de playlist.
    *   `--file, -f`: Importa una lista de artistas/playlists desde un archivo de texto (uno por línea).
*   **`tidmon monitor remove [IDENTIFICADORES...]`**: Elimina artistas del monitoreo por nombre o ID.
*   **`tidmon monitor list`**: Muestra una lista de todos los artistas y playlists monitorizados.
*   **`tidmon monitor clear`**: Elimina **todos** los artistas del monitoreo (pide confirmación).
*   **`tidmon monitor export -o [ARCHIVO]`**: Exporta los IDs de artistas y URLs de playlists a un archivo.

---

## `refresh`: Buscar Nuevos Lanzamientos

Comprueba en TIDAL si hay nuevos álbumes o pistas de los artistas y playlists que estás monitoreando.

*   **`tidmon refresh [OPCIONES]`**

**Opciones:**

*   `-D`, `--download`: Descarga automáticamente los nuevos lanzamientos encontrados.
*   `--artist <NOMBRE>`, `-a <NOMBRE>`: Refresca solo un artista específico por su nombre.
*   `--id <ID>`: Refresca solo un artista específico por su ID.
*   `--since <YYYY-MM-DD>`: Refresca solo artistas añadidos *después* de una fecha.
*   `--until <YYYY-MM-DD>`: Refresca solo artistas añadidos *antes* de una fecha.
*   `--album-since <YYYY-MM-DD>`: Procesa solo álbumes lanzados *después* de una fecha.
*   `--album-until <YYYY-MM-DD>`: Procesa solo álbumes lanzados *antes* de una fecha.

---

## `download`: Descargar Música y Vídeos

El sistema de descargas avanzado de `tidmon`.

*   **`tidmon download album <ID_ALBUM> [--force]`**: Descarga un álbum completo por su ID.
*   **`tidmon download artist [ID | "NOMBRE"] [--force]`**: Descarga la discografía completa de un artista.
*   **`tidmon download track <ID_PISTA> [--force]`**: Descarga una única pista por su ID.
*   **`tidmon download url <URL_TIDAL> [--force]`**: Descarga desde una URL de TIDAL (álbum, artista, pista, etc.).
*   **`tidmon download monitored [OPCIONES]`**: Descarga todos los álbumes pendientes de los artistas monitorizados.
    *   Opciones: `--force`, `--since <FECHA>`, `--until <FECHA>`, `--dry-run`, `--export <ARCHIVO>`, `--also-download`
*   **`tidmon download all [OPCIONES]`**: Descarga **todos** los álbumes de la base de datos, sin importar su estado.
    *   Opciones: `--force`, `--dry-run`, `--resume`, `--since <FECHA>`, `--until <FECHA>`, `--export <ARCHIVO>`, `--also-download`

**Opciones Comunes de Descarga:**

*   `--force`: Vuelve a descargar el contenido aunque el archivo ya exista.
*   `--dry-run`: Muestra lo que se descargaría, pero sin realizar la descarga real.
*   `--resume`: Reanuda una descarga masiva (`download all`), omitiendo los álbumes ya completados.
*   `--since <FECHA>` / `--until <FECHA>`: Filtra los álbumes a procesar por su fecha de lanzamiento.
*   `--export <ARCHIVO>`: En lugar de descargar, exporta las URLs de los álbumes filtrados a un archivo.
*   `--also-download`: Usado con `--export`, descarga los álbumes *además* de exportar sus URLs.

---

## `config`: Configuración

Permite ver y modificar la configuración de `tidmon`.

*   **`tidmon config show`**: Muestra toda la configuración actual.
*   **`tidmon config get <CLAVE>`**: Obtiene el valor de una clave específica.
*   **`tidmon config set <CLAVE> <VALOR>`**: Establece un nuevo valor para una clave.
*   **`tidmon config path`**: Muestra la ruta al archivo `config.json`.

---

## Otros Comandos

*   **`tidmon search <CONSULTA> [-t TIPO] [-l LIMITE]`**: Busca en TIDAL. `TIPO` puede ser `artists`, `albums` o `tracks`.
*   **`tidmon show`**: Muestra datos de la base de datos local (artistas, lanzamientos, álbumes).
*   **`tidmon backup`**: Gestiona la creación y restauración de copias de seguridad de tus datos.

---

## Ejemplos de Uso

Combinaciones de comandos para flujos de trabajo comunes.

**Refrescar y descargar automáticamente:**
```bash
# Busca nuevos lanzamientos de todos tus artistas y descarga lo nuevo
tidmon refresh --download
```

**Reanudar una descarga masiva con información detallada:**
```bash
# Continúa una descarga masiva, saltando álbumes ya completados.
# El modo -v (verbose) mostrará qué álbumes específicos se están omitiendo.
tidmon download all --resume -v
```

**Exportar URLs de todos los álbumes de 2023:**
```bash
# Filtra todos los álbumes de la base de datos lanzados en 2023 y guarda sus URLs en un archivo.
tidmon download all --since 2023-01-01 --until 2023-12-31 --export albums_2023.txt
```

**Descargar los álbumes pendientes de este mes Y exportar la lista:**
```bash
# Descarga los álbumes pendientes lanzados desde el 1ro de este mes y también guarda sus URLs.
# (Requiere un shell compatible como bash o git-bash para el comando 'date')
tidmon download monitored --since $(date +%Y-%m-01) --export monthly_pending.txt --also-download
```

**Hacer una copia de seguridad antes de una operación mayor:**
```bash
# Crea un backup con fecha antes de limpiar la lista de monitoreo
tidmon backup create -o backup_before_clear.zip
tidmon monitor clear
```
