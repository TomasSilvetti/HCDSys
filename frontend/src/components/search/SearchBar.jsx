import { useState } from 'react';
import { FiSearch, FiX, FiAlertCircle } from 'react-icons/fi';
import PropTypes from 'prop-types';

/**
 * Componente de barra de búsqueda con validación y estado de carga
 */
const SearchBar = ({ onSearch, isLoading = false, initialQuery = '' }) => {
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [error, setError] = useState('');

  /**
   * Maneja el envío del formulario de búsqueda
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validar que el campo no esté vacío
    if (!searchQuery.trim()) {
      setError('Por favor, ingrese un término de búsqueda');
      return;
    }
    
    // Limpiar error y ejecutar búsqueda
    setError('');
    onSearch(searchQuery.trim());
  };

  /**
   * Limpia el campo de búsqueda
   */
  const handleClear = () => {
    setSearchQuery('');
    setError('');
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          {/* Icono de búsqueda */}
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <FiSearch className="h-5 w-5 text-gray-400" />
          </div>
          
          {/* Campo de búsqueda */}
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={`block w-full pl-10 pr-10 py-3 border ${
              error ? 'border-red-500' : 'border-gray-300'
            } rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent`}
            placeholder="Buscar documentos por título, número de expediente..."
            disabled={isLoading}
            aria-label="Campo de búsqueda"
          />
          
          {/* Botón para limpiar el campo */}
          {searchQuery && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute inset-y-0 right-12 flex items-center pr-3"
              aria-label="Limpiar búsqueda"
            >
              <FiX className="h-5 w-5 text-gray-400 hover:text-gray-600" />
            </button>
          )}
        </div>
        
        {/* Botón de búsqueda */}
        <button
          type="submit"
          className={`absolute right-0 inset-y-0 px-4 py-2 bg-primary-600 text-white rounded-r-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
            isLoading ? 'opacity-75 cursor-not-allowed' : ''
          }`}
          disabled={isLoading}
          aria-label="Buscar"
        >
          {isLoading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
          ) : (
            'Buscar'
          )}
        </button>
      </form>
      
      {/* Mensaje de error */}
      {error && (
        <div className="mt-2 text-sm text-red-600 flex items-center">
          <FiAlertCircle className="mr-1" /> {error}
        </div>
      )}
      
      {/* Texto de ayuda */}
      <p className="mt-2 text-xs text-gray-500">
        Ingrese palabras clave para buscar documentos. Puede usar filtros adicionales para refinar su búsqueda.
      </p>
    </div>
  );
};

SearchBar.propTypes = {
  onSearch: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  initialQuery: PropTypes.string,
};

export default SearchBar;
