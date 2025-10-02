# HU010: Almacenamiento de Documentos

## Historia de Usuario
Como gestor de documentos
Quiero que los documentos se guarden de forma segura
Para mantener la integridad de la información

## Criterios de Aceptación
1. Dado que se ha subido un documento
   Cuando el sistema lo almacena
   Entonces:
   - Se verifica que no exista otro documento con el mismo título
   - Se guarda el registro en la base de datos para obtener el ID
   - Se guarda el archivo físico usando el ID como nombre (ej: "123.pdf")
   - Se actualiza el campo path_archivo con la ruta generada

2. Dado que se está guardando un documento
   Cuando ya existe un documento con el mismo título
   Entonces el sistema:
   - Muestra un mensaje de error al usuario
   - Solicita que modifique el título
   - No procede con el guardado hasta que el título sea único

3. Dado que se guarda un documento
   Cuando el proceso es exitoso
   Entonces:
   - Se registra la acción en el historial de acceso

4. Dado que ocurre un error durante el almacenamiento
   Cuando el sistema no puede guardar el archivo
   Entonces:
   - Se eliminan los archivos parcialmente guardados
   - Se revierten los cambios en la base de datos
   - Se notifica el error al usuario

5. Dado que se ha guardado un documento
   Cuando se necesita acceder a él posteriormente
   Entonces el sistema garantiza:
   - La integridad del archivo
   - Que el contenido no ha sido alterado
   - Que la ruta de acceso es válida

## Detalles Técnicos

### Backend
- Servicios:
  - `StorageService`: Manejo del almacenamiento de archivos
  - `FileValidationService`: Validación de archivos
- Funcionalidades:
  - Validación de tipos MIME y checksums
  - Gestión de rutas de almacenamiento
  - Organización por fechas
- Configuración:
  ```typescript
  interface StorageConfig {
    basePath: string;           // Ruta base de almacenamiento
    maxFileSize: number;        // Tamaño máximo permitido
    allowedExtensions: string[]; // Extensiones permitidas
    allowedMimeTypes: Record<string, string[]>; // Mapeo extensión -> tipos MIME permitidos
  }
  ```

### Sistema de Archivos
- Estructura de directorios:
  ```
  /storage
    /documents          # Documentos principales
      /YYYY            # Año
        /MM            # Mes
          /123.pdf     # ID_documento.extension
          /124.docx
  ```

### Base de Datos
- Actualizaciones en:
  - `Documento`: path_archivo actualizado
  - `Version`: registro de versión inicial
  - `HistorialAcceso`: registro de la creación

### Seguridad
- Validaciones:
  - Verificación de tipos MIME (asegurar que el archivo corresponde al tipo declarado)
  - Verificación de integridad básica (tamaño y formato correctos)
- Permisos:
  - Archivos no accesibles directamente vía web
  - Permisos restrictivos a nivel de sistema de archivos
  - Acceso solo través de endpoints autorizados



## Explicación en Lenguaje Natural
Esta historia trata sobre cómo guardamos los documentos de forma segura una vez que el usuario los sube. El sistema implementa:

1. Organización:
   - Guarda los archivos de manera ordenada por fecha
   - Usa títulos únicos para identificar documentos
   - Mantiene un registro de ubicación y metadatos

2. Seguridad:
   - Verifica que los archivos sean del tipo correcto (PDF es PDF, DOC es DOC, etc.)
   - Calcula checksums para verificar integridad
   - Los guarda en ubicaciones seguras del servidor

3. Protección contra errores:
   - Si algo sale mal, no deja archivos a medias
   - Revierte cambios en la base de datos si hay errores
   - Notifica al usuario sobre problemas

4. Mantenimiento del orden:
   - Organiza los archivos por fecha
   - Mantiene registro de accesos
   - Facilita encontrar documentos

El objetivo es asegurar que:
- Los documentos se almacenan de forma segura
- La integridad del archivo está garantizada
- No se puede acceder sin autorización
- Se mantiene un registro claro de todos los documentos