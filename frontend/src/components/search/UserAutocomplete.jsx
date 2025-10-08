import { useState, useEffect, useRef } from 'react';
import { FiUser, FiSearch, FiX } from 'react-icons/fi';
import PropTypes from 'prop-types';
import api from '../../utils/api';

/**
 * Componente de autocompletado para buscar usuarios
 * 
 * @param {Object} props - Propiedades del componente
 * @param {Function} props.onSelect - Función que se ejecuta al seleccionar un usuario
 * @param {string} props.initialValue - Valor inicial (ID de usuario)
 * @param {string} props.initialLabel - Etiqueta inicial (nombre de usuario)
 * @returns {JSX.Element} Componente de autocompletado de usuarios
 */
const UserAutocomplete = ({ onSelect, initialValue = '', initialLabel = '' }) => {
  const [query, setQuery] = useState('');
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(initialValue ? { id: initialValue, nombre_completo: initialLabel } : null);
  const [error, setError] = useState('');
  const dropdownRef = useRef(null);
  const inputRef = useRef(null);
  
  // Cerrar el dropdown al hacer clic fuera del componente
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  // Buscar usuarios cuando cambia la consulta
  useEffect(() => {
    const searchUsers = async () => {
      if (!query.trim() || query.length < 2) {
        setUsers([]);
        return;
      }
      
      setIsLoading(true);
      setError('');
      
      try {
        // Llamada a la API para buscar usuarios
        const response = await api.get('/users/search', {
          params: { query: query.trim() }
        });
        
        setUsers(response.data || []);
      } catch (error) {
        console.error('Error al buscar usuarios:', error);
        setError('Error al buscar usuarios');
        setUsers([]);
      } finally {
        setIsLoading(false);
      }
    };
    
    // Debounce para evitar muchas llamadas a la API
    const timeoutId = setTimeout(() => {
      searchUsers();
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [query]);
  
  // Manejar selección de usuario
  const handleSelectUser = (user) => {
    setSelectedUser(user);
    setQuery('');
    setIsOpen(false);
    onSelect(user.id, user.nombre_completo);
    
    // Enfocar el input después de seleccionar
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };
  
  // Limpiar selección
  const handleClearSelection = () => {
    setSelectedUser(null);
    setQuery('');
    onSelect('', '');
    
    // Enfocar el input después de limpiar
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };
  
  return (
    <div className="relative" ref={dropdownRef}>
      <div className="relative">
        {/* Icono de usuario */}
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <FiUser className="h-5 w-5 text-gray-400" />
        </div>
        
        {/* Campo de búsqueda o usuario seleccionado */}
        {selectedUser ? (
          <div className="flex items-center w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md bg-gray-50">
            <span className="flex-grow truncate">{selectedUser.nombre_completo}</span>
            <button
              type="button"
              onClick={handleClearSelection}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              aria-label="Limpiar selección"
            >
              <FiX className="h-5 w-5 text-gray-400 hover:text-gray-600" />
            </button>
          </div>
        ) : (
          <div className="relative">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setIsOpen(true);
              }}
              onClick={() => setIsOpen(true)}
              placeholder="Buscar usuario..."
              className="block w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              aria-label="Buscar usuario"
            />
            {query && (
              <button
                type="button"
                onClick={() => setQuery('')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                aria-label="Limpiar búsqueda"
              >
                <FiX className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              </button>
            )}
          </div>
        )}
      </div>
      
      {/* Dropdown de resultados */}
      {isOpen && !selectedUser && (
        <div className="absolute z-10 mt-1 w-full bg-white rounded-md shadow-lg max-h-60 overflow-auto border border-gray-200">
          {isLoading ? (
            <div className="flex justify-center items-center py-4">
              <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-primary-600"></div>
            </div>
          ) : error ? (
            <div className="p-4 text-sm text-red-600">{error}</div>
          ) : users.length > 0 ? (
            <ul className="py-1">
              {users.map((user) => (
                <li key={user.id}>
                  <button
                    type="button"
                    onClick={() => handleSelectUser(user)}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    <div className="font-medium">{user.nombre_completo}</div>
                    <div className="text-xs text-gray-500">{user.email}</div>
                  </button>
                </li>
              ))}
            </ul>
          ) : query.length >= 2 ? (
            <div className="p-4 text-sm text-gray-500">No se encontraron usuarios</div>
          ) : (
            <div className="p-4 text-sm text-gray-500">
              <div className="flex items-center">
                <FiSearch className="mr-2 text-gray-400" />
                Ingrese al menos 2 caracteres para buscar
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

UserAutocomplete.propTypes = {
  onSelect: PropTypes.func.isRequired,
  initialValue: PropTypes.string,
  initialLabel: PropTypes.string
};

export default UserAutocomplete;
