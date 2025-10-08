import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { FiChevronDown, FiChevronUp } from 'react-icons/fi';
import DateRangePicker from './DateRangePicker';
import UserAutocomplete from './UserAutocomplete';

/**
 * Componente para filtros avanzados de búsqueda
 * 
 * @param {Object} props - Propiedades del componente
 * @param {Array} props.categories - Lista de categorías disponibles
 * @param {Array} props.documentTypes - Lista de tipos de documentos disponibles
 * @param {Object} props.initialFilters - Filtros iniciales
 * @param {Function} props.onApplyFilters - Función que se ejecuta al aplicar filtros
 * @param {Function} props.onClearFilters - Función que se ejecuta al limpiar filtros
 * @returns {JSX.Element} Componente de filtros avanzados
 */
const AdvancedFilters = ({ 
  categories = [], 
  documentTypes = [], 
  initialFilters = {}, 
  onApplyFilters,
  onClearFilters
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [dateRange, setDateRange] = useState({ 
    startDate: initialFilters.startDate || '', 
    endDate: initialFilters.endDate || '' 
  });
  const [selectedCategory, setSelectedCategory] = useState(initialFilters.categoryId || '');
  const [selectedType, setSelectedType] = useState(initialFilters.typeId || '');
  const [expedienteNumber, setExpedienteNumber] = useState(initialFilters.expedienteNumber || '');
  const [selectedUserId, setSelectedUserId] = useState(initialFilters.userId || '');
  const [selectedUserName, setSelectedUserName] = useState(initialFilters.userName || '');
  
  // Actualizar estado cuando cambian los filtros iniciales
  useEffect(() => {
    setDateRange({ 
      startDate: initialFilters.startDate || '', 
      endDate: initialFilters.endDate || '' 
    });
    setSelectedCategory(initialFilters.categoryId || '');
    setSelectedType(initialFilters.typeId || '');
    setExpedienteNumber(initialFilters.expedienteNumber || '');
    setSelectedUserId(initialFilters.userId || '');
    setSelectedUserName(initialFilters.userName || '');
  }, [initialFilters]);
  
  // Manejar cambio en el rango de fechas
  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };
  
  // Manejar cambio en la categoría
  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
  };
  
  // Manejar cambio en el tipo de documento
  const handleTypeChange = (e) => {
    setSelectedType(e.target.value);
  };
  
  // Manejar cambio en el número de expediente
  const handleExpedienteChange = (e) => {
    setExpedienteNumber(e.target.value);
  };
  
  // Manejar selección de usuario
  const handleUserSelect = (userId, userName) => {
    setSelectedUserId(userId);
    setSelectedUserName(userName);
  };
  
  // Manejar aplicación de filtros
  const handleApplyFilters = () => {
    onApplyFilters({
      startDate: dateRange.startDate,
      endDate: dateRange.endDate,
      categoryId: selectedCategory,
      typeId: selectedType,
      expedienteNumber: expedienteNumber,
      userId: selectedUserId,
      userName: selectedUserName
    });
  };
  
  // Manejar limpieza de filtros
  const handleClearFilters = () => {
    setDateRange({ startDate: '', endDate: '' });
    setSelectedCategory('');
    setSelectedType('');
    setExpedienteNumber('');
    setSelectedUserId('');
    setSelectedUserName('');
    
    onClearFilters();
  };
  
  // Determinar si hay filtros activos
  const hasActiveFilters = () => {
    return dateRange.startDate || 
           dateRange.endDate || 
           selectedCategory || 
           selectedType || 
           expedienteNumber || 
           selectedUserId;
  };
  
  return (
    <div className="bg-white border border-gray-200 rounded-md shadow-sm mb-6">
      {/* Encabezado del panel de filtros */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex justify-between items-center px-4 py-3 focus:outline-none"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center">
          <span className="text-lg font-medium text-gray-700">Filtros avanzados</span>
          {hasActiveFilters() && (
            <span className="ml-2 bg-primary-100 text-primary-800 text-xs font-medium px-2 py-0.5 rounded-full">
              Activos
            </span>
          )}
        </div>
        {isExpanded ? (
          <FiChevronUp className="h-5 w-5 text-gray-500" />
        ) : (
          <FiChevronDown className="h-5 w-5 text-gray-500" />
        )}
      </button>
      
      {/* Contenido del panel de filtros */}
      {isExpanded && (
        <div className="p-4 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Rango de fechas */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Rango de fechas</label>
              <DateRangePicker
                onRangeChange={handleDateRangeChange}
                initialStartDate={dateRange.startDate}
                initialEndDate={dateRange.endDate}
              />
            </div>
            
            {/* Tipo de documento */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Tipo de documento</label>
              <select 
                className="block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={selectedType}
                onChange={handleTypeChange}
              >
                <option value="">Todos los tipos</option>
                {documentTypes.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.nombre}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Categoría */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Categoría</label>
              <select 
                className="block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={selectedCategory}
                onChange={handleCategoryChange}
              >
                <option value="">Todas las categorías</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.nombre}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Número de expediente */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Número de expediente</label>
              <input
                type="text"
                value={expedienteNumber}
                onChange={handleExpedienteChange}
                placeholder="Ej: EXP-2023-00123"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            
            {/* Usuario que lo cargó */}
            <div className="space-y-2 md:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Usuario que lo cargó</label>
              <UserAutocomplete 
                onSelect={handleUserSelect} 
                initialValue={selectedUserId}
                initialLabel={selectedUserName}
              />
            </div>
          </div>
          
          {/* Botones de acción */}
          <div className="mt-4 flex justify-end space-x-2">
            <button 
              type="button"
              onClick={handleClearFilters}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Limpiar filtros
            </button>
            <button 
              type="button"
              onClick={handleApplyFilters}
              className="px-4 py-2 bg-primary-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary-700"
            >
              Aplicar filtros
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

AdvancedFilters.propTypes = {
  categories: PropTypes.array,
  documentTypes: PropTypes.array,
  initialFilters: PropTypes.object,
  onApplyFilters: PropTypes.func.isRequired,
  onClearFilters: PropTypes.func.isRequired
};

export default AdvancedFilters;
