import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchBar from '../../components/search/SearchBar';
import DateRangePicker from '../../components/search/DateRangePicker';
import SearchResults from '../../components/search/SearchResults';
import { documentService } from '../../utils/documentService';
import { FiFilter } from 'react-icons/fi';

const SearchPage = () => {
  // Estado para manejar los parámetros de búsqueda
  const [searchParams, setSearchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [results, setResults] = useState([]);
  const [dateRange, setDateRange] = useState({ startDate: '', endDate: '' });
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    totalItems: 0,
    totalPages: 0
  });
  const [sortConfig, setSortConfig] = useState({
    field: 'fecha_modificacion',
    direction: 'desc'
  });
  const [categories, setCategories] = useState([]);
  const [documentTypes, setDocumentTypes] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [error, setError] = useState('');
  
  // Obtener parámetros de búsqueda de la URL
  const query = searchParams.get('q') || '';
  const startDate = searchParams.get('startDate') || '';
  const endDate = searchParams.get('endDate') || '';
  const page = parseInt(searchParams.get('page') || '1', 10);
  const categoryId = searchParams.get('categoria_id') || '';
  const typeId = searchParams.get('tipo_documento_id') || '';
  
  // Cargar categorías y tipos de documentos
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const [categoriesData, typesData] = await Promise.all([
          documentService.getCategories(),
          documentService.getDocumentTypes()
        ]);
        
        setCategories(categoriesData);
        setDocumentTypes(typesData);
      } catch (error) {
        console.error('Error al cargar filtros:', error);
        setError('Error al cargar los filtros. Por favor, intente de nuevo.');
      }
    };
    
    fetchFilters();
  }, []);
  
  // Función para realizar la búsqueda
  const performSearch = async (params) => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await documentService.searchDocuments(params);
      setResults(response.items || []);
      setPagination({
        page: response.page || 1,
        pageSize: response.page_size || 10,
        totalItems: response.total || 0,
        totalPages: response.total_pages || 0
      });
    } catch (error) {
      console.error('Error al buscar documentos:', error);
      setError('Error al buscar documentos. Por favor, intente de nuevo.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Función para manejar la búsqueda
  const handleSearch = (searchQuery) => {
    // Crear objeto con los parámetros actuales
    const params = { 
      termino: searchQuery,
      page: 1 // Resetear a primera página al hacer nueva búsqueda
    };
    
    // Añadir fechas si están presentes
    if (dateRange.startDate) params.fecha_desde = dateRange.startDate;
    if (dateRange.endDate) params.fecha_hasta = dateRange.endDate;
    
    // Añadir categoría y tipo si están seleccionados
    if (selectedCategory) params.categoria_id = selectedCategory;
    if (selectedType) params.tipo_documento_id = selectedType;
    
    // Añadir ordenamiento
    params.sort_by = sortConfig.field;
    params.sort_order = sortConfig.direction;
    
    // Actualizar los parámetros de URL
    setSearchParams({
      q: searchQuery,
      page: '1',
      ...(dateRange.startDate && { startDate: dateRange.startDate }),
      ...(dateRange.endDate && { endDate: dateRange.endDate }),
      ...(selectedCategory && { categoria_id: selectedCategory }),
      ...(selectedType && { tipo_documento_id: selectedType })
    });
    
    // Realizar la búsqueda
    performSearch(params);
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
  
  // Función para manejar cambio de página
  const handlePageChange = (newPage) => {
    // Actualizar parámetros de URL
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set('page', newPage.toString());
    setSearchParams(newSearchParams);
    
    // Crear objeto con los parámetros actuales para la búsqueda
    const params = {
      termino: query,
      page: newPage,
      page_size: pagination.pageSize
    };
    
    // Añadir otros parámetros
    if (dateRange.startDate) params.fecha_desde = dateRange.startDate;
    if (dateRange.endDate) params.fecha_hasta = dateRange.endDate;
    if (selectedCategory) params.categoria_id = selectedCategory;
    if (selectedType) params.tipo_documento_id = selectedType;
    params.sort_by = sortConfig.field;
    params.sort_order = sortConfig.direction;
    
    // Realizar la búsqueda
    performSearch(params);
  };
  
  // Función para manejar cambio de ordenamiento
  const handleSort = (field, direction) => {
    setSortConfig({ field, direction });
    
    // Crear objeto con los parámetros actuales para la búsqueda
    const params = {
      termino: query,
      page: pagination.page,
      page_size: pagination.pageSize,
      sort_by: field,
      sort_order: direction
    };
    
    // Añadir otros parámetros
    if (dateRange.startDate) params.fecha_desde = dateRange.startDate;
    if (dateRange.endDate) params.fecha_hasta = dateRange.endDate;
    if (selectedCategory) params.categoria_id = selectedCategory;
    if (selectedType) params.tipo_documento_id = selectedType;
    
    // Realizar la búsqueda
    performSearch(params);
  };
  
  // Función para manejar cambio de categoría
  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
  };
  
  // Función para manejar cambio de tipo de documento
  const handleTypeChange = (e) => {
    setSelectedType(e.target.value);
  };
  
  // Función para limpiar filtros
  const handleClearFilters = () => {
    setDateRange({ startDate: '', endDate: '' });
    setSelectedCategory('');
    setSelectedType('');
  };
  
  // Realizar búsqueda inicial si hay un término en la URL
  useEffect(() => {
    if (query) {
      // Inicializar filtros desde URL
      if (categoryId) setSelectedCategory(categoryId);
      if (typeId) setSelectedType(typeId);
      
      // Crear objeto con los parámetros para la búsqueda
      const params = {
        termino: query,
        page: page,
        page_size: pagination.pageSize
      };
      
      // Añadir otros parámetros
      if (startDate) params.fecha_desde = startDate;
      if (endDate) params.fecha_hasta = endDate;
      if (categoryId) params.categoria_id = categoryId;
      if (typeId) params.tipo_documento_id = typeId;
      params.sort_by = sortConfig.field;
      params.sort_order = sortConfig.direction;
      
      // Realizar la búsqueda
      performSearch(params);
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
            
            {/* Selector de categoría */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Categoría</label>
              <select 
                className="block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                value={selectedCategory}
                onChange={handleCategoryChange}
              >
                <option value="">Todas</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.nombre}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Selector de tipo de documento */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Tipo de documento</label>
              <select 
                className="block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                value={selectedType}
                onChange={handleTypeChange}
              >
                <option value="">Todos</option>
                {documentTypes.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.nombre}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="mt-4 flex justify-end space-x-2">
            <button 
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              onClick={handleClearFilters}
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
      
      {/* Mensaje de error */}
      {error && (
        <div className="mt-6 bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Resultados de búsqueda */}
      <div className="mt-6">
        <SearchResults
          results={results}
          isLoading={isLoading}
          query={query}
          page={pagination.page}
          totalPages={pagination.totalPages}
          totalItems={pagination.totalItems}
          onPageChange={handlePageChange}
          onSort={handleSort}
        />
      </div>
    </div>
  );
};

export default SearchPage;