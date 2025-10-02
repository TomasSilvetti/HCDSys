# HU016: Filtros Avanzados

Como usuario del sistema
Quiero poder aplicar filtros adicionales a mi búsqueda
Para refinar los resultados con criterios más específicos

## Descripción
El sistema debe extender la búsqueda simple existente (HU006) con filtros adicionales que permitan refinar los resultados de búsqueda. Esta funcionalidad complementa la búsqueda por palabras clave y fechas ya implementada.

## Criterios de Aceptación

1. Dado que estoy en la interfaz de búsqueda
   Cuando selecciono "Más Filtros"
   Entonces además de la búsqueda simple veo:
   - Tipo de documento (desplegable)
   - Usuario que lo cargó (autocompletado)
   - Número de expediente (campo de texto)
   - Categoría (desplegable)

2. Dado que estoy en búsqueda avanzada
   Cuando aplico múltiples filtros
   Entonces:
   - Los filtros se combinan con operador AND
   - Se actualiza la lista de resultados
   - Se muestra claramente los filtros activos
   - Puedo eliminar filtros individualmente

3. Dado que hay filtros activos
   Cuando realizo una nueva búsqueda
   Entonces:
   - Se muestran los documentos que cumplen todos los criterios
   - Se indica el total de resultados encontrados
   - Se mantiene el orden por relevancia

4. Dado que estoy viendo resultados filtrados
   Cuando no hay coincidencias
   Entonces:
   - Se muestra un mensaje claro
   - Se sugiere reducir o modificar los filtros
   - Se mantienen visibles los filtros aplicados

5. Dado que uso la búsqueda avanzada
   Cuando limpio los filtros
   Entonces:
   - Se resetean todos los campos
   - Se vuelve a la vista de resultados sin filtros
   - Se mantiene la última búsqueda por palabras clave

## Implementación Técnica

### Filtros Disponibles
```typescript
interface AdvancedFilters {
  dateRange: {
    from: Date;
    to: Date;
  };
  documentType: string[];
  uploadedBy: number; // ID del usuario
  expedientNumber: string;
  category: number; // ID de categoría
}
```

### Validaciones
- Fechas: 'desde' debe ser anterior a 'hasta'
- Tipos de documento: solo tipos válidos del sistema
- Usuario: debe existir en la base de datos
- Categoría: debe existir en la base de datos

## Notas Técnicas
- Extender el endpoint de búsqueda existente (HU006)
- Reutilizar la lógica de búsqueda por fechas
- Implementar filtros adicionales como parámetros opcionales
- Mantener la eficiencia de las consultas al combinar filtros
- Usar componentes reutilizables para la UI de filtros

## Criterios de Calidad
- Los filtros adicionales no deben impactar el rendimiento de la búsqueda simple
- La interfaz debe mantener la simplicidad de uso
- Clara distinción entre búsqueda simple y filtros adicionales
- Transición suave entre modos de búsqueda
- Mantener la velocidad de respuesta del endpoint original