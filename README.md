# HCDSys - Sistema de Gestión Documental Municipal

## Descripción
Sistema de gestión documental para el honorable concejo deliberante (HCD) de Lules. Permite cargar, buscar y gestionar documentos municipales de manera eficiente.

## Importante 
- Diseño responsive de toda la pagina

## Roles
Los roles tendrán diferentes permisos en el sistema:
- Administrador: Acceso completo al sistema, gestión de usuarios y roles
- Gestor de Documentos: Carga, edición y gestión de documentos
- Usuario de Consulta: Solo búsqueda y visualización de documentos

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

#### Backend (FastAPI)
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/HCDSys.git
   cd HCDSys
   ```

2. Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En macOS/Linux
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   - Crear archivo `.env` en la carpeta `backend` basado en `.env.example`

5. Iniciar servidor de desarrollo:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend (React + Vite)
1. Instalar dependencias:
   ```bash
   cd frontend
   npm install
   ```

2. Configurar variables de entorno:
   - Crear archivo `.env.local` en la carpeta `frontend` basado en `.env.example`

3. Iniciar servidor de desarrollo:
   ```bash
   npm run dev
   ```

#### Base de datos (PostgreSQL)
1. Crear base de datos:
   ```sql
   CREATE DATABASE hcdsys;
   ```

2. Ejecutar migraciones:
   ```bash
   cd backend
   alembic upgrade head
   ```

## Estructura de la Base de Datos

### Entidades Principales

#### Usuario
- id: Integer (PK)
- nombre: String
- apellido: String
- email: String (único)
- password_hash: String
- dni: String (único)
- role_id: Integer (FK)
- activo: Boolean
- fecha_registro: DateTime
- ultimo_acceso: DateTime

#### Documento
- id: Integer (PK)
- titulo: String
- numero_expediente: String
- descripcion: Text
- fecha_creacion: DateTime
- fecha_modificacion: DateTime
- categoria_id: Integer (FK)
- tipo_documento_id: Integer (FK)
- usuario_id: Integer (FK)
- path_archivo: String
- activo: Boolean

#### Rol
- id: Integer (PK)
- nombre: String
- descripcion: Text

#### Permiso
- id: Integer (PK)
- nombre: String
- descripcion: Text
- codigo: String (único)

#### RolPermiso
- rol_id: Integer (PK, FK)
- permiso_id: Integer (PK, FK)

#### Categoria
- id: Integer (PK)
- nombre: String
- descripcion: Text

#### TipoDocumento
- id: Integer (PK)
- nombre: String
- descripcion: Text
- extensiones_permitidas: String

#### VersionDocumento
- id: Integer (PK)
- documento_id: Integer (FK)
- numero_version: Integer
- fecha_version: DateTime
- comentario: Text
- path_archivo: String
- usuario_id: Integer (FK)

#### HistorialAcceso
- id: Integer (PK)
- usuario_id: Integer (FK)
- documento_id: Integer (FK)
- accion: String
- fecha: DateTime
- detalles: Text

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