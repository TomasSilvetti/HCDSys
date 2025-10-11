import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { FiDownload, FiClock, FiUser, FiRefreshCw, FiGitBranch, FiFileText, FiCheck, FiX } from 'react-icons/fi';
import { documentService } from '../../utils/documentService';

const VersionHistory = ({ documentId, canDownload, canEdit, documentTitle }) => {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadingVersion, setDownloadingVersion] = useState(null);
  const [restoringVersion, setRestoringVersion] = useState(null);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [restoreComment, setRestoreComment] = useState('');
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [compareVersions, setCompareVersions] = useState({ version1: null, version2: null });
  const [compareResult, setCompareResult] = useState(null);
  const [comparingVersions, setComparingVersions] = useState(false);
  
  // Cargar versiones del documento
  useEffect(() => {
    const fetchVersions = async () => {
      // Validar que documentId sea válido antes de hacer la petición
      if (!documentId || documentId === 'undefined' || documentId === 'null') {
        setError('ID de documento inválido');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const data = await documentService.getDocumentVersions(documentId);
        setVersions(data || []);
      } catch (error) {
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
      setError('No se pudo descargar la versión del documento.');
    } finally {
      setDownloadingVersion(null);
    }
  };
  
  // Función para abrir modal de restauración
  const handleOpenRestoreModal = (version) => {
    if (!canEdit) return;
    
    setSelectedVersion(version);
    setRestoreComment(`Restauración de la versión ${version.numero_version}`);
    setShowRestoreModal(true);
  };
  
  // Función para restaurar una versión
  const handleRestoreVersion = async () => {
    if (!canEdit || !selectedVersion) return;
    
    try {
      setRestoringVersion(selectedVersion.id);
      await documentService.restoreDocumentVersion(
        documentId, 
        selectedVersion.id, 
        restoreComment
      );
      
      // Recargar versiones después de restaurar
      const data = await documentService.getDocumentVersions(documentId);
      setVersions(data || []);
      
      // Cerrar modal
      setShowRestoreModal(false);
      setSelectedVersion(null);
      setRestoreComment('');
    } catch (error) {
      setError('No se pudo restaurar la versión del documento.');
    } finally {
      setRestoringVersion(null);
    }
  };
  
  // Función para abrir modal de comparación
  const handleOpenCompareModal = () => {
    if (versions.length < 2) return;
    
    setCompareVersions({
      version1: versions[1]?.id || null, // Segunda versión más reciente
      version2: versions[0]?.id || null  // Versión más reciente
    });
    
    setShowCompareModal(true);
  };
  
  // Función para comparar versiones
  const handleCompareVersions = async () => {
    if (!compareVersions.version1 || !compareVersions.version2) return;
    
    try {
      setComparingVersions(true);
      const result = await documentService.compareDocumentVersions(
        documentId,
        compareVersions.version1,
        compareVersions.version2
      );
      
      setCompareResult(result);
    } catch (error) {
      setError('No se pudieron comparar las versiones del documento.');
    } finally {
      setComparingVersions(false);
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
      {/* Barra de acciones */}
      <div className="mb-4 flex justify-end">
        {/* Botón de comparar versiones temporalmente deshabilitado
        {versions.length >= 2 && (
          <button
            onClick={handleOpenCompareModal}
            className="px-3 py-1 rounded flex items-center text-sm bg-blue-100 text-blue-800 hover:bg-blue-200 mr-2"
          >
            <FiGitBranch className="mr-1" /> Comparar versiones
          </button>
        )}
        */}
      </div>
      
      {/* Lista de versiones */}
      <ul className="divide-y divide-gray-200">
        {versions.map((version) => (
          <li key={version.id} className="py-4">
            <div className="flex items-center justify-between">
              <div>
                <div>
                  <div className="flex items-center">
                    <h4 className="text-lg font-medium text-gray-900">
                      Versión {version.numero_version}
                    </h4>
                    {version.es_actual && (
                      <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded-full">
                        Actual
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    <span className="font-medium">Título del archivo:</span> {version.titulo_archivo || version.titulo || documentTitle || "Sin título"}
                  </div>
                </div>
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
                {version.cambios && (
                  <div className="mt-2">
                    <div className="flex items-center text-sm text-gray-700 font-medium">
                      <FiFileText className="mr-1" /> Cambios:
                    </div>
                    <p className="text-sm text-gray-600 ml-5">{version.cambios}</p>
                  </div>
                )}
              </div>
              
              <div className="flex">
                {canEdit && !version.es_actual && (
                  <button
                    onClick={() => handleOpenRestoreModal(version)}
                    disabled={restoringVersion === version.id}
                    className={`mr-2 px-3 py-1 rounded flex items-center text-sm ${
                      restoringVersion === version.id
                        ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                        : 'bg-amber-100 text-amber-800 hover:bg-amber-200'
                    }`}
                  >
                    <FiRefreshCw className="mr-1" />
                    {restoringVersion === version.id ? 'Restaurando...' : 'Restaurar'}
                  </button>
                )}
                
                {canDownload && (
                  <button
                    onClick={() => handleDownloadVersion(version.id)}
                    disabled={downloadingVersion === version.id}
                    className={`px-3 py-1 rounded flex items-center text-sm ${
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
            </div>
          </li>
        ))}
      </ul>
      
      {/* Modal de restauración */}
      {showRestoreModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Restaurar versión {selectedVersion?.numero_version}
            </h3>
            <p className="text-gray-600 mb-4">
              Esta acción creará una nueva versión del documento basada en la versión {selectedVersion?.numero_version}.
              La versión actual seguirá disponible en el historial.
            </p>
            <div className="mb-4">
              <label htmlFor="restoreComment" className="block text-sm font-medium text-gray-700 mb-1">
                Comentario (opcional)
              </label>
              <textarea
                id="restoreComment"
                value={restoreComment}
                onChange={(e) => setRestoreComment(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowRestoreModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleRestoreVersion}
                disabled={restoringVersion !== null}
                className={`px-4 py-2 rounded-md text-white ${
                  restoringVersion !== null
                    ? 'bg-amber-400 cursor-not-allowed'
                    : 'bg-amber-600 hover:bg-amber-700'
                }`}
              >
                {restoringVersion !== null ? 'Restaurando...' : 'Restaurar versión'}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Modal de comparación */}
      {showCompareModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Comparar versiones
            </h3>
            
            {!compareResult ? (
              <>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label htmlFor="version1" className="block text-sm font-medium text-gray-700 mb-1">
                      Primera versión
                    </label>
                    <select
                      id="version1"
                      value={compareVersions.version1 || ''}
                      onChange={(e) => setCompareVersions({...compareVersions, version1: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Seleccione una versión</option>
                      {versions.map((version) => (
                        <option key={version.id} value={version.id}>
                          Versión {version.numero_version} ({formatDate(version.fecha_version)})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label htmlFor="version2" className="block text-sm font-medium text-gray-700 mb-1">
                      Segunda versión
                    </label>
                    <select
                      id="version2"
                      value={compareVersions.version2 || ''}
                      onChange={(e) => setCompareVersions({...compareVersions, version2: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Seleccione una versión</option>
                      {versions.map((version) => (
                        <option key={version.id} value={version.id}>
                          Versión {version.numero_version} ({formatDate(version.fecha_version)})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowCompareModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleCompareVersions}
                    disabled={!compareVersions.version1 || !compareVersions.version2 || comparingVersions}
                    className={`px-4 py-2 rounded-md text-white ${
                      !compareVersions.version1 || !compareVersions.version2 || comparingVersions
                        ? 'bg-blue-400 cursor-not-allowed'
                        : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                  >
                    {comparingVersions ? 'Comparando...' : 'Comparar'}
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="mb-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="border rounded-md p-4">
                      <h4 className="font-medium text-gray-900">
                        Versión {compareResult.version1.numero_version}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {formatDate(compareResult.version1.fecha)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {compareResult.version1.usuario}
                      </p>
                      {compareResult.version1.comentario && (
                        <p className="text-sm text-gray-700 mt-2">
                          {compareResult.version1.comentario}
                        </p>
                      )}
                    </div>
                    <div className="border rounded-md p-4">
                      <h4 className="font-medium text-gray-900">
                        Versión {compareResult.version2.numero_version}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {formatDate(compareResult.version2.fecha)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {compareResult.version2.usuario}
                      </p>
                      {compareResult.version2.comentario && (
                        <p className="text-sm text-gray-700 mt-2">
                          {compareResult.version2.comentario}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="mb-4">
                  <h4 className="font-medium text-gray-900 mb-2">Resumen de cambios</h4>
                  <div className="flex space-x-4">
                    <div className="flex items-center">
                      <span className="inline-block w-4 h-4 bg-green-100 rounded-full mr-1"></span>
                      <span className="text-sm text-gray-700">
                        {compareResult.added_lines} líneas añadidas
                      </span>
                    </div>
                    <div className="flex items-center">
                      <span className="inline-block w-4 h-4 bg-red-100 rounded-full mr-1"></span>
                      <span className="text-sm text-gray-700">
                        {compareResult.removed_lines} líneas eliminadas
                      </span>
                    </div>
                  </div>
                </div>
                
                {compareResult.is_binary ? (
                  <div className="bg-gray-100 p-4 rounded-md">
                    <p className="text-gray-700">
                      Los archivos son binarios y no se pueden mostrar las diferencias en texto.
                    </p>
                  </div>
                ) : (
                  <div className="bg-gray-100 p-4 rounded-md overflow-x-auto">
                    <pre className="text-sm font-mono">
                      {compareResult.diff.map((line, index) => {
                        let className = 'text-gray-800';
                        
                        if (line.startsWith('+') && !line.startsWith('+++')) {
                          className = 'text-green-700 bg-green-100';
                        } else if (line.startsWith('-') && !line.startsWith('---')) {
                          className = 'text-red-700 bg-red-100';
                        } else if (line.startsWith('@@ ')) {
                          className = 'text-blue-700 bg-blue-100';
                        }
                        
                        return (
                          <div key={index} className={className}>
                            {line}
                          </div>
                        );
                      })}
                    </pre>
                  </div>
                )}
                
                <div className="mt-4 flex justify-end">
                  <button
                    onClick={() => {
                      setCompareResult(null);
                      setShowCompareModal(false);
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cerrar
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

VersionHistory.propTypes = {
  documentId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  canDownload: PropTypes.bool,
  canEdit: PropTypes.bool,
  documentTitle: PropTypes.string
};

VersionHistory.defaultProps = {
  canDownload: false,
  canEdit: false,
  documentTitle: ''
};

export default VersionHistory;
