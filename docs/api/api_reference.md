# Referencia de la API - HCDSys

## Visión General

La API de HCDSys está construida con FastAPI y sigue los principios RESTful. Todas las respuestas están en formato JSON y los códigos de estado HTTP se utilizan para indicar el resultado de las operaciones.

## Base URL

```
https://[dominio]/api
```

## Autenticación

La API utiliza autenticación basada en tokens JWT.

### Obtener Token

```
POST /auth/login
```

**Cuerpo de la Solicitud:**

```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña"
}
```

**Respuesta Exitosa:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "role": "admin"
  }
}
```

### Uso del Token

Incluir el token en el encabezado `Authorization` de todas las solicitudes autenticadas:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Endpoints

### Autenticación y Usuarios

#### Iniciar Sesión

```
POST /auth/login
```

**Cuerpo de la Solicitud:**

```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña"
}
```

**Respuesta Exitosa (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "role": "admin"
  }
}
```

#### Registrar Usuario

```
POST /auth/register
```

**Cuerpo de la Solicitud:**

```json
{
  "email": "nuevo@ejemplo.com",
  "password": "contraseña",
  "first_name": "Nombre",
  "last_name": "Apellido"
}
```

**Respuesta Exitosa (201 Created):**

```json
{
  "id": 2,
  "email": "nuevo@ejemplo.com",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "is_active": true,
  "role": "user",
  "created_at": "2025-10-08T12:00:00"
}
```

#### Obtener Perfil de Usuario

```
GET /users/me
```

**Respuesta Exitosa (200 OK):**

```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "is_active": true,
  "role": "admin",
  "created_at": "2025-10-01T10:00:00",
  "permissions": ["create_document", "delete_document", "manage_users"]
}
```

#### Listar Usuarios

```
GET /users
```

**Parámetros de Consulta:**
- `page`: Número de página (por defecto: 1)
- `limit`: Elementos por página (por defecto: 10)
- `search`: Búsqueda por nombre o email

**Respuesta Exitosa (200 OK):**

```json
{
  "total": 25,
  "page": 1,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "email": "usuario@ejemplo.com",
      "first_name": "Nombre",
      "last_name": "Apellido",
      "is_active": true,
      "role": "admin",
      "created_at": "2025-10-01T10:00:00"
    },
    // ...más usuarios
  ]
}
```

### Documentos

#### Listar Documentos

```
GET /documents
```

**Parámetros de Consulta:**
- `page`: Número de página (por defecto: 1)
- `limit`: Elementos por página (por defecto: 10)
- `search`: Búsqueda por título o descripción
- `category`: Filtrar por categoría
- `tags`: Filtrar por etiquetas (separadas por comas)
- `from_date`: Filtrar desde fecha (formato: YYYY-MM-DD)
- `to_date`: Filtrar hasta fecha (formato: YYYY-MM-DD)

**Respuesta Exitosa (200 OK):**

```json
{
  "total": 150,
  "page": 1,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "title": "Ordenanza Municipal 123/2025",
      "description": "Regulación de espacios públicos",
      "category": "ORDENANZA",
      "tags": ["espacios", "regulación", "municipal"],
      "created_by": {
        "id": 1,
        "name": "Nombre Apellido"
      },
      "created_at": "2025-10-01T10:00:00",
      "updated_at": "2025-10-01T10:00:00",
      "current_version": 1
    },
    // ...más documentos
  ]
}
```

#### Obtener Documento

```
GET /documents/{document_id}
```

**Respuesta Exitosa (200 OK):**

```json
{
  "id": 1,
  "title": "Ordenanza Municipal 123/2025",
  "description": "Regulación de espacios públicos",
  "category": "ORDENANZA",
  "tags": ["espacios", "regulación", "municipal"],
  "created_by": {
    "id": 1,
    "name": "Nombre Apellido"
  },
  "updated_by": {
    "id": 1,
    "name": "Nombre Apellido"
  },
  "created_at": "2025-10-01T10:00:00",
  "updated_at": "2025-10-01T10:00:00",
  "current_version": 1,
  "versions": [
    {
      "version_num": 1,
      "created_by": {
        "id": 1,
        "name": "Nombre Apellido"
      },
      "created_at": "2025-10-01T10:00:00",
      "file_size": 1024000,
      "mime_type": "application/pdf"
    }
  ]
}
```

#### Crear Documento

```
POST /documents
```

**Cuerpo de la Solicitud (multipart/form-data):**

- `title`: Título del documento
- `description`: Descripción del documento
- `category`: Categoría del documento
- `tags`: Etiquetas (array o string separado por comas)
- `file`: Archivo del documento

**Respuesta Exitosa (201 Created):**

```json
{
  "id": 2,
  "title": "Nueva Ordenanza 124/2025",
  "description": "Descripción de la nueva ordenanza",
  "category": "ORDENANZA",
  "tags": ["nueva", "ordenanza"],
  "created_by": {
    "id": 1,
    "name": "Nombre Apellido"
  },
  "created_at": "2025-10-08T12:30:00",
  "updated_at": "2025-10-08T12:30:00",
  "current_version": 1
}
```

#### Actualizar Documento

```
PUT /documents/{document_id}
```

**Cuerpo de la Solicitud:**

```json
{
  "title": "Título Actualizado",
  "description": "Descripción actualizada",
  "category": "DECRETO",
  "tags": ["actualizado", "decreto"]
}
```

**Respuesta Exitosa (200 OK):**

```json
{
  "id": 1,
  "title": "Título Actualizado",
  "description": "Descripción actualizada",
  "category": "DECRETO",
  "tags": ["actualizado", "decreto"],
  "created_by": {
    "id": 1,
    "name": "Nombre Apellido"
  },
  "updated_by": {
    "id": 1,
    "name": "Nombre Apellido"
  },
  "created_at": "2025-10-01T10:00:00",
  "updated_at": "2025-10-08T12:45:00",
  "current_version": 1
}
```

#### Subir Nueva Versión

```
POST /documents/{document_id}/versions
```

**Cuerpo de la Solicitud (multipart/form-data):**

- `file`: Archivo del documento

**Respuesta Exitosa (201 Created):**

```json
{
  "document_id": 1,
  "version_num": 2,
  "created_by": {
    "id": 1,
    "name": "Nombre Apellido"
  },
  "created_at": "2025-10-08T13:00:00",
  "file_size": 1048576,
  "mime_type": "application/pdf"
}
```

#### Descargar Versión de Documento

```
GET /documents/{document_id}/versions/{version_num}/download
```

**Respuesta:**
El archivo del documento como una descarga.

#### Eliminar Documento

```
DELETE /documents/{document_id}
```

**Respuesta Exitosa (204 No Content)**

### Roles y Permisos

#### Listar Roles

```
GET /roles
```

**Respuesta Exitosa (200 OK):**

```json
[
  {
    "id": 1,
    "name": "admin",
    "description": "Administrador del sistema",
    "permissions": [
      {
        "id": 1,
        "name": "create_document",
        "description": "Crear documentos"
      },
      // ...más permisos
    ]
  },
  // ...más roles
]
```

#### Crear Rol

```
POST /roles
```

**Cuerpo de la Solicitud:**

```json
{
  "name": "editor",
  "description": "Editor de documentos",
  "permissions": [1, 2, 3]  // IDs de permisos
}
```

**Respuesta Exitosa (201 Created):**

```json
{
  "id": 3,
  "name": "editor",
  "description": "Editor de documentos",
  "permissions": [
    {
      "id": 1,
      "name": "create_document",
      "description": "Crear documentos"
    },
    // ...más permisos
  ],
  "created_at": "2025-10-08T13:15:00"
}
```

#### Asignar Rol a Usuario

```
PUT /users/{user_id}/role
```

**Cuerpo de la Solicitud:**

```json
{
  "role_id": 3
}
```

**Respuesta Exitosa (200 OK):**

```json
{
  "id": 2,
  "email": "usuario@ejemplo.com",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "role": {
    "id": 3,
    "name": "editor",
    "description": "Editor de documentos"
  },
  "updated_at": "2025-10-08T13:20:00"
}
```

### Historial de Documentos

#### Obtener Historial de un Documento

```
GET /documents/{document_id}/history
```

**Parámetros de Consulta:**
- `page`: Número de página (por defecto: 1)
- `limit`: Elementos por página (por defecto: 10)

**Respuesta Exitosa (200 OK):**

```json
{
  "total": 5,
  "page": 1,
  "limit": 10,
  "items": [
    {
      "id": 5,
      "document_id": 1,
      "user": {
        "id": 1,
        "name": "Nombre Apellido"
      },
      "action": "UPDATE",
      "details": {
        "fields_changed": ["title", "description"]
      },
      "created_at": "2025-10-08T12:45:00"
    },
    // ...más entradas de historial
  ]
}
```

## Códigos de Estado

- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `204 No Content`: Solicitud exitosa, sin contenido para devolver
- `400 Bad Request`: Error en la solicitud del cliente
- `401 Unauthorized`: Autenticación requerida o inválida
- `403 Forbidden`: El cliente no tiene permisos para acceder al recurso
- `404 Not Found`: Recurso no encontrado
- `422 Unprocessable Entity`: Error de validación
- `500 Internal Server Error`: Error del servidor

## Manejo de Errores

Las respuestas de error siguen un formato consistente:

```json
{
  "detail": "Descripción del error"
}
```

Para errores de validación:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Paginación

Las respuestas paginadas incluyen metadatos:

```json
{
  "total": 150,     // Total de elementos
  "page": 2,        // Página actual
  "limit": 10,      // Elementos por página
  "items": [...]    // Elementos de la página actual
}
```

## Rate Limiting

La API implementa límites de tasa para proteger contra abusos:

- 60 solicitudes por minuto para endpoints públicos
- 300 solicitudes por minuto para usuarios autenticados

Las respuestas incluyen encabezados de límite de tasa:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1633694700
```

## Versiones de la API

La versión actual de la API es v1. La versión se especifica en la URL:

```
https://[dominio]/api/v1/...
```

Para garantizar la compatibilidad, las versiones anteriores se mantienen durante un período de tiempo después de la introducción de una nueva versión.
