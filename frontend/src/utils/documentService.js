import api from './api';

// Servicio para gestión de documentos
export const documentService = {
  // Buscar documentos
  searchDocuments: async (params) => {
    try {
      const response = await api.get('/documents', { params });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Obtener un documento por ID
  getDocument: async (id) => {
    try {
      const response = await api.get(`/documents/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Descargar un documento
  downloadDocument: async (id, fileName = null) => {
    try {
      const response = await api.get(`/documents/${id}/download`, {
        responseType: 'blob'
      });
      
      // Crear URL para el blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      
      // Crear enlace temporal para la descarga
      const link = document.createElement('a');
      link.href = url;
      
      // Usar nombre proporcionado o extraer del header Content-Disposition
      const contentDisposition = response.headers['content-disposition'];
      const defaultFileName = `documento_${id}.pdf`;
      
      if (fileName) {
        link.setAttribute('download', fileName);
      } else if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
        link.setAttribute('download', fileNameMatch ? fileNameMatch[1] : defaultFileName);
      } else {
        link.setAttribute('download', defaultFileName);
      }
      
      // Añadir al DOM, hacer clic y eliminar
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Liberar la URL
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Descargar una versión específica de un documento
  downloadDocumentVersion: async (documentId, versionId, fileName = null) => {
    try {
      const response = await api.get(`/documents/${documentId}/versions/${versionId}/download`, {
        responseType: 'blob'
      });
      
      // Crear URL para el blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      
      // Crear enlace temporal para la descarga
      const link = document.createElement('a');
      link.href = url;
      
      // Usar nombre proporcionado o extraer del header Content-Disposition
      const contentDisposition = response.headers['content-disposition'];
      const defaultFileName = `documento_${documentId}_v${versionId}.pdf`;
      
      if (fileName) {
        link.setAttribute('download', fileName);
      } else if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
        link.setAttribute('download', fileNameMatch ? fileNameMatch[1] : defaultFileName);
      } else {
        link.setAttribute('download', defaultFileName);
      }
      
      // Añadir al DOM, hacer clic y eliminar
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Liberar la URL
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Obtener categorías de documentos
  getCategories: async () => {
    try {
      const response = await api.get('/documents/categories');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Obtener tipos de documentos
  getDocumentTypes: async () => {
    try {
      const response = await api.get('/documents/types');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Obtener historial de acceso a un documento
  getDocumentHistory: async (id) => {
    try {
      const response = await api.get(`/documents/${id}/history`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Obtener versiones de un documento
  getDocumentVersions: async (id) => {
    try {
      const response = await api.get(`/documents/${id}/versions`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
};

// Función para manejar errores de API
function handleApiError(error) {
  let errorMessage = 'Ha ocurrido un error. Por favor, inténtelo de nuevo.';
  
  if (error.response) {
    // La solicitud fue realizada y el servidor respondió con un código de estado
    // que cae fuera del rango 2xx
    const data = error.response.data;
    errorMessage = data.detail || data.message || errorMessage;
  } else if (error.request) {
    // La solicitud fue realizada pero no se recibió respuesta
    errorMessage = 'No se pudo conectar con el servidor. Verifique su conexión.';
  }
  
  return new Error(errorMessage);
}

export default documentService;