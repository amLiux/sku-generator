# GF SKU Generator

CLI interactivo para generar y registrar SKUs de productos de GF.

El proyecto mantiene un catálogo local en `db.json` y utiliza un wizard paso a paso para construir cada SKU de forma consistente.

## Stack

- **Python 3.11+**
- **uv** — gestión del entorno y dependencias
- **Questionary** — wizard interactivo
- **Rich** — presentación y formato de la terminal
- **JSON** — almacenamiento local

## Requisitos

Necesitas Python y `uv`.

### Python

Descarga Python desde:

https://www.python.org/downloads/

Comprueba la instalación:

```bash
python3 --version
```

### uv

`uv` es el gestor de proyectos y entornos Python utilizado por este proyecto.

Documentación oficial:

https://docs.astral.sh/uv/

En macOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Comprueba la instalación:

```bash
uv --version
```

## Instalación

### Desde GitHub

Clona el repositorio:

```bash
git clone <REPOSITORY_URL>
cd sku-generator
```

Instala las dependencias:

```bash
uv sync
```

Ejecuta el programa:

```bash
uv run python main.py
```

### Sin GitHub

Si recibiste el proyecto como una carpeta o un `.zip`, entra en la carpeta del proyecto:

```bash
cd sku-generator
```

Instala las dependencias:

```bash
uv sync
```

Ejecuta el programa:

```bash
uv run python main.py
```

No necesitas crear manualmente un virtual environment. `uv` se encarga de crear y utilizar `.venv`.

## Uso

Al iniciar el programa aparecerá un wizard interactivo:

```text
GF · SKU GENERATOR

SKU actual
GF

Step 1/7

? Drop
❯ D1 · Drop 1
  D2 · Drop 2
  ＋ Crear nuevo
```

El SKU se va construyendo conforme avanzas:

```text
GF
GF-D1
GF-D1-TS
GF-D1-TS-OVS
GF-D1-TS-OVS-BLK
GF-D1-TS-OVS-BLK-GR1
GF-D1-TS-OVS-BLK-GR1-WHT
GF-D1-TS-OVS-BLK-GR1-WHT-M
```

Al finalizar se valida que el SKU no exista y se solicita confirmación antes de guardarlo.

## Catálogo local

Los valores disponibles se almacenan en:

```text
db.json
```

Si durante el wizard eliges:

```text
＋ Crear nuevo
```

el nuevo valor se valida, normaliza y agrega automáticamente al catálogo.

Por ejemplo:

```text
Dark Blue
```

se convierte en:

```text
DARK-BLUE
```

y queda disponible para futuros SKUs.

Los productos creados también se registran en `db.json`.

## Estructura

```text
sku-generator/
├── db.json
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Ejecutar nuevamente

La forma recomendada es:

```bash
uv run python main.py
```

No necesitas activar `.venv` manualmente.

Si prefieres activarlo:

### macOS / Linux

```bash
source .venv/bin/activate
python main.py
```

### Windows

```powershell
.venv\Scripts\activate
python main.py
```

## Desarrollo

Actualizar dependencias:

```bash
uv sync
```

Agregar una dependencia:

```bash
uv add nombre-del-paquete
```

Eliminar una dependencia:

```bash
uv remove nombre-del-paquete
```

## Licencia

Uso interno de GF.