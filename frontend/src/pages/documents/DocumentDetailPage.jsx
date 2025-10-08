import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { FiArrowLeft, FiDownload, FiClock, FiUser, FiFileText, FiTag, FiCalendar, FiLock } from 'react-icons/fi';
import { documentService } from '../../utils/documentService';
import { useAuth } from '../../context/AuthContext';
import VersionHistory from '../../components/documents/VersionHistory';
import PermissionCheck from '../../components/auth/PermissionCheck';

const DocumentDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { currentUser, isAuthenticated } = useAuth();
  
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isDownloading, setIsDownloading] = useState(false);
  
  // Verificar si el usuario tiene permisos para ver el documento
  const canViewDocument = isAuthenticated && (
    currentUser?.role_id === 1 || // Administrador
    document?.usuario_id === currentUser?.id || // Creador del documento
    (currentUser?.permissions && (
      currentUser.permissions.includes('DOCUMENT_VIEW_ALL') || 
      currentUser.permissions.includes('DOCUMENT_VIEW_RESTRICTED')
    ))
  );
  
  // Verificar si el usuario tiene permisos para descargar
  const canDownload = isAuthenticated && (
    currentUser?.role_id === 1 || // Administrador
    document?.usuario_id === currentUser?.id || // Creador del documento
    (currentUser?.permissions && currentUser.permissions.includes('DOCUMENT_DOWNLOAD'))
  );
  
  // Cargar datos del documento
  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setLoading(true);
        const data = await documentService.getDocument(id);
        setDocument(data);
      } catch (error) {
        console.error('Error al cargar documento:', error);
        setError('No se pudo cargar el documento. Por favor, intente de nuevo.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDocument();
  }, [id]);
  
  // Función para formatear fechas
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  // Función para volver a la página anterior
  const handleGoBack = () => {
    // Si venimos de la página de búsqueda, volver allí
    if (location.state?.from === 'search') {
      navigate(-1);
    } else {
      // Si no, ir a la página de búsqueda
      navigate('/buscar');
    }
  };
  
  // Función para descargar el documento
  const handleDownload = async () => {
    if (!canDownload || !document) return;
    
    try {
      setIsDownloading(true);
      
      // Usar el servicio de documentos para la descarga
      await documentService.downloadDocument(id, `${document.titulo}${document.extension_archivo || '.pdf'}`);
      
      setIsDownloading(false);
    } catch (error) {
      console.error('Error al descargar documento:', error);
      setError('No se pudo descargar el documento. Por favor, intente de nuevo.');
      setIsDownloading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }
  
  if (error || !document) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6">
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
            <p className="text-gray-700">{error || 'No se pudo encontrar el documento solicitado.'}</p>
            <button 
              onClick={handleGoBack}
              className="mt-6 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
            >
              Volver
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  // Verificar permisos para ver el documento
  if (!canViewDocument) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6">
          <div className="text-center py-12">
            <FiLock className="mx-auto h-16 w-16 text-red-600 mb-4" />
            <h2 className="text-2xl font-bold text-red-600 mb-4">Acceso Denegado</h2>
            <p className="text-gray-700">No tiene permisos para ver este documento.</p>
            <button 
              onClick={handleGoBack}
              className="mt-6 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
            >
              Volver
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Botón para volver */}
      <button 
        onClick={handleGoBack}
        className="mb-6 flex items-center text-gray-600 hover:text-gray-900"
      >
        <FiArrowLeft className="mr-2" /> Volver a resultados
      </button>
      
      {/* Encabezado del documento */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
        <div className="px-6 py-5 border-b border-gray-200">
          <div className="flex justify-between items-start">
            <h1 className="text-2xl font-bold text-gray-900">{document.titulo}</h1>
            {canDownload && (
              <button 
                onClick={handleDownload}
                disabled={isDownloading}
                className={`px-4 py-2 rounded-md flex items-center ${
                  isDownloading 
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                    : 'bg-primary-600 text-white hover:bg-primary-700'
                }`}
              >
                <FiDownload className="mr-2" /> 
                {isDownloading ? 'Descargando...' : 'Descargar'}
              </button>
            )}
          </div>
          <p className="mt-2 text-sm text-gray-500">Expediente: <span className="font-medium">{document.numero_expediente}</span></p>
        </div>
        
        {/* Detalles del documento */}
        <div className="px-6 py-5">
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
            <div className="col-span-1">
              <dt className="text-sm font-medium text-gray-500 flex items-center">
                <FiCalendar className="mr-2" /> Fecha de creación
              </dt>
              <dd className="mt-1 text-sm text-gray-900">{formatDate(document.fecha_creacion)}</dd>
            </div>
            
            <div className="col-span-1">
              <dt className="text-sm font-medium text-gray-500 flex items-center">
                <FiClock className="mr-2" /> Última modificación
              </dt>
              <dd className="mt-1 text-sm text-gray-900">{formatDate(document.fecha_modificacion)}</dd>
            </div>
            
            <div className="col-span-1">
              <dt className="text-sm font-medium text-gray-500 flex items-center">
                <FiUser className="mr-2" /> Creado por
              </dt>
              <dd className="mt-1 text-sm text-gray-900">
                {document.usuario ? `${document.usuario.nombre} ${document.usuario.apellido}` : 'Usuario no disponible'}
              </dd>
            </div>
            
            <div className="col-span-1">
              <dt className="text-sm font-medium text-gray-500 flex items-center">
                <FiFileText className="mr-2" /> Tipo de documento
              </dt>
              <dd className="mt-1 text-sm text-gray-900">
                {document.tipo_documento ? document.tipo_documento.nombre : 'No especificado'}
              </dd>
            </div>
            
            {document.categoria && (
              <div className="col-span-1">
                <dt className="text-sm font-medium text-gray-500 flex items-center">
                  <FiTag className="mr-2" /> Categoría
                </dt>
                <dd className="mt-1 text-sm text-gray-900">{document.categoria.nombre}</dd>
              </div>
            )}
          </dl>
          
          {/* Descripción */}
          {document.descripcion && (
            <div className="mt-6 border-t border-gray-200 pt-6">
              <h3 className="text-lg font-medium text-gray-900">Descripción</h3>
              <div className="mt-2 prose prose-sm text-gray-700">
                <p>{document.descripcion}</p>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Componente de historial de versiones */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-6 py-5 border-b border-gray-200">
          <h2 className="text-xl font-medium text-gray-900">Historial de versiones</h2>
        </div>
        <div className="px-6 py-5">
          <VersionHistory documentId={id} canDownload={canDownload} />
        </div>
      </div>
    </div>
  );
};

export default DocumentDetailPage;
