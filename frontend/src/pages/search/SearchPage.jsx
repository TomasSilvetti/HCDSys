import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchBar from '../../components/search/SearchBar';
import SearchResults from '../../components/search/SearchResults';
import AdvancedFilters from '../../components/search/AdvancedFilters';
import ActiveFilters from '../../components/search/ActiveFilters';
import EmptyResultsSuggestions from '../../components/search/EmptyResultsSuggestions';
import { documentService } from '../../utils/documentService';

const SearchPage = () => {
  // Estado para manejar los parámetros de búsqueda
  const [searchParams, setSearchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState([]);
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
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');
  const [activeFilters, setActiveFilters] = useState([]);
  
  // Obtener parámetros de búsqueda de la URL
  const query = searchParams.get('q') || '';
  const startDate = searchParams.get('startDate') || '';
  const endDate = searchParams.get('endDate') || '';
  const page = parseInt(searchParams.get('page') || '1', 10);
  const categoryId = searchParams.get('categoria_id') || '';
  const typeId = searchParams.get('tipo_documento_id') || '';
  const expedienteNumber = searchParams.get('expediente') || '';
  const userId = searchParams.get('usuario_id') || '';
  const userName = searchParams.get('usuario_nombre') || '';
  
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
  
  // Actualizar los filtros activos cuando cambian los parámetros de URL
  useEffect(() => {
    const filters = [];
    
    if (query) {
      filters.push({
        id: 'query',
        label: 'Búsqueda',
        value: query
      });
    }
    
    if (startDate) {
      const formattedDate = new Date(startDate).toLocaleDateString('es-ES');
      filters.push({
        id: 'startDate',
        label: 'Desde',
        value: formattedDate
      });
    }
    
    if (endDate) {
      const formattedDate = new Date(endDate).toLocaleDateString('es-ES');
      filters.push({
        id: 'endDate',
        label: 'Hasta',
        value: formattedDate
      });
    }
    
    if (categoryId) {
      const category = categories.find(c => c.id.toString() === categoryId);
      if (category) {
        filters.push({
          id: 'category',
          label: 'Categoría',
          value: category.nombre
        });
      }
    }
    
    if (typeId) {
      const type = documentTypes.find(t => t.id.toString() === typeId);
      if (type) {
        filters.push({
          id: 'type',
          label: 'Tipo',
          value: type.nombre
        });
      }
    }
    
    if (expedienteNumber) {
      filters.push({
        id: 'expediente',
        label: 'Expediente',
        value: expedienteNumber
      });
    }
    
    if (userId && userName) {
      filters.push({
        id: 'user',
        label: 'Usuario',
        value: userName
      });
    }
    
    setActiveFilters(filters);
  }, [query, startDate, endDate, categoryId, typeId, expedienteNumber, userId, userName, categories, documentTypes]);
  
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
    if (startDate) params.fecha_desde = startDate;
    if (endDate) params.fecha_hasta = endDate;
    
    // Añadir otros filtros si están presentes
    if (categoryId) params.categoria_id = categoryId;
    if (typeId) params.tipo_documento_id = typeId;
    if (expedienteNumber) params.numero_expediente = expedienteNumber;
    if (userId) params.usuario_id = userId;
    
    // Añadir ordenamiento
    params.sort_by = sortConfig.field;
    params.sort_order = sortConfig.direction;
    
    // Actualizar los parámetros de URL
    const newSearchParams = {
      q: searchQuery,
      page: '1',
      ...(startDate && { startDate }),
      ...(endDate && { endDate }),
      ...(categoryId && { categoria_id: categoryId }),
      ...(typeId && { tipo_documento_id: typeId }),
      ...(expedienteNumber && { expediente: expedienteNumber }),
      ...(userId && { usuario_id: userId }),
      ...(userName && { usuario_nombre: userName })
    };
    
    setSearchParams(newSearchParams);
    
    // Realizar la búsqueda
    performSearch(params);
  };
  
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
    if (startDate) params.fecha_desde = startDate;
    if (endDate) params.fecha_hasta = endDate;
    if (categoryId) params.categoria_id = categoryId;
    if (typeId) params.tipo_documento_id = typeId;
    if (expedienteNumber) params.numero_expediente = expedienteNumber;
    if (userId) params.usuario_id = userId;
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
    if (startDate) params.fecha_desde = startDate;
    if (endDate) params.fecha_hasta = endDate;
    if (categoryId) params.categoria_id = categoryId;
    if (typeId) params.tipo_documento_id = typeId;
    if (expedienteNumber) params.numero_expediente = expedienteNumber;
    if (userId) params.usuario_id = userId;
    
    // Realizar la búsqueda
    performSearch(params);
  };
  
  // Función para manejar aplicación de filtros avanzados
  const handleApplyAdvancedFilters = (filters) => {
    // Actualizar parámetros de URL con los filtros
    const newSearchParams = {
      ...(query && { q: query }),
      page: '1',
      ...(filters.startDate && { startDate: filters.startDate }),
      ...(filters.endDate && { endDate: filters.endDate }),
      ...(filters.categoryId && { categoria_id: filters.categoryId }),
      ...(filters.typeId && { tipo_documento_id: filters.typeId }),
      ...(filters.expedienteNumber && { expediente: filters.expedienteNumber }),
      ...(filters.userId && { usuario_id: filters.userId }),
      ...(filters.userName && { usuario_nombre: filters.userName })
    };
    
    setSearchParams(newSearchParams);
    
    // Crear objeto con los parámetros para la búsqueda
    const params = {
      ...(query && { termino: query }),
      page: 1,
      page_size: pagination.pageSize,
      sort_by: sortConfig.field,
      sort_order: sortConfig.direction,
      ...(filters.startDate && { fecha_desde: filters.startDate }),
      ...(filters.endDate && { fecha_hasta: filters.endDate }),
      ...(filters.categoryId && { categoria_id: filters.categoryId }),
      ...(filters.typeId && { tipo_documento_id: filters.typeId }),
      ...(filters.expedienteNumber && { numero_expediente: filters.expedienteNumber }),
      ...(filters.userId && { usuario_id: filters.userId })
    };
    
    // Realizar la búsqueda
    performSearch(params);
  };
  
  // Función para limpiar filtros
  const handleClearFilters = () => {
    // Mantener solo la consulta de búsqueda y resetear página
    const newSearchParams = query ? { q: query, page: '1' } : { page: '1' };
    setSearchParams(newSearchParams);
    
    // Realizar búsqueda solo con el término (si existe)
    const params = {
      page: 1,
      page_size: pagination.pageSize,
      sort_by: sortConfig.field,
      sort_order: sortConfig.direction
    };
    
    if (query) {
      params.termino = query;
    }
    
    performSearch(params);
  };
  
  // Función para eliminar un filtro específico
  const handleRemoveFilter = (filterId) => {
    const newSearchParams = new URLSearchParams(searchParams);
    
    switch (filterId) {
      case 'query':
        newSearchParams.delete('q');
        break;
      case 'startDate':
        newSearchParams.delete('startDate');
        break;
      case 'endDate':
        newSearchParams.delete('endDate');
        break;
      case 'category':
        newSearchParams.delete('categoria_id');
        break;
      case 'type':
        newSearchParams.delete('tipo_documento_id');
        break;
      case 'expediente':
        newSearchParams.delete('expediente');
        break;
      case 'user':
        newSearchParams.delete('usuario_id');
        newSearchParams.delete('usuario_nombre');
        break;
      default:
        break;
    }
    
    // Resetear a la primera página
    newSearchParams.set('page', '1');
    setSearchParams(newSearchParams);
    
    // Crear objeto con los parámetros restantes para la búsqueda
    const params = {
      page: 1,
      page_size: pagination.pageSize,
      sort_by: sortConfig.field,
      sort_order: sortConfig.direction
    };
    
    // Añadir los parámetros que quedan
    if (filterId !== 'query' && newSearchParams.has('q')) {
      params.termino = newSearchParams.get('q');
    }
    
    if (filterId !== 'startDate' && newSearchParams.has('startDate')) {
      params.fecha_desde = newSearchParams.get('startDate');
    }
    
    if (filterId !== 'endDate' && newSearchParams.has('endDate')) {
      params.fecha_hasta = newSearchParams.get('endDate');
    }
    
    if (filterId !== 'category' && newSearchParams.has('categoria_id')) {
      params.categoria_id = newSearchParams.get('categoria_id');
    }
    
    if (filterId !== 'type' && newSearchParams.has('tipo_documento_id')) {
      params.tipo_documento_id = newSearchParams.get('tipo_documento_id');
    }
    
    if (filterId !== 'expediente' && newSearchParams.has('expediente')) {
      params.numero_expediente = newSearchParams.get('expediente');
    }
    
    if (filterId !== 'user' && newSearchParams.has('usuario_id')) {
      params.usuario_id = newSearchParams.get('usuario_id');
    }
    
    // Realizar la búsqueda
    performSearch(params);
  };
  
  // Realizar búsqueda inicial si hay un término o filtros en la URL
  useEffect(() => {
    if (query || startDate || endDate || categoryId || typeId || expedienteNumber || userId) {
      // Crear objeto con los parámetros para la búsqueda
      const params = {
        page: page,
        page_size: pagination.pageSize,
        sort_by: sortConfig.field,
        sort_order: sortConfig.direction
      };
      
      // Añadir otros parámetros
      if (query) params.termino = query;
      if (startDate) params.fecha_desde = startDate;
      if (endDate) params.fecha_hasta = endDate;
      if (categoryId) params.categoria_id = categoryId;
      if (typeId) params.tipo_documento_id = typeId;
      if (expedienteNumber) params.numero_expediente = expedienteNumber;
      if (userId) params.usuario_id = userId;
      
      // Realizar la búsqueda
      performSearch(params);
    }
  }, []);
  
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
      
      {/* Filtros activos */}
      {activeFilters.length > 0 && (
        <ActiveFilters 
          filters={activeFilters} 
          onRemoveFilter={handleRemoveFilter} 
          onClearAllFilters={handleClearFilters} 
        />
      )}
      
      {/* Filtros avanzados */}
      <AdvancedFilters
        categories={categories}
        documentTypes={documentTypes}
        initialFilters={{
          startDate,
          endDate,
          categoryId,
          typeId,
          expedienteNumber,
          userId,
          userName
        }}
        onApplyFilters={handleApplyAdvancedFilters}
        onClearFilters={handleClearFilters}
      />
      
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
        {results.length === 0 && !isLoading && (query || activeFilters.length > 0) ? (
          <EmptyResultsSuggestions 
            query={query} 
            filters={{
              startDate,
              endDate,
              categoryId,
              typeId,
              expedienteNumber,
              userId
            }}
            onClearFilters={handleClearFilters}
          />
        ) : (
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
        )}
      </div>
    </div>
  );
};

export default SearchPage;