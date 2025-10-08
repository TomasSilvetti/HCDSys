# Modelo de Datos - HCDSys

## Visión General

El modelo de datos de HCDSys está diseñado para soportar un sistema de gestión documental con control de versiones, permisos basados en roles, y capacidades avanzadas de búsqueda. El esquema está implementado en PostgreSQL utilizando SQLAlchemy como ORM.

## Diagrama Entidad-Relación

```
+---------------+       +---------------+       +---------------+
| User          |       | Role          |       | Permission    |
+---------------+       +---------------+       +---------------+
| id            |<----->| id            |<----->| id            |
| email         |       | name          |       | name          |
| password_hash |       | description   |       | description   |
| first_name    |       | created_at    |       | created_at    |
| last_name     |       | updated_at    |       | updated_at    |
| is_active     |       +---------------+       +---------------+
| created_at    |
| updated_at    |
+------^--------+
       |
       |
+------v--------+       +---------------+       +---------------+
| Document      |<----->| DocVersion    |<----->| DocHistory    |
+---------------+       +---------------+       +---------------+
| id            |       | id            |       | id            |
| title         |       | document_id   |       | document_id   |
| description   |       | version_num   |       | user_id       |
| category      |       | file_path     |       | action        |
| tags          |       | file_hash     |       | details       |
| created_by    |       | file_size     |       | created_at    |
| updated_by    |       | mime_type     |       +---------------+
| created_at    |       | created_by    |
| updated_at    |       | created_at    |
+---------------+       +---------------+
```

## Entidades Principales

### 1. User (Usuario)

Representa a los usuarios del sistema.

| Campo         | Tipo      | Descripción                                   |
|---------------|-----------|-----------------------------------------------|
| id            | Integer   | Identificador único (clave primaria)          |
| email         | String    | Correo electrónico (único)                    |
| password_hash | String    | Hash de la contraseña                         |
| first_name    | String    | Nombre del usuario                            |
| last_name     | String    | Apellido del usuario                          |
| is_active     | Boolean   | Estado de activación de la cuenta             |
| role_id       | Integer   | Rol asignado al usuario (clave foránea)       |
| created_at    | DateTime  | Fecha y hora de creación                      |
| updated_at    | DateTime  | Fecha y hora de última actualización          |

### 2. Role (Rol)

Define los roles disponibles en el sistema.

| Campo         | Tipo      | Descripción                                   |
|---------------|-----------|-----------------------------------------------|
| id            | Integer   | Identificador único (clave primaria)          |
| name          | String    | Nombre del rol (único)                        |
| description   | String    | Descripción del rol                           |
| created_at    | DateTime  | Fecha y hora de creación                      |
| updated_at    | DateTime  | Fecha y hora de última actualización          |

### 3. Permission (Permiso)

Define los permisos individuales que pueden asignarse a roles.

| Campo         | Tipo      | Descripción                                   |
|---------------|-----------|-----------------------------------------------|
| id            | Integer   | Identificador único (clave primaria)          |
| name          | String    | Nombre del permiso (único)                    |
| description   | String    | Descripción del permiso                       |
| created_at    | DateTime  | Fecha y hora de creación                      |
| updated_at    | DateTime  | Fecha y hora de última actualización          |

### 4. RolePermission (Relación Rol-Permiso)

Tabla de relación muchos a muchos entre roles y permisos.

| Campo         | Tipo      | Descripción                                   |
|---------------|-----------|-----------------------------------------------|
| role_id       | Integer   | ID del rol (clave foránea)                    |
| permission_id | Integer   | ID del permiso (clave foránea)                |

### 5. Document (Documento)

Almacena los metadatos de los documentos.

| Campo         | Tipo      | Descripción                                   |
|---------------|-----------|-----------------------------------------------|
| id            | Integer   | Identificador único (clave primaria)          |
| title         | String    | Título del documento                          |
| description   | String    | Descripción del documento                     |
| category      | String    | Categoría del documento (ORDENANZA, DECRETO, etc.) |
| tags          | ARRAY     | Etiquetas asociadas al documento              |
| created_by    | Integer   | ID del usuario que creó el documento          |
| updated_by    | Integer   | ID del último usuario que modificó el documento |
| created_at    | DateTime  | Fecha y hora de creación                      |
| updated_at    | DateTime  | Fecha y hora de última actualización          |

### 6. DocumentVersion (Versión de Documento)

Almacena las diferentes versiones de cada documento.

| Campo         | Tipo      | Descripción                                   |
|---------------|-----------|-----------------------------------------------|
| id            | Integer   | Identificador único (clave primaria)          |
| document_id   | Integer   | ID del documento (clave foránea)              |
| version_num   | Integer   | Número de versión                             |
| file_path     | String    | Ruta al archivo físico                        |
| file_hash     | String    | Hash SHA-256 del contenido del archivo        |
| file_size     | Integer   | Tamaño del archivo en bytes                   |
| mime_type     | String    | Tipo MIME del archivo                         |
| created_by    | Integer   | ID del usuario que creó esta versión          |
| created_at    | DateTime  | Fecha y hora de creación                      |

### 7. DocumentHistory (Historial de Documento)

Registra todas las acciones realizadas sobre los documentos.

| Campo         | Tipo      | Descripción                                   |
|---------------|-----------|-----------------------------------------------|
| id            | Integer   | Identificador único (clave primaria)          |
| document_id   | Integer   | ID del documento (clave foránea)              |
| user_id       | Integer   | ID del usuario que realizó la acción          |
| action        | String    | Tipo de acción (CREATE, UPDATE, DELETE, VIEW) |
| details       | JSON      | Detalles adicionales de la acción             |
| created_at    | DateTime  | Fecha y hora de la acción                     |

## Índices

Para optimizar el rendimiento de las consultas, se han definido los siguientes índices:

1. **Índices de Clave Primaria**:
   - `users.id`
   - `roles.id`
   - `permissions.id`
   - `documents.id`
   - `document_versions.id`
   - `document_history.id`

2. **Índices Únicos**:
   - `users.email`
   - `roles.name`
   - `permissions.name`

3. **Índices de Búsqueda**:
   - `documents.title` (índice de texto)
   - `documents.description` (índice de texto)
   - `documents.tags` (índice GIN para arrays)
   - `documents.category`
   - `document_versions.document_id`
   - `document_history.document_id`
   - `document_history.user_id`

## Restricciones y Reglas de Integridad

1. **Claves Foráneas**:
   - `users.role_id` → `roles.id`
   - `role_permission.role_id` → `roles.id`
   - `role_permission.permission_id` → `permissions.id`
   - `documents.created_by` → `users.id`
   - `documents.updated_by` → `users.id`
   - `document_versions.document_id` → `documents.id`
   - `document_versions.created_by` → `users.id`
   - `document_history.document_id` → `documents.id`
   - `document_history.user_id` → `users.id`

2. **Restricciones de Eliminación**:
   - `CASCADE`: Al eliminar un documento, se eliminan todas sus versiones e historial
   - `RESTRICT`: No se puede eliminar un rol si hay usuarios asignados a él
   - `RESTRICT`: No se puede eliminar un permiso si está asignado a roles

3. **Valores por Defecto**:
   - `users.is_active` = `True`
   - `documents.created_at` = `CURRENT_TIMESTAMP`
   - `documents.updated_at` = `CURRENT_TIMESTAMP`

## Migraciones

El esquema de base de datos se gestiona mediante Alembic, lo que permite:

1. Crear y aplicar migraciones de forma controlada
2. Realizar rollback a versiones anteriores si es necesario
3. Mantener un historial de cambios en el esquema
4. Sincronizar el esquema entre diferentes entornos

Las migraciones se encuentran en el directorio `/backend/alembic/versions/`.

## Consideraciones de Rendimiento

1. **Particionamiento**: Para tablas que crecen significativamente (como `document_history`), se implementa particionamiento por rango de fechas.

2. **Índices Parciales**: Para consultas frecuentes sobre subconjuntos de datos (por ejemplo, documentos activos).

3. **Índices de Texto**: Para búsquedas eficientes en campos de texto como título y descripción.

4. **Caché**: Implementación de caché para consultas frecuentes y resultados de búsqueda.

## Escalabilidad

El modelo está diseñado para escalar horizontalmente:

1. **Sharding**: Posibilidad de distribuir datos por categoría o fecha.
2. **Réplicas de Lectura**: Para distribuir la carga de consultas.
3. **Particionamiento**: Para tablas de gran volumen.

## Seguridad de Datos

1. **Cifrado**: Campos sensibles almacenados con cifrado.
2. **Auditoría**: Registro completo de cambios en `document_history`.
3. **Control de Acceso**: Basado en el modelo de roles y permisos.
4. **Integridad**: Verificación de hash para detectar modificaciones no autorizadas en archivos.
