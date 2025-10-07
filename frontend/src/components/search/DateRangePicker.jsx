import { useState, useEffect, useRef } from 'react';
import { FiCalendar, FiX } from 'react-icons/fi';
import PropTypes from 'prop-types';

/**
 * Componente para seleccionar un rango de fechas
 */
const DateRangePicker = ({ 
  onRangeChange, 
  initialStartDate = '', 
  initialEndDate = '' 
}) => {
  const [startDate, setStartDate] = useState(initialStartDate);
  const [endDate, setEndDate] = useState(initialEndDate);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState('');
  const dropdownRef = useRef(null);
  
  // Formatear fecha para mostrar
  const formatDisplayDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };
  
  // Texto a mostrar en el botón
  const getDisplayText = () => {
    if (startDate && endDate) {
      return `${formatDisplayDate(startDate)} - ${formatDisplayDate(endDate)}`;
    } else if (startDate) {
      return `Desde ${formatDisplayDate(startDate)}`;
    } else if (endDate) {
      return `Hasta ${formatDisplayDate(endDate)}`;
    }
    return 'Seleccionar fechas';
  };
  
  // Validar rango de fechas
  const validateDateRange = () => {
    if (startDate && endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      if (start > end) {
        setError('La fecha inicial no puede ser posterior a la fecha final');
        return false;
      }
    }
    
    setError('');
    return true;
  };
  
  // Aplicar rango de fechas
  const applyDateRange = () => {
    if (validateDateRange()) {
      onRangeChange({ startDate, endDate });
      setIsOpen(false);
    }
  };
  
  // Limpiar rango de fechas
  const clearDateRange = () => {
    setStartDate('');
    setEndDate('');
    setError('');
    onRangeChange({ startDate: '', endDate: '' });
  };
  
  // Manejar clic fuera del componente para cerrar
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
  
  // Validar fechas cuando cambian
  useEffect(() => {
    if (startDate || endDate) {
      validateDateRange();
    }
  }, [startDate, endDate]);
  
  return (
    <div className="relative" ref={dropdownRef}>
      {/* Botón para abrir el selector */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center w-full px-4 py-2 text-left border border-gray-300 rounded-md bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <FiCalendar className="mr-2 text-gray-400" />
        <span className="flex-grow truncate">{getDisplayText()}</span>
        {(startDate || endDate) && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              clearDateRange();
            }}
            className="ml-2 text-gray-400 hover:text-gray-600"
            aria-label="Limpiar fechas"
          >
            <FiX />
          </button>
        )}
      </button>
      
      {/* Dropdown del selector de fechas */}
      {isOpen && (
        <div className="absolute z-10 mt-1 w-full bg-white rounded-md shadow-lg border border-gray-200">
          <div className="p-4">
            <div className="space-y-4">
              {/* Fecha inicial */}
              <div>
                <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha inicial
                </label>
                <input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              
              {/* Fecha final */}
              <div>
                <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha final
                </label>
                <input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              
              {/* Mensaje de error */}
              {error && (
                <div className="text-sm text-red-600">
                  {error}
                </div>
              )}
              
              {/* Botones de acción */}
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={clearDateRange}
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Limpiar
                </button>
                <button
                  type="button"
                  onClick={applyDateRange}
                  className="px-3 py-1 bg-primary-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary-700"
                >
                  Aplicar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

DateRangePicker.propTypes = {
  onRangeChange: PropTypes.func.isRequired,
  initialStartDate: PropTypes.string,
  initialEndDate: PropTypes.string,
};

export default DateRangePicker;
