import { FiX } from 'react-icons/fi';
import PropTypes from 'prop-types';

/**
 * Componente para mostrar y gestionar los filtros activos
 * 
 * @param {Object} props - Propiedades del componente
 * @param {Array} props.filters - Array de filtros activos
 * @param {Function} props.onRemoveFilter - Función para eliminar un filtro
 * @param {Function} props.onClearAllFilters - Función para limpiar todos los filtros
 * @returns {JSX.Element} Componente de filtros activos
 */
const ActiveFilters = ({ filters, onRemoveFilter, onClearAllFilters }) => {
  // Si no hay filtros activos, no mostrar nada
  if (!filters || filters.length === 0) {
    return null;
  }

  return (
    <div className="bg-gray-50 p-3 rounded-md border border-gray-200 mb-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-700">Filtros activos</h3>
        <button 
          onClick={onClearAllFilters}
          className="text-xs text-primary-600 hover:text-primary-800 font-medium"
          aria-label="Limpiar todos los filtros"
        >
          Limpiar todos
        </button>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {filters.map((filter) => (
          <div 
            key={filter.id} 
            className="inline-flex items-center bg-white px-2 py-1 rounded-md border border-gray-200 text-sm"
          >
            <span className="mr-1 font-medium text-gray-600">{filter.label}:</span>
            <span className="text-gray-800">{filter.value}</span>
            <button 
              onClick={() => onRemoveFilter(filter.id)}
              className="ml-1 text-gray-400 hover:text-gray-600"
              aria-label={`Eliminar filtro ${filter.label}`}
            >
              <FiX size={14} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

ActiveFilters.propTypes = {
  filters: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired
    })
  ).isRequired,
  onRemoveFilter: PropTypes.func.isRequired,
  onClearAllFilters: PropTypes.func.isRequired
};

export default ActiveFilters;
