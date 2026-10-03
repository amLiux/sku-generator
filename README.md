GF SKU Generator

Herramienta interactiva de terminal (TUI) para generar y administrar SKUs de productos de GF.

La aplicación utiliza un archivo local db.json como base de datos, por lo que no requiere ningún servidor ni configuración adicional.

Requisitos

Python 3.11 o superior

uv

Instalación

Clona el repositorio y ejecuta:

uv sync


Esto instalará automáticamente las dependencias del proyecto.

Ejecutar la aplicación
uv run sku


También puedes ejecutarla directamente como módulo de Python:

uv run python -m gf_sku

Formato del SKU

El formato actual del SKU es:

GF-DROP-CAT-SUB-BASE-DESIGN-CLR-SZ


Por ejemplo:

GF-D1-TS-OVS-BLK-GR1-WHT-M


Cada componente representa:

Componente	Significado	Ejemplo
GF	Marca	GF
DROP	Número de drop	D1
CAT	Categoría	TS
SUB	Subcategoría	OVS
BASE	Color base del producto	BLK
DESIGN	Tipo de diseño	GR1
CLR	Color del diseño	WHT
SZ	Talla	M
Ejemplo completo
GF-D1-TS-OVS-BLK-GR1-WHT-M


Significa:

GF → GF

D1 → Drop 1

TS → Camiseta

OVS → Oversized

BLK → Negro

GR1 → Diseño gráfico

WHT → Diseño blanco

M → Talla Medium

Flujo de creación

La aplicación guía al usuario paso a paso:

Drop

Categoría

Subcategoría

Color base

Tipo de diseño

Color del diseño

Talla

Revisión del SKU

Guardar

En cada paso se muestran las opciones que ya existen en el catálogo.

También existe la opción:

+ Add new


para crear un nuevo valor directamente desde la aplicación.

Por ejemplo:

Base Color

  BLK — Black
  WHT — White
  GRY — Grey
  + Add new


Si se introduce:

Dark Blue


el sistema lo normaliza automáticamente a:

DARK-BLUE


y lo agrega al catálogo.

Base de datos local

Toda la información se almacena en:

db.json


No se necesita SQLite, PostgreSQL ni ningún servidor para utilizar esta versión.

El archivo contiene tanto los catálogos como los productos creados:

{
  "categories": [],
  "subcategories": [],
  "base_colors": [],
  "designs": [],
  "design_colors": [],
  "sizes": [],
  "products": []
}


La aplicación actualiza automáticamente este archivo cuando:

Se agrega una nueva opción al catálogo.

Se crea un nuevo producto.

Se guarda un nuevo SKU.

Validación

Todos los valores introducidos manualmente pasan por un proceso de normalización y validación antes de entrar al catálogo.

Por ejemplo:

dark blue       → DARK-BLUE
Dark Blue       → DARK-BLUE
dark_blue       → DARK-BLUE
 dark blue      → DARK-BLUE
red/white       → RED-WHITE


Los códigos pueden contener:

A-Z
0-9
-


No se permiten:

Espacios.

Caracteres especiales.

-- consecutivos.

- al inicio.

- al final.

La idea es que cualquier valor almacenado en el catálogo pueda utilizarse directamente dentro de un SKU.

Evitar SKUs duplicados

Antes de guardar un producto, la aplicación verifica si el SKU ya existe.

Por ejemplo, si ya existe:

GF-D1-TS-OVS-BLK-GR1-WHT-M


el sistema no permitirá crear otro producto con el mismo SKU.

Estructura del proyecto
gf-sku/
├── db.json
├── pyproject.toml
├── README.md
└── src/
    └── gf_sku/
        ├── __init__.py
        ├── __main__.py
        ├── app.py
        ├── database.py
        └── validation.py

app.py

Contiene la interfaz TUI y el flujo de creación del SKU.

database.py

Maneja la lectura y escritura de db.json, además de las operaciones sobre productos y catálogos.

validation.py

Contiene la lógica para normalizar y validar los códigos utilizados por los SKUs.

db.json

Es la base de datos local de la aplicación.

Desarrollo

Para instalar las dependencias:

uv sync


Para ejecutar:

uv run sku


Para ejecutar como módulo:

uv run python -m gf_sku


Para inspeccionar la base de datos:

cat db.json


En Windows PowerShell:

Get-Content db.json

Próximos pasos

La primera versión está enfocada en generar SKUs rápidamente y mantener un catálogo local.

Algunas mejoras previstas:

Hacer que las subcategorías dependan de la categoría seleccionada.

Detectar automáticamente cuándo una categoría no utiliza talla y asignar NA.

Permitir editar y eliminar opciones del catálogo.

Permitir editar productos existentes.

Mejorar la navegación con teclado.

Agregar búsqueda dentro de catálogos grandes.

Agregar confirmación antes de modificar el catálogo.

Exportar productos a CSV.

Agregar tests automatizados.

Eventualmente separar el motor de generación de SKU de la interfaz TUI para poder reutilizarlo en otros contextos.