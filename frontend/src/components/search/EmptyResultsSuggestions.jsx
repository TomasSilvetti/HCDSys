import { FiInfo, FiSearch } from 'react-icons/fi';
import PropTypes from 'prop-types';

/**
 * Componente para mostrar sugerencias cuando no hay resultados de búsqueda
 * 
 * @param {Object} props - Propiedades del componente
 * @param {string} props.query - Término de búsqueda
 * @param {Object} props.filters - Filtros aplicados
 * @param {Function} props.onClearFilters - Función para limpiar filtros
 * @returns {JSX.Element} Componente de sugerencias
 */
const EmptyResultsSuggestions = ({ query, filters, onClearFilters }) => {
  // Contar filtros activos
  const activeFiltersCount = Object.values(filters).filter(Boolean).length;
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 text-center">
      <div className="flex justify-center mb-4">
        <div className="bg-gray-100 rounded-full p-3">
          <FiSearch className="h-8 w-8 text-gray-400" />
        </div>
      </div>
      
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        No se encontraron resultados
      </h3>
      
      <p className="text-gray-500 mb-4">
        {query ? (
          <>No se encontraron documentos que coincidan con "<strong>{query}</strong>"</>
        ) : (
          <>No se encontraron documentos que coincidan con los filtros seleccionados</>
        )}
      </p>
      
      <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4 text-left">
        <div className="flex">
          <div className="flex-shrink-0">
            <FiInfo className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-700">
              {activeFiltersCount > 0 ? (
                <>
                  Tienes <strong>{activeFiltersCount} {activeFiltersCount === 1 ? 'filtro activo' : 'filtros activos'}</strong>. 
                  Intenta con términos más generales o elimina algunos filtros para ampliar tu búsqueda.
                </>
              ) : (
                <>
                  Intenta con términos más generales o verifica la ortografía de tu búsqueda.
                </>
              )}
            </p>
          </div>
        </div>
      </div>
      
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-700">Sugerencias:</h4>
        <ul className="text-sm text-gray-600 list-disc list-inside space-y-1 text-left">
          <li>Verifica la ortografía de los términos de búsqueda</li>
          <li>Utiliza palabras clave más generales</li>
          <li>Prueba con sinónimos</li>
          {activeFiltersCount > 0 && (
            <li>Reduce el número de filtros aplicados</li>
          )}
        </ul>
      </div>
      
      {activeFiltersCount > 0 && (
        <button
          onClick={onClearFilters}
          className="mt-4 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Limpiar todos los filtros
        </button>
      )}
    </div>
  );
};

EmptyResultsSuggestions.propTypes = {
  query: PropTypes.string,
  filters: PropTypes.object.isRequired,
  onClearFilters: PropTypes.func.isRequired
};

export default EmptyResultsSuggestions;
