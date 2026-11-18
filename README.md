# Sistema de Seguimiento de Envíos

## Descripción del proyecto

Aplicación web desarrollada con Python y Flask para gestionar envíos de pequeños emprendimientos o negocios, permitiendo registrar paquetes, actualizar sus estados y consultar públicamente su seguimiento mediante un código único.

## Funcionalidades principales

### Administración

- Inicio y cierre de sesión.
- Registro de nuevos envíos.
- Generación automática de códigos de seguimiento.
- Visualización de los envíos registrados.
- Actualización del estado de cada envío.
- Registro de observaciones.
- Consulta del historial de movimientos de cada envío.

### Consulta pública

- Búsqueda de envíos mediante código de seguimiento.
- Visualización del estado actual.
- Consulta de la fecha de registro.
- Visualización del historial de actualizaciones y observaciones.

## Tecnologías utilizadas

- Python: desarrollo de la lógica de la aplicación.
- Flask: framework para la construcción del sistema web.
- SQLite: almacenamiento de la información.
- HTML: estructura de las páginas.
- CSS: diseño y estilos de las interfaces.
- Git: control de versiones.
- GitHub: alojamiento del código fuente.

## Estructura del proyecto

```text
seguimiento_envios/
│
├── app.py
├── database.py
├── crear_admin.py
├── requirements.txt
├── .gitignore
│
├── instance/
│   └── envios.db
│
├── static/
│   └── css/
│       └── estilos.css
│
└── templates/
    ├── login.html
    ├── dashboard.html
    ├── registro.html
    └── seguimiento.html
```

La base de datos se genera localmente al iniciar la aplicación. El archivo de base de datos no se incluye en el repositorio.

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/alexanderte/Seguimiento-de-envios.git
```

### 2. Ingresar al directorio

```bash
cd Seguimiento-de-envios
```

### 3. Crear un entorno virtual

```bash
python -m venv venv
```

### 4. Activar el entorno virtual
