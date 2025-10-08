import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { FiDownload, FiClock, FiUser } from 'react-icons/fi';
import { documentService } from '../../utils/documentService';

const VersionHistory = ({ documentId, canDownload }) => {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadingVersion, setDownloadingVersion] = useState(null);
  
  // Cargar versiones del documento
  useEffect(() => {
    const fetchVersions = async () => {
      try {
        setLoading(true);
        const data = await documentService.getDocumentVersions(documentId);
        setVersions(data || []);
      } catch (error) {
        console.error('Error al cargar versiones:', error);
        setError('No se pudieron cargar las versiones del documento.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchVersions();
  }, [documentId]);
  
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
  
  // Función para descargar una versión específica
  const handleDownloadVersion = async (versionId) => {
    if (!canDownload) return;
    
    try {
      setDownloadingVersion(versionId);
      await documentService.downloadDocumentVersion(documentId, versionId);
    } catch (error) {
      console.error('Error al descargar versión:', error);
      setError('No se pudo descargar la versión del documento.');
    } finally {
      setDownloadingVersion(null);
    }
  };
  
  if (loading) {
    return (
      <div className="py-4 flex justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="py-4 text-center text-red-600">
        <p>{error}</p>
      </div>
    );
  }
  
  if (versions.length === 0) {
    return (
      <div className="py-4 text-center text-gray-500 italic">
        <p>Este documento no tiene versiones anteriores registradas.</p>
      </div>
    );
  }
  
  return (
    <div className="overflow-hidden">
      <ul className="divide-y divide-gray-200">
        {versions.map((version) => (
          <li key={version.id} className="py-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-lg font-medium text-gray-900">
                  Versión {version.numero_version}
                </h4>
                <div className="mt-1 flex items-center text-sm text-gray-500">
                  <FiClock className="mr-1" />
                  <span>{formatDate(version.fecha_version)}</span>
                </div>
                {version.usuario && (
                  <div className="mt-1 flex items-center text-sm text-gray-500">
                    <FiUser className="mr-1" />
                    <span>{version.usuario.nombre} {version.usuario.apellido}</span>
                  </div>
                )}
                {version.comentario && (
                  <p className="mt-2 text-sm text-gray-700">{version.comentario}</p>
                )}
              </div>
              
              {canDownload && (
                <button
                  onClick={() => handleDownloadVersion(version.id)}
                  disabled={downloadingVersion === version.id}
                  className={`ml-4 px-3 py-1 rounded flex items-center text-sm ${
                    downloadingVersion === version.id
                      ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      : 'bg-primary-100 text-primary-800 hover:bg-primary-200'
                  }`}
                >
                  <FiDownload className="mr-1" />
                  {downloadingVersion === version.id ? 'Descargando...' : 'Descargar'}
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

VersionHistory.propTypes = {
  documentId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  canDownload: PropTypes.bool
};

VersionHistory.defaultProps = {
  canDownload: false
};

export default VersionHistory;
