# Arquitectura del Sistema HCDSys

## Visión General

HCDSys es un sistema de gestión documental diseñado para facilitar el almacenamiento, búsqueda y gestión de documentos digitales. La arquitectura del sistema está basada en un enfoque de microservicios con una clara separación entre el frontend y el backend.

## Diagrama de Arquitectura

```
+----------------------------------+
|                                  |
|  Cliente (Navegador Web)         |
|                                  |
+----------------+----------------+
                 |
                 | HTTPS
                 |
+----------------v----------------+
|                                  |
|  Servidor Web (Nginx)            |
|  - Proxy inverso                 |
|  - Balanceo de carga             |
|  - SSL/TLS                       |
|                                  |
+----------------+----------------+
                 |
     +-----------+-----------+
     |                       |
+----v-----+           +----v-----+
|          |           |          |
| Frontend |           | Backend  |
| (React)  |           | (FastAPI)|
|          |           |          |
+----------+           +----+-----+
                            |
                            |
                       +----v-----+
                       |          |
                       | Base de  |
                       | Datos    |
                       | (Postgres)|
                       |          |
                       +----------+
                            |
                            |
                       +----v-----+
                       |          |
                       | Almacén  |
                       | Documentos|
                       |          |
                       +----------+
```

## Componentes Principales

### 1. Frontend

- **Tecnologías**: React, Vite, TailwindCSS
- **Responsabilidades**:
  - Interfaz de usuario
  - Gestión de estado de la aplicación
  - Comunicación con la API del backend
  - Validación de formularios
  - Renderizado de componentes
- **Estructura**:
  - `/src/components`: Componentes reutilizables
  - `/src/pages`: Páginas principales de la aplicación
  - `/src/utils`: Utilidades y funciones auxiliares
  - `/src/context`: Contextos de React para gestión de estado
  - `/src/hooks`: Hooks personalizados

### 2. Backend

- **Tecnologías**: Python, FastAPI, SQLAlchemy, Alembic
- **Responsabilidades**:
  - Autenticación y autorización
  - Gestión de documentos
  - Búsqueda y filtrado
  - Gestión de usuarios y roles
  - Almacenamiento de archivos
- **Estructura**:
  - `/app/routes`: Endpoints de la API
  - `/app/db`: Modelos de datos y configuración de base de datos
  - `/app/utils`: Utilidades y funciones auxiliares
  - `/app/services`: Lógica de negocio

### 3. Base de Datos

- **Tecnología**: PostgreSQL
- **Responsabilidades**:
  - Almacenamiento persistente de datos
  - Relaciones entre entidades
  - Indexación para búsquedas eficientes
- **Principales Tablas**:
  - `users`: Información de usuarios
  - `roles`: Roles del sistema
  - `permissions`: Permisos disponibles
  - `documents`: Metadatos de documentos
  - `document_versions`: Versiones de documentos
  - `document_history`: Historial de cambios

### 4. Almacenamiento de Documentos

- **Tecnología**: Sistema de archivos (producción: almacenamiento en nube)
- **Responsabilidades**:
  - Almacenamiento físico de archivos de documentos
  - Organización en directorios
  - Gestión de versiones

### 5. Servidor Web (Nginx)

- **Responsabilidades**:
  - Proxy inverso para backend y frontend
  - Servir archivos estáticos
  - Gestión de SSL/TLS
  - Balanceo de carga
  - Compresión de respuestas

## Flujos de Datos Principales

### 1. Autenticación de Usuario

1. El usuario ingresa credenciales en el frontend
2. El frontend envía las credenciales al backend (`/api/auth/login`)
3. El backend valida las credenciales contra la base de datos
4. Si son válidas, se genera un token JWT
5. El token se devuelve al frontend y se almacena en localStorage
6. Las solicitudes posteriores incluyen el token en el encabezado Authorization

### 2. Carga de Documentos

1. El usuario selecciona un archivo en el frontend
2. El frontend valida el tipo y tamaño del archivo
3. El archivo se envía al backend (`/api/documents`)
4. El backend:
   - Valida el archivo
   - Lo almacena en el sistema de archivos
   - Crea un registro en la base de datos
   - Indexa el contenido para búsquedas
5. Se devuelve la confirmación al frontend

### 3. Búsqueda de Documentos

1. El usuario ingresa términos de búsqueda en el frontend
2. El frontend envía la consulta al backend (`/api/documents?search=...`)
3. El backend:
   - Busca en la base de datos según los criterios
   - Aplica filtros de permisos
   - Devuelve los resultados paginados
4. El frontend muestra los resultados al usuario

## Consideraciones de Seguridad

- **Autenticación**: JWT con expiración corta
- **Autorización**: Basada en roles y permisos
- **Protección de Datos**: Validación de entrada, sanitización de salida
- **HTTPS**: Toda la comunicación cifrada
- **Rate Limiting**: Protección contra ataques de fuerza bruta
- **Validación de Archivos**: Verificación de tipos y tamaños
- **Registro de Actividad**: Auditoría de acciones críticas

## Escalabilidad

- **Horizontal**: Múltiples instancias de backend detrás de balanceador
- **Vertical**: Optimización de recursos en cada instancia
- **Caché**: Implementación de Redis para caché de consultas frecuentes
- **Base de Datos**: Índices optimizados para consultas frecuentes
- **Almacenamiento**: Posibilidad de migrar a soluciones cloud (S3, Azure Blob)

## Monitoreo y Observabilidad

- **Logs**: Centralización con formato JSON
- **Métricas**: Prometheus para recopilación
- **Dashboard**: Grafana para visualización
- **Alertas**: Configuración para eventos críticos
- **Trazabilidad**: Identificadores únicos para seguimiento de solicitudes

## Entornos

1. **Desarrollo**:
   - Configuración local para desarrolladores
   - Base de datos SQLite para simplicidad
   - Modo debug activado

2. **Pruebas**:
   - Entorno aislado para pruebas automatizadas
   - Base de datos en memoria o contenedor efímero
   - Configuración similar a producción

3. **Producción**:
   - Optimizado para rendimiento y seguridad
   - Base de datos PostgreSQL
   - Logs detallados pero sin información sensible
   - Monitoreo completo
