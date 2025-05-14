# Sistema de Registro de Asistencia

Este sistema de asistencia está destinado para el laboratorio de Metal Mecánica (DNICYT) situado en Alto Irpavi de la Escuela Militar de Ingeniería, desarrollado por Alvaro Encinas.

## Descripción

Sistema de registro y control de asistencia con interfaz web que permite gestionar la entrada y salida de personal en el laboratorio de Metal Mecánica. Esta aplicación está desarrollada con Flask y proporciona una solución completa y fácil de usar para la administración de asistencia del personal.

## Estructura del Proyecto

```
sistema_de_registro_de_asistencia/
│
├── static/images/           # Imágenes y recursos estáticos 
├── templates/               # Plantillas HTML para la interfaz web
├── .gitignore               # Archivos y directorios ignorados por Git
├── README.md                # Este archivo de documentación
├── app.py                   # Aplicación principal Flask
├── attendance.db            # Base de datos SQLite para el registro de asistencia
├── database.py              # Módulo para interactuar con la base de datos
├── requirements.txt         # Dependencias del proyecto
└── server_manager.py        # Gestor para iniciar/detener el servidor en producción
```

## Características

- **Registro de entrada y salida**: Control de asistencia con registro de fechas y horas exactas
- **Interfaz web amigable**: Diseño frontend intuitivo y responsivo
- **Base de datos SQLite**: Almacenamiento eficiente y portable
- **Modo de producción**: Sistema de despliegue simple con gestor de servidor incluido
- **Funcionalidad completa**: Incluye todas las operaciones necesarias para la gestión de asistencia

## Requisitos

- Python 3.6 o superior
- Git (para gestión de versiones)
- Bash y WSL (para algunas funcionalidades en entorno Windows)
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clone el repositorio:
   ```
   git clone [url-del-repositorio]
   ```

2. Instale las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Inicialice la base de datos (si es necesario):
   ```
   python database.py
   ```

## Uso

### Modo Desarrollo

Para ejecutar el sistema en modo desarrollo:

```
python app.py
```

### Modo Producción

El sistema incluye un gestor de servidor para facilitar el despliegue en producción:

1. Ejecute el gestor de servidor:
   ```
   python server_manager.py
   ```

2. Utilice la interfaz del gestor para:
   - Iniciar el servidor
   - Detener el servidor
   - Ver la dirección IP para acceder al sistema
   - Monitorear logs en tiempo real

### Acceso al Sistema

Una vez iniciado, acceda al sistema desde cualquier navegador usando la URL proporcionada por la aplicación.

## Despliegue en macOS

Para usuarios de macOS, siga estos pasos para crear una aplicación nativa:

1. Asegúrese de tener `server_manager.py` y `create_macos_app.sh` en su directorio
2. Haga ejecutable el script:
   ```
   chmod +x create_macos_app.sh
   ```
3. Ejecute el script:
   ```
   ./create_macos_app.sh
   ```
4. Se creará una aplicación "Gestor Servidor Flask.app" que puede ejecutarse con doble clic

## Frontend

El frontend del sistema está desarrollado con:
- HTML5/CSS3 para la estructura y estilos
- JavaScript para la interactividad
- Diseño responsivo adaptable a diferentes dispositivos

## Base de Datos

La aplicación utiliza SQLite como motor de base de datos, facilitando la portabilidad y minimizando la configuración necesaria. La estructura de la base de datos incluye tablas para:
- Registro de personal
- Control de asistencia
- Información temporal y estadísticas

## Desarrollo

El desarrollo del sistema siguió estas etapas principales:
1. Creación de bases y estructura inicial
2. Desarrollo del frontend y componentes de interfaz
3. Implementación de la funcionalidad completa
4. Finalización y optimización del frontend
5. Implementación del sistema de despliegue en producción

## Contacto

Para cualquier consulta sobre la implementación o funcionamiento del sistema, contacte al desarrollador:

**Desarrollador:** Alvaro Encinas  
**Institución:** Escuela Militar de Ingeniería  
**Laboratorio:** Metal Mecánica (DNICYT) - Alto Irpavi