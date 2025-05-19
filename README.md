# Sistema de Gestión Integral

Este sistema de asistencia está destinado para el laboratorio de Metal Mecánica (DNICYT) situado en Alto Irpavi de la Escuela Militar de Ingeniería, desarrollado por Alvaro S. Encinas Flores.

## Descripción

Sistema integral de registro y control de asistencia con interfaz web moderna que permite gestionar la entrada y salida de personal, así como el registro de trabajos realizados en el laboratorio de Metal Mecánica. Esta aplicación está desarrollada con Flask y proporciona una solución completa y fácil de usar para la administración de asistencia y gestión de trabajos del personal.

## 🆕 Nuevas Funcionalidades

- **Módulo de Trabajo**: Sistema completo para registrar, gestionar y hacer seguimiento de trabajos realizados en el laboratorio
- **Frontend Mejorado**: Interfaz completamente rediseñada con mejor experiencia de usuario
- **Base de Datos Actualizada**: Nuevas tablas y consultas optimizadas para soportar el módulo de trabajo
- **Gestión Avanzada**: Funcionalidades expandidas para control integral del laboratorio

## Estructura del Proyecto

```
sistema_de_registro_de_asistencia/
│
├── static/images/                    # Imágenes y recursos estáticos 
├── templates/                        # Plantillas HTML para la interfaz web
├── .gitignore                       # Archivos y directorios ignorados por Git
├── README.md                        # Este archivo de documentación
├── app.py                           # Aplicación principal Flask con nuevas rutas
├── attendance.db                    # Base de datos SQLite actualizada
├── database.py                      # Módulo para interactuar con la base de datos
├── requirements.txt                 # Dependencias del proyecto
├── server_manager.py                # Gestor para iniciar/detener el servidor
└── QUERYS PARA ACTUALIZAR EL SISTEMA.sql  # Scripts SQL para actualización
```

## Características

### Módulo de Asistencia
- **Registro de entrada y salida**: Control de asistencia con registro de fechas y horas exactas
- **Gestión de personal**: Administración completa de usuarios y perfiles

### 🆕 Módulo de Trabajo
- **Registro de trabajos**: Creación y seguimiento de trabajos realizados en el laboratorio
- **Gestión de estados**: Control de progreso y estados de cada trabajo
- **Asignación de personal**: Vinculación de trabajos con el personal responsable
- **Reportes y seguimiento**: Visualización detallada del progreso de trabajos

### Interfaz y Experiencia
- **Interfaz web moderna**: Frontend completamente rediseñado con mejor UX/UI
- **Diseño responsivo**: Adaptable a diferentes dispositivos y pantallas
- **Navegación intuitiva**: Estructura mejorada para facilitar el uso

### Sistema
- **Base de datos SQLite**: Almacenamiento eficiente y portable con nuevas tablas
- **Modo de producción**: Sistema de despliegue optimizado
- **Actualización automática**: Scripts SQL incluidos para migración de base de datos

## Requisitos

- Python 3.6 o superior
- Git (para gestión de versiones)
- Bash y WSL (para algunas funcionalidades en entorno Windows)
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clone el repositorio:
   ```bash
   git clone [url-del-repositorio]
   ```

2. Instale las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. **🆕 Actualice la base de datos** (para instalaciones existentes):
   ```bash
   # Ejecute las consultas SQL del archivo de actualización
   # O inicialice una nueva base de datos
   python database.py
   ```

## Uso

### Modo Desarrollo

Para ejecutar el sistema en modo desarrollo:

```bash
python app.py
```

### Modo Producción

El sistema incluye un gestor de servidor mejorado para facilitar el despliegue:

1. Ejecute el gestor de servidor:
   ```bash
   python server_manager.py
   ```

2. Utilice la interfaz del gestor para:
   - Iniciar/detener el servidor
   - Ver la dirección IP para acceder al sistema
   - Monitorear logs en tiempo real
   - Gestionar la aplicación de forma centralizada

### Acceso al Sistema

Una vez iniciado, acceda al sistema desde cualquier navegador usando la URL proporcionada. El sistema ahora incluye:

- **Panel de Control**: Vista principal con estadísticas y acceso rápido
- **Módulo de Asistencia**: Registro y gestión de asistencia del personal
- **🆕 Módulo de Trabajo**: Gestión completa de trabajos del laboratorio
- **Reportes**: Visualización de datos y estadísticas

## Despliegue en macOS

Para usuarios de macOS, siga estos pasos para crear una aplicación nativa:

1. Asegúrese de tener `server_manager.py` en su directorio
2. Haga ejecutable el script de creación:
   ```bash
   chmod +x create_macos_app.sh
   ```
3. Ejecute el script:
   ```bash
   ./create_macos_app.sh
   ```
4. Se creará una aplicación "Gestor Servidor Flask.app" ejecutable

## Frontend

El frontend ha sido completamente renovado e incluye:

- **HTML5/CSS3**: Estructura moderna y estilos actualizados
- **JavaScript**: Interactividad mejorada y funcionalidades avanzadas
- **Diseño responsivo**: Optimizado para todos los dispositivos
- **UX/UI moderna**: Interfaz intuitiva y atractiva
- **Componentes modulares**: Arquitectura escalable y mantenible

## Base de Datos

La aplicación utiliza SQLite con estructura expandida que incluye:

### Tablas Existentes
- Registro de personal
- Control de asistencia
- Información temporal y estadísticas

### 🆕 Nuevas Tablas
- Gestión de trabajos y proyectos
- Estados y seguimiento de tareas
- Relaciones trabajo-personal
- Metadatos y configuraciones

### Actualización
- Incluye archivo `QUERYS PARA ACTUALIZAR EL SISTEMA.sql` para migración
- Compatibilidad con versiones anteriores
- Optimizaciones de rendimiento

## Desarrollo y Actualizaciones

### Historial de Desarrollo
1. ✅ Creación de bases y estructura inicial
2. ✅ Desarrollo del frontend y componentes de interfaz
3. ✅ Implementación de la funcionalidad de asistencia
4. ✅ **🆕 Implementación del módulo de trabajo**
5. ✅ **🆕 Renovación completa del frontend**
6. ✅ **🆕 Optimización de base de datos y consultas**
7. ✅ Finalización y optimización del sistema completo

### Versiones Recientes
- **v2.0**: Implementación del módulo de trabajo
- **v2.1**: Renovación completa del frontend
- **v2.2**: Optimizaciones y mejoras en UX/UI

## Migración desde Versiones Anteriores

Si está actualizando desde una versión anterior:

1. Haga una copia de seguridad de su base de datos actual
2. Ejecute las consultas del archivo `QUERYS PARA ACTUALIZAR EL SISTEMA.sql`
3. Reinicie la aplicación
4. Verifique que todas las funcionalidades trabajen correctamente

## Contacto y Soporte

Para consultas sobre implementación, funcionamiento o actualizaciones del sistema:

**Desarrollador:** Alvaro Encinas  
**Institución:** Escuela Militar de Ingeniería  
**Laboratorio:** Metal Mecánica (DNICYT) - Alto Irpavi

---

*Última actualización: Mayo 2025 - Versión 2.2 con módulo de trabajo y frontend renovado*
