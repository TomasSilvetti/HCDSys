# HCDSys - Sistema de Gestión Documental Municipal

## Descripción
Sistema de gestión documental para el honorable concejo deliberante (HCD) de Lules. Permite cargar, buscar y gestionar documentos municipales de manera eficiente.

## Importante 
- Diseño responsive de toda la pagina

## Roles
los roles van a tener diferentes permisos, estos son los diferentes roles:
- 

## Tecnologías
- Frontend: React + Vite
- Backend: FastAPI
- Base de datos: PostgreSQL
- Conexión DB: psycopg2

## Características Principales
- [ ] Carga de documentos
- [ ] Búsqueda por metadatos
- [ ] Visualización de documentos
- [ ] Control de acceso básico

## Configuración del Proyecto
### Requisitos Previos
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+

### Instalación
[Instrucciones de instalación pendientes]

## Estructura de la Base de Datos
[Esquema de base de datos pendiente]

## Estructura del Proyecto
```
/frontend
  /src
    /components     # Componentes reutilizables de React
    /pages         # Páginas principales
    /utils         # Funciones utilitarias
    /hooks         # Custom hooks de React
    /styles        # Estilos CSS/SCSS
/backend
  /app
    /routes        # Endpoints de la API
    /db           # Conexión y queries a PostgreSQL
    /utils        # Funciones utilitarias
/docs            # Documentación adicional
```