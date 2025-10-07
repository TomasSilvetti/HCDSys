import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchBar from '../../components/search/SearchBar';
import DateRangePicker from '../../components/search/DateRangePicker';
import { FiFilter } from 'react-icons/fi';

const SearchPage = () => {
  // Estado para manejar los parámetros de búsqueda
  const [searchParams, setSearchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [results, setResults] = useState([]);
  const [dateRange, setDateRange] = useState({ startDate: '', endDate: '' });
  
  // Obtener parámetros de búsqueda de la URL
  const query = searchParams.get('q') || '';
  const startDate = searchParams.get('startDate') || '';
  const endDate = searchParams.get('endDate') || '';
  
  // Función para manejar la búsqueda
  const handleSearch = (searchQuery) => {
    // Crear objeto con los parámetros actuales
    const params = { q: searchQuery };
    
    // Añadir fechas si están presentes
    if (dateRange.startDate) params.startDate = dateRange.startDate;
    if (dateRange.endDate) params.endDate = dateRange.endDate;
    
    // Actualizar los parámetros de URL
    setSearchParams(params);
    
    // Simular una búsqueda
    setIsLoading(true);
    
    // Aquí se realizaría la llamada a la API
    setTimeout(() => {
      // Simulación de resultados
      setResults([
        { id: 1, title: 'Documento de ejemplo 1', expediente: 'EXP-2023-001', fecha: '2023-10-15' },
        { id: 2, title: 'Documento de ejemplo 2', expediente: 'EXP-2023-002', fecha: '2023-09-22' },
        { id: 3, title: 'Documento de ejemplo 3', expediente: 'EXP-2023-003', fecha: '2023-08-10' },
      ]);
      setIsLoading(false);
    }, 1000);
  };
  
  // Función para manejar cambios en el rango de fechas
  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };
  
  // Inicializar el estado del rango de fechas desde la URL
  useEffect(() => {
    if (startDate || endDate) {
      setDateRange({
        startDate: startDate || '',
        endDate: endDate || ''
      });
    }
  }, [startDate, endDate]);
  
  // Realizar búsqueda inicial si hay un término en la URL
  useEffect(() => {
    if (query) {
      // No llamamos a handleSearch para evitar un ciclo infinito
      // ya que handleSearch actualiza los searchParams
      setIsLoading(true);
      
      // Simular búsqueda inicial
      setTimeout(() => {
        setResults([
          { id: 1, title: 'Documento de ejemplo 1', expediente: 'EXP-2023-001', fecha: '2023-10-15' },
          { id: 2, title: 'Documento de ejemplo 2', expediente: 'EXP-2023-002', fecha: '2023-09-22' },
          { id: 3, title: 'Documento de ejemplo 3', expediente: 'EXP-2023-003', fecha: '2023-08-10' },
        ]);
        setIsLoading(false);
      }, 1000);
    }
  }, []);
  
  // Función para alternar la visibilidad de los filtros
  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8">Búsqueda de Documentos</h1>
      
      {/* Barra de búsqueda */}
      <div className="mb-6">
        <SearchBar 
          onSearch={handleSearch} 
          isLoading={isLoading} 
          initialQuery={query}
        />
      </div>
      
      {/* Botón para mostrar/ocultar filtros */}
      <div className="flex justify-end mb-4">
        <button
          onClick={toggleFilters}
          className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          <FiFilter className="mr-2" /> 
          {showFilters ? 'Ocultar filtros' : 'Mostrar filtros'}
        </button>
      </div>
      
      {/* Sección de filtros */}
      {showFilters && (
        <div className="bg-gray-50 p-4 rounded-lg mb-6 border border-gray-200">
          <h2 className="text-lg font-medium mb-4">Filtros</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Componente de selección de rango de fechas */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Rango de fechas</label>
              <DateRangePicker
                onRangeChange={handleDateRangeChange}
                initialStartDate={dateRange.startDate}
                initialEndDate={dateRange.endDate}
              />
            </div>
            
            {/* Espacio para futuros filtros */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Tipo de documento</label>
              <select className="block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500">
                <option value="">Todos</option>
                <option value="1">Resolución</option>
                <option value="2">Expediente</option>
                <option value="3">Informe</option>
              </select>
            </div>
          </div>
          
          <div className="mt-4 flex justify-end space-x-2">
            <button 
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              onClick={() => {
                setDateRange({ startDate: '', endDate: '' });
                // Limpiar otros filtros aquí
              }}
            >
              Limpiar filtros
            </button>
            <button 
              className="px-4 py-2 bg-primary-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary-700"
              onClick={() => {
                if (query) {
                  handleSearch(query);
                }
              }}
            >
              Aplicar filtros
            </button>
          </div>
        </div>
      )}
      
      {/* Resultados de búsqueda */}
      <div className="mt-6">
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
          </div>
        ) : results.length > 0 ? (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {results.map((doc) => (
                <li key={doc.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-medium text-primary-600">{doc.title}</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        Expediente: {doc.expediente} | Fecha: {doc.fecha}
                      </p>
                    </div>
                    <button className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
                      Ver detalles
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : query ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No se encontraron resultados para "{query}"</p>
            <p className="mt-2 text-sm text-gray-400">Intente con otros términos de búsqueda o filtros</p>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">Ingrese un término de búsqueda para encontrar documentos</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;