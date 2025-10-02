# HU008: Vista Detalle de Documento

## Historia de Usuario
Como usuario del sistema
Quiero poder ver el detalle completo de un documento
Para acceder a toda su información y contenido

## Criterios de Aceptación
1. Dado que seleccioné un documento de los resultados de búsqueda
   Cuando accedo a su vista detalle
   Entonces veo la siguiente información:
   - Título del documento
   - Número de expediente
   - Descripción completa
   - Fecha de creación
   - Fecha de última modificación
   - Categoría a la que pertenece
   - Usuario que lo creó
   - Tipo de documento
   - Botón de descarga del archivo

2. Dado que estoy en la vista detalle
   Cuando el documento pertenece a una categoría
   Entonces veo el nombre y descripción de la categoría

3. Dado que estoy en la vista detalle
   Cuando el documento tiene versiones anteriores
   Entonces veo un historial de versiones con:
   - Número de versión
   - Fecha del cambio
   - Comentarios de la versión
   - Link para descargar la versión específica

4. Dado que estoy en la vista detalle
   Cuando intento descargar el documento
   Entonces el sistema inicia la descarga ya que tengo los permisos necesarios

5. Dado que estoy en la vista detalle
   Cuando quiero volver a los resultados de búsqueda
   Entonces encuentro un botón para regresar fácilmente

## Detalles Técnicos

### Frontend
- Componentes:
  - `DocumentDetail`: Componente principal para mostrar el detalle
  - `DocumentHeader`: Muestra título y metadatos principales
  - `DocumentContent`: Muestra descripción y detalles
  - `VersionHistory`: Lista de versiones si existen
  - `DownloadButton`: Componente para descargar archivos
- Rutas:
  - `/documents/:id`: Ruta para ver el detalle de un documento
- Estado:
  - Datos del documento actual
  - Lista de versiones
  - Estado de carga
  - Estado de permisos
- Interfaces:
  ```typescript
  interface DocumentDetail {
    id: number;
    titulo: string;
    descripcion: string;
    numero_expediente: string;
    fecha_creacion: Date;
    fecha_modificacion: Date;
    tipo_documento: string;
    path_archivo: string;
    categoria: {
      id: number;
      nombre: string;
      descripcion: string;
    };
    usuario: {
      id: number;
      nombre: string;
      apellido: string;
    };
    versiones?: {
      numero_version: number;
      fecha_cambio: Date;
      comentarios: string;
      path_archivo: string;
    }[];
  }
  ```

### Backend
- Endpoints:
  - `GET /api/documents/:id`
    - Parámetros:
      - `id`: ID del documento
    - Respuestas:
      - 200: documento encontrado
      - 403: sin permisos
      - 404: no encontrado
  - `GET /api/documents/:id/download`
    - Parámetros:
      - `id`: ID del documento
    - Respuestas:
      - 200: archivo para descarga
      - 403: sin permisos
      - 404: no encontrado
    - Headers de respuesta:
      - `Content-Disposition`: para forzar descarga
      - `Content-Type`: tipo MIME del archivo
    - Incluye información relacionada de:
      - Categoría
      - Usuario creador
      - Versiones
- Funcionalidades:
  - Validación de permisos de acceso
  - Construcción de rutas de descarga seguras
  - Registro de acceso en HistorialAcceso

### Base de Datos
Utiliza las tablas:
- `Documento`: Información principal
- `Categoria`: Datos de la categoría
- `Usuario`: Datos del creador
- `Version`: Historial de versiones
- `HistorialAcceso`: Para registrar la visualización

## Explicación en Lenguaje Natural
Esta historia trata sobre mostrar toda la información de un documento cuando hacemos clic en él. Es como cuando abres un artículo completo después de ver su resumen en los resultados de búsqueda.

Lo que vamos a construir:
1. Una página que muestre todos los detalles del documento:
   - La información básica como título y descripción
   - Datos importantes como fechas y número de expediente
   - Información sobre quién lo creó y a qué categoría pertenece
   - Un botón para descargar el archivo

2. Si el documento tiene versiones anteriores:
   - Mostramos una lista de todas las versiones
   - Cada versión tiene su fecha y comentarios
   - Se puede descargar cualquier versión

3. Sistema de permisos:
   - Los documentos clasificados o restringidos son completamente invisibles para usuarios sin permisos
   - Solo podemos llegar a esta vista si tenemos los permisos necesarios
   - Registramos quién mira y descarga cada documento para auditoría
   - La seguridad se maneja desde la búsqueda, garantizando que solo vemos lo que podemos acceder

4. Navegación fácil:
   - Un botón para volver a los resultados de búsqueda
   - Todo organizado de forma clara y fácil de entender