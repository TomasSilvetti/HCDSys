import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import { FiArrowUp, FiArrowDown, FiInfo, FiEye } from 'react-icons/fi';

const SearchResults = ({ 
  results, 
  isLoading, 
  query,
  page,
  totalPages,
  totalItems,
  onPageChange,
  onSort
}) => {
  const navigate = useNavigate();
  const [sortField, setSortField] = useState('fecha_modificacion');
  const [sortDirection, setSortDirection] = useState('desc');
  const [hoveredItem, setHoveredItem] = useState(null);
  
  // Manejar clic en documento para navegar a la vista detalle
  const handleDocumentClick = (documentId) => {
    if (!documentId) {
      return;
    }
    
    // Asegurarnos de que el ID sea una cadena de texto
    const formattedId = String(documentId).trim();
    
    if (!formattedId) {
      return;
    }
    
    navigate(`/documentos/${formattedId}`, { 
      state: { 
        from: 'search',
        documentId: formattedId // Incluir el ID en el estado para mayor seguridad
      } 
    });
  };
  
  // Manejar cambio de ordenamiento
  const handleSort = (field) => {
    const newDirection = field === sortField && sortDirection === 'asc' ? 'desc' : 'asc';
    setSortField(field);
    setSortDirection(newDirection);
    onSort(field, newDirection);
  };
  
  // Manejar cambio de página
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      onPageChange(newPage);
    }
  };
  
  // Generar array de páginas a mostrar
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;
    
    if (totalPages <= maxPagesToShow) {
      // Si hay pocas páginas, mostrar todas
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Mostrar un subconjunto de páginas
      if (page <= 3) {
        // Estamos cerca del inicio
        for (let i = 1; i <= 5; i++) {
          pages.push(i);
        }
      } else if (page >= totalPages - 2) {
        // Estamos cerca del final
        for (let i = totalPages - 4; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        // Estamos en el medio
        for (let i = page - 2; i <= page + 2; i++) {
          pages.push(i);
        }
      }
    }
    
    return pages;
  };
  
  // Formatear fecha para mostrar
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };
  
  // Renderizar contenido según estado
  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  if (results.length === 0) {
    if (query) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-500">No se encontraron resultados para "{query}"</p>
          <p className="mt-2 text-sm text-gray-400">Intente con otros términos de búsqueda o filtros</p>
        </div>
      );
    } else {
      return (
        <div className="text-center py-12">
          <p className="text-gray-500">Ingrese un término de búsqueda para encontrar documentos</p>
        </div>
      );
    }
  }
  
  return (
    <div className="space-y-4">
      {/* Información de resultados y ordenamiento */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center text-sm text-gray-600">
        <div>
          Mostrando {((page - 1) * results.length) + 1}-{Math.min(page * results.length, totalItems)} de {totalItems} resultados
        </div>
        <div className="flex items-center mt-2 sm:mt-0">
          <span className="mr-2">Ordenar por:</span>
          <div className="flex space-x-4">
            <button 
              className={`flex items-center ${sortField === 'titulo' ? 'text-primary-600 font-medium' : ''}`}
              onClick={() => handleSort('titulo')}
            >
              Título
              {sortField === 'titulo' && (
                sortDirection === 'asc' ? <FiArrowUp className="ml-1" /> : <FiArrowDown className="ml-1" />
              )}
            </button>
            <button 
              className={`flex items-center ${sortField === 'fecha_modificacion' ? 'text-primary-600 font-medium' : ''}`}
              onClick={() => handleSort('fecha_modificacion')}
            >
              Fecha
              {sortField === 'fecha_modificacion' && (
                sortDirection === 'asc' ? <FiArrowUp className="ml-1" /> : <FiArrowDown className="ml-1" />
              )}
            </button>
          </div>
        </div>
      </div>
      
      {/* Lista de resultados */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {results.map((doc) => (
            <li 
              key={doc.id} 
              className="px-6 py-4 hover:bg-gray-50 relative"
              onMouseEnter={() => setHoveredItem(doc.id)}
              onMouseLeave={() => setHoveredItem(null)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-primary-600">{doc.titulo}</h3>
                  <div className="mt-1 text-sm text-gray-500 grid grid-cols-1 sm:grid-cols-2 gap-x-4">
                    <p>Expediente: <span className="font-medium">{doc.numero_expediente}</span></p>
                    <p>Fecha: <span className="font-medium">{formatDate(doc.fecha_modificacion)}</span></p>
                    {doc.categoria && (
                      <p className="mt-1 sm:mt-0">
                        Categoría: <span className="font-medium">{doc.categoria.nombre}</span>
                      </p>
                    )}
                    {doc.tipo_documento && (
                      <p className="mt-1 sm:mt-0">
                        Tipo: <span className="font-medium">{doc.tipo_documento.nombre}</span>
                      </p>
                    )}
                  </div>
                </div>
                <button 
                  className="ml-4 px-4 py-2 bg-primary-100 text-primary-800 rounded-full text-sm font-medium hover:bg-primary-200 flex items-center"
                  onClick={() => handleDocumentClick(doc.id)}
                >
                  <FiEye className="mr-1" /> Ver detalles
                </button>
              </div>
              
              {/* Tooltip con descripción */}
              {hoveredItem === doc.id && doc.descripcion && (
                <div className="absolute z-10 bg-gray-800 text-white text-sm rounded p-3 shadow-lg max-w-xs left-6 -bottom-2 transform translate-y-full">
                  <div className="flex items-start">
                    <FiInfo className="mr-2 mt-0.5 flex-shrink-0" />
                    <p>{doc.descripcion}</p>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
      
      {/* Paginación */}
      {totalPages > 1 && (
        <div className="flex justify-center mt-6">
          <nav className="inline-flex rounded-md shadow">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              className={`px-3 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium
                ${page === 1 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-700 hover:bg-gray-50'}`}
            >
              Anterior
            </button>
            
            {getPageNumbers().map((pageNum) => (
              <button
                key={pageNum}
                onClick={() => handlePageChange(pageNum)}
                className={`px-4 py-2 border-t border-b border-gray-300 text-sm font-medium
                  ${pageNum === page 
                    ? 'bg-primary-50 text-primary-600 border-primary-500' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'}`}
              >
                {pageNum}
              </button>
            ))}
            
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages}
              className={`px-3 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium
                ${page === totalPages ? 'text-gray-300 cursor-not-allowed' : 'text-gray-700 hover:bg-gray-50'}`}
            >
              Siguiente
            </button>
          </nav>
        </div>
      )}
    </div>
  );
};

SearchResults.propTypes = {
  results: PropTypes.array.isRequired,
  isLoading: PropTypes.bool.isRequired,
  query: PropTypes.string,
  page: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  totalItems: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  onSort: PropTypes.func.isRequired
};

SearchResults.defaultProps = {
  results: [],
  isLoading: false,
  query: '',
  page: 1,
  totalPages: 1,
  totalItems: 0
};

export default SearchResults;
