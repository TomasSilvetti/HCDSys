import { useState } from 'react'
import { FiSearch, FiFilter, FiX, FiCalendar } from 'react-icons/fi'

// Datos de ejemplo para simular resultados de búsqueda
const mockResults = [
  {
    id: 1,
    titulo: 'Ordenanza Municipal 123/2023',
    numero_expediente: 'EXP-2023-00123',
    fecha_creacion: '2023-05-15',
    categoria: 'Ordenanzas',
    descripcion: 'Ordenanza que regula el uso de espacios públicos en el municipio de Lules.'
  },
  {
    id: 2,
    titulo: 'Resolución 45/2023 - Presupuesto anual',
    numero_expediente: 'EXP-2023-00045',
    fecha_creacion: '2023-02-10',
    categoria: 'Resoluciones',
    descripcion: 'Resolución que aprueba el presupuesto anual para el ejercicio 2023.'
  },
  {
    id: 3,
    titulo: 'Acta de Sesión Ordinaria 15/2023',
    numero_expediente: 'ACTA-2023-00015',
    fecha_creacion: '2023-07-22',
    categoria: 'Actas',
    descripcion: 'Acta de la sesión ordinaria número 15 del Honorable Concejo Deliberante.'
  }
]

const SearchPage = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [results, setResults] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  
  // Filtros avanzados
  const [documentType, setDocumentType] = useState('')
  const [expedientNumber, setExpedientNumber] = useState('')
  const [category, setCategory] = useState('')
  
  const handleSearch = async (e) => {
    e.preventDefault()
    
    if (!searchTerm.trim()) {
      alert('Ingrese un término de búsqueda')
      return
    }
    
    setIsLoading(true)
    setHasSearched(true)
    
    try {
      // Simulación de llamada a API - reemplazar con llamada real
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // Filtrar resultados de ejemplo según el término de búsqueda
      const filteredResults = mockResults.filter(doc => 
        doc.titulo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.numero_expediente.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.descripcion.toLowerCase().includes(searchTerm.toLowerCase())
      )
      
      setResults(filteredResults)
    } catch (error) {
      console.error('Error en la búsqueda:', error)
    } finally {
      setIsLoading(false)
    }
  }
  
  const clearFilters = () => {
    setDateFrom('')
    setDateTo('')
    setDocumentType('')
    setExpedientNumber('')
    setCategory('')
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Búsqueda de Documentos</h1>
      
      {/* Formulario de búsqueda */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <form onSubmit={handleSearch}>
          <div className="flex flex-col md:flex-row gap-4">
            {/* Campo de búsqueda */}
            <div className="flex-grow relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FiSearch className="text-secondary-400" />
              </div>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10 w-full"
                placeholder="Buscar por título o número de expediente"
              />
            </div>
            
            {/* Botón de búsqueda */}
            <button 
              type="submit" 
              className="btn btn-primary flex items-center justify-center gap-2"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
              ) : (
                <>
                  <FiSearch /> Buscar
                </>
              )}
            </button>
            
            {/* Botón de filtros */}
            <button 
              type="button" 
              className="btn btn-secondary flex items-center justify-center gap-2"
              onClick={() => setShowFilters(!showFilters)}
            >
              {showFilters ? <FiX /> : <FiFilter />}
              {showFilters ? 'Ocultar Filtros' : 'Más Filtros'}
            </button>
          </div>
          
          {/* Filtros avanzados */}
          {showFilters && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Filtro por fechas */}
              <div>
                <label className="label">Fecha desde</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <FiCalendar className="text-secondary-400" />
                  </div>
                  <input
                    type="date"
                    value={dateFrom}
                    onChange={(e) => setDateFrom(e.target.value)}
                    className="input pl-10 w-full"
                  />
                </div>
              </div>
              
              <div>
                <label className="label">Fecha hasta</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <FiCalendar className="text-secondary-400" />
                  </div>
                  <input
                    type="date"
                    value={dateTo}
                    onChange={(e) => setDateTo(e.target.value)}
                    className="input pl-10 w-full"
                  />
                </div>
              </div>
              
              {/* Filtro por tipo de documento */}
              <div>
                <label className="label">Tipo de documento</label>
                <select
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  className="input w-full"
                >
                  <option value="">Todos los tipos</option>
                  <option value="ordenanza">Ordenanza</option>
                  <option value="resolucion">Resolución</option>
                  <option value="acta">Acta</option>
                  <option value="decreto">Decreto</option>
                </select>
              </div>
              
              {/* Filtro por número de expediente */}
              <div>
                <label className="label">Número de expediente</label>
                <input
                  type="text"
                  value={expedientNumber}
                  onChange={(e) => setExpedientNumber(e.target.value)}
                  className="input w-full"
                  placeholder="Ej: EXP-2023-00123"
                />
              </div>
              
              {/* Filtro por categoría */}
              <div>
                <label className="label">Categoría</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="input w-full"
                >
                  <option value="">Todas las categorías</option>
                  <option value="ordenanzas">Ordenanzas</option>
                  <option value="resoluciones">Resoluciones</option>
                  <option value="actas">Actas</option>
                  <option value="decretos">Decretos</option>
                </select>
              </div>
              
              {/* Botón para limpiar filtros */}
              <div className="flex items-end">
                <button
                  type="button"
                  onClick={clearFilters}
                  className="btn btn-secondary w-full"
                >
                  Limpiar Filtros
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
      
      {/* Resultados de búsqueda */}
      {hasSearched && (
        <div>
          <h2 className="text-xl font-semibold mb-4">
            Resultados de la búsqueda
            {results.length > 0 && <span className="text-secondary-500 ml-2">({results.length} encontrados)</span>}
          </h2>
          
          {results.length > 0 ? (
            <div className="space-y-4">
              {results.map((doc) => (
                <div 
                  key={doc.id} 
                  className="bg-white p-4 rounded-lg shadow-sm border border-secondary-200 hover:shadow-md transition-shadow"
                >
                  <h3 className="text-lg font-semibold text-primary-700">{doc.titulo}</h3>
                  <div className="flex flex-wrap gap-x-6 gap-y-2 mt-2 text-sm text-secondary-600">
                    <p><span className="font-medium">Expediente:</span> {doc.numero_expediente}</p>
                    <p><span className="font-medium">Fecha:</span> {new Date(doc.fecha_creacion).toLocaleDateString('es-AR')}</p>
                    <p><span className="font-medium">Categoría:</span> {doc.categoria}</p>
                  </div>
                  <p className="mt-2 text-secondary-700">{doc.descripcion}</p>
                  <div className="mt-3">
                    <button className="text-primary-600 hover:text-primary-800 text-sm font-medium">
                      Ver detalle
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-secondary-50 border border-secondary-200 rounded-lg p-8 text-center">
              <p className="text-secondary-600">No se encontraron documentos que coincidan con tu búsqueda.</p>
              <p className="text-secondary-500 mt-2">Intenta con otros términos o ajusta los filtros.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default SearchPage
