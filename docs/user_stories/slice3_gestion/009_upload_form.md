# HU009: Formulario de Carga de Documentos

## Historia de Usuario
Como gestor de documentos
Quiero poder cargar nuevos documentos al sistema
Para mantener actualizada la base documental

## Criterios de Aceptación
1. Dado que soy un gestor de documentos
   Cuando accedo a la sección de carga de documentos
   Entonces veo un formulario con los siguientes campos:
   - Título del documento (obligatorio)
   - Número de expediente (obligatorio)
   - Descripción
   - Categoría (selector, Por el momento no obligatorio) 
   - Tipo de documento (selector, obligatorio)
   - Área de carga de archivo que permite:
     * Arrastrar y soltar archivos (drag & drop)
     * Botón para seleccionar archivo del dispositivo

2. Dado que estoy en el formulario de carga
   Cuando arrastro un archivo al área de carga o uso el botón de selección
   Entonces el área de carga muestra una vista previa del archivo seleccionado

3. Dado que estoy en el formulario de carga
   Cuando intento subir un archivo (por cualquiera de los dos métodos)
   Entonces solo puedo seleccionar archivos de tipo:
   - PDF (.pdf)
   - Word (.doc, .docx)
   - Excel (.xls, .xlsx)
   - Texto plano (.txt)

3. Dado que estoy completando el formulario
   Cuando algún campo obligatorio está vacío
   Entonces veo un mensaje de error indicando los campos requeridos

4. Dado que estoy subiendo un archivo
   Cuando el archivo excede el tamaño máximo permitido (10MB)
   Entonces veo un mensaje de error indicando el límite de tamaño

5. Dado que he completado el formulario correctamente
   Cuando presiono el botón "Cargar Documento"
   Entonces veo una barra de progreso de la carga

6. Dado que la carga fue exitosa
   Cuando el documento se guarda correctamente
   Entonces soy redirigido a la vista detalle del nuevo documento

7. Dado que ocurre un error durante la carga
   Cuando el sistema no puede procesar el documento
   Entonces veo un mensaje de error explicativo y puedo intentar nuevamente

## Detalles Técnicos

### Frontend
- Componentes:
  - `UploadForm`: Formulario principal de carga
  - `DragDropFileInput`: Área de drag & drop con botón de selección integrado
  - `FilePreview`: Vista previa del archivo seleccionado
  - `ProgressBar`: Barra de progreso de carga
  - `CategorySelect`: Selector de categorías
  - `DocumentTypeSelect`: Selector de tipos de documento
- Validaciones:
  - Campos requeridos
  - Tipos de archivo permitidos
  - Tamaño máximo de archivo
- Estado:
  - Datos del formulario
  - Estado de la carga
  - Errores de validación
- Interfaces:
  ```typescript
  interface UploadFormData {
    titulo: string;
    numero_expediente: string;
    descripcion?: string;
    categoria_id: number;
    tipo_documento: string;
    archivo: File;
  }
  ```

### Backend
- Endpoints:
  - `POST /api/documents`
    - Content-Type: multipart/form-data
    - Body:
      - Campos del formulario
      - Archivo adjunto
    - Respuestas:
      - 201: documento creado
      - 400: datos inválidos
      - 413: archivo muy grande
      - 415: tipo de archivo no soportado
- Validaciones:
  - Permisos del usuario
  - Formato de campos
  - Validación de archivo
  - Unicidad de número de expediente
- Procesamiento:
  - Sanitización de datos
  - Validación de archivo
  - Almacenamiento seguro
  - Generación de rutas

### Base de Datos
Utiliza las tablas:
- `Documento`: Para almacenar metadatos
- `Categoria`: Para validar categoría seleccionada
- `Usuario`: Para registrar creador
- `HistorialAcceso`: Para registrar la creación

## Explicación en Lenguaje Natural
Esta historia trata sobre crear un formulario amigable donde los gestores de documentos puedan subir nuevos archivos al sistema. Es como cuando subes un archivo a Google Drive, pero con campos adicionales para organizarlo mejor.

Lo que vamos a construir:
1. Un formulario claro y fácil de usar donde:
   - Ingresamos información básica como título y número de expediente
   - Seleccionamos una categoría para organizarlo
   - Elegimos el tipo de documento
   - Subimos el archivo arrastrándolo al área designada o usando el botón de selección
   - Vemos una vista previa del archivo seleccionado

2. Sistema de validación que:
   - Nos avisa si nos falta completar algo importante
   - Verifica que el archivo sea del tipo correcto
   - Controla que no sea muy grande

3. Proceso de carga que:
   - Muestra el progreso de la subida
   - Avisa si todo salió bien
   - Explica claramente si hubo algún error

4. Después de la carga:
   - Nos lleva a ver el documento que acabamos de subir
   - Podemos verificar que toda la información esté correcta