# HU006: Endpoint de Búsqueda Simple

## Historia de Usuario
Como usuario del sistema
Quiero poder buscar documentos por título o número de expediente, y filtrar por rango de fechas
Para encontrar la información que necesito

## Criterios de Aceptación
1. Dado que soy un usuario con una sesión activa
   Cuando realizo una búsqueda con un término válido
   Entonces recibo una lista solo de los documentos a los que tengo permiso de acceso y que coinciden con mi búsqueda

2. Dado que soy un usuario con una sesión activa
   Cuando existen documentos clasificados o restringidos
   Entonces estos documentos son completamente excluidos de mis resultados de búsqueda si no tengo los permisos necesarios

2. Dado que realizo una búsqueda
   Cuando el término de búsqueda está vacío
   Entonces el servidor responde con un error 400 indicando que el término es requerido

3. Dado que realizo una búsqueda con fechas
   Cuando especifico una fecha desde y/o hasta
   Entonces recibo documentos que fueron creados en ese rango de fechas

4. Dado que realizo una búsqueda
   Cuando no se encuentran documentos que coincidan
   Entonces recibo una lista vacía y un mensaje indicando que no hay resultados

5. Dado que realizo una búsqueda
   Cuando hay un error en el servidor
   Entonces recibo un mensaje de error apropiado y un código de estado HTTP 500

## Detalles Técnicos

### Frontend
- Servicios:
  - `searchService.ts`: Servicio para manejar las llamadas al API de búsqueda
- Interfaces:
  - `SearchResponse`: Interface para tipado de respuesta de búsqueda
  - `SearchParams`: Interface para parámetros de búsqueda

### Backend
- Endpoints:
  - `GET /api/search`
    - Query params:
      - `searchTerm`: término para buscar en título o número de expediente (string)
      - `searchField`: campo a buscar ('titulo' o 'numero_expediente', opcional)
      - `fromDate`: fecha desde (opcional, ISO string)
      - `toDate`: fecha hasta (opcional, ISO string)
- Seguridad:
  - La consulta SQL incluye filtros de permisos en la cláusula WHERE
  - Los documentos restringidos se excluyen a nivel de base de datos
  - La verificación de permisos se hace antes de ejecutar la búsqueda
  - No se utiliza filtrado posterior de resultados
    - Respuestas:
      - 200: búsqueda exitosa
      - 400: parámetros inválidos
      - 500: error del servidor
- Funcionalidades:
  - Validación de parámetros de búsqueda
  - Sanitización de términos de búsqueda
  - Construcción de consulta SQL con fechas opcionales
  - Paginación de resultados

### Base de Datos
- Tabla: `Documento`
  - Campos utilizados:
    - `id`: identificador único
    - `titulo`: título del documento
    - `numero_expediente`: número de expediente
    - `fecha_creacion`: fecha de creación
    - `fecha_modificacion`: fecha de modificación
- Índices necesarios:
  - Índice en `fecha_creacion` para optimizar búsqueda por fechas
  - Índices en `titulo` y `numero_expediente` para búsquedas

## Explicación en Lenguaje Natural
Esta historia se trata de crear el sistema de búsqueda básico que permite encontrar documentos por su título o número de expediente, y filtrarlos por fecha.

Lo que vamos a construir:
1. Un servicio que permite buscar documentos por:
   - Su título
   - Su número de expediente
   - Un rango de fechas
2. Un sistema que maneja errores de forma amigable

En términos técnicos simples:
- Cuando alguien busca algo, el sistema:
  1. Verifica que la búsqueda sea válida
  2. Busca en la base de datos documentos que coincidan
  3. Si encuentra algo, lo devuelve ordenadamente
  4. Si no encuentra nada, avisa al usuario
  5. Si algo sale mal, muestra un mensaje de error entendible

La base de datos necesitará algunos ajustes para hacer las búsquedas más rápidas (como poner índices), pero no necesitamos crear nuevas tablas ni campos.
