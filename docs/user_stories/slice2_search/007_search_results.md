# HU007: Visualización de Resultados de Búsqueda

## Historia de Usuario
Como usuario del sistema
Quiero ver los resultados de búsqueda de forma clara
Para poder identificar fácilmente los documentos que necesito

## Criterios de Aceptación
1. Dado que realicé una búsqueda exitosa
   Cuando el sistema encuentra documentos
   Entonces veo una lista con los siguientes datos por cada documento:
   - Título del documento
   - Número de expediente
   - Fecha de creación
   - Categoría

2. Dado que estoy viendo los resultados
   Cuando hay más de 10 documentos
   Entonces veo una paginación que me permite navegar entre páginas de resultados

3. Dado que estoy viendo la lista de resultados
   Cuando no hay documentos que coincidan con la búsqueda
   Entonces veo un mensaje amigable indicando que no se encontraron resultados

4. Dado que estoy viendo los resultados
   Cuando paso el mouse sobre un documento
   Entonces veo un resumen con su descripción

5. Dado que estoy viendo la lista de resultados
   Cuando hago clic en un documento
   Entonces soy redirigido a la vista detalle de ese documento

## Detalles Técnicos

### Frontend
- Componentes:
  - `SearchResults`: Componente principal para mostrar la lista de resultados
  - `DocumentCard`: Tarjeta individual para mostrar cada documento
  - `Pagination`: Componente de paginación
  - `NoResults`: Componente para mostrar mensaje cuando no hay resultados
- Estado:
  - Lista de documentos
  - Página actual
  - Total de resultados
  - Estado de carga
- Interfaces:
  ```typescript
  interface DocumentResult {
    id: number;
    titulo: string;
    numero_expediente: string;
    fecha_creacion: Date;
    categoria: {
      id: number;
      nombre: string;
    };
    descripcion: string;
  }
  ```

### Backend
Ya definido en la HU006 (Endpoint de Búsqueda)
- Agregar al response:
  - Total de documentos encontrados
  - Información de paginación

### Base de Datos
Utiliza las tablas existentes:
- `Documento`: Para la información principal
- `Categoria`: Para obtener el nombre de la categoría

## Explicación en Lenguaje Natural
Esta historia trata sobre cómo mostrar los documentos que encontramos al buscar. Es como cuando buscas en Google y te aparece una lista de resultados, pero en nuestro caso mostramos documentos con su información importante.

Lo que vamos a construir:
1. Una lista clara donde cada documento muestra:
   - Su título para saber de qué trata
   - Su número de expediente para identificarlo fácilmente
   - La fecha en que se creó
   - A qué categoría pertenece
   - En qué estado está

2. Si hay muchos resultados:
   - Los dividimos en páginas de 10 documentos
   - Agregamos botones para ir a la página siguiente/anterior

3. Detalles útiles:
   - Si pasas el mouse por un documento, ves más información
   - Puedes hacer clic para ver todos los detalles
   - Si no encontramos nada, te lo decimos claramente

La idea es que sea fácil y rápido encontrar el documento que necesitas entre todos los resultados.