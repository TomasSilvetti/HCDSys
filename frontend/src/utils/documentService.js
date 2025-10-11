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
  },
  
  // Obtener una versión específica de un documento
  getDocumentVersion: async (documentId, versionId) => {
    try {
      const response = await api.get(`/documents/${documentId}/versions/${versionId}`);
      return response.data;
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
  
  // Restaurar una versión específica de un documento
  restoreDocumentVersion: async (documentId, versionId, comentario = null) => {
    try {
      const formData = new FormData();
      if (comentario) {
        formData.append('comentario', comentario);
      }
      
      const response = await api.post(
        `/documents/${documentId}/versions/${versionId}/restore`, 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Comparar dos versiones de un documento
  compareDocumentVersions: async (documentId, versionId1, versionId2) => {
    try {
      const response = await api.post(`/documents/${documentId}/versions/compare`, {
        version_id1: versionId1,
        version_id2: versionId2
      });
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Cargar un nuevo documento
  uploadDocument: async (documentData, onProgressUpdate = null) => {
    try {
      const formData = new FormData();
      
      // Añadir campos del documento
      Object.keys(documentData).forEach(key => {
        if (key === 'archivo') {
          formData.append('archivo', documentData.archivo);
        } else if (documentData[key] !== null && documentData[key] !== undefined) {
          formData.append(key, documentData[key]);
        }
      });
      
      // Configuración para seguimiento de progreso
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      };
      
      // Añadir handler de progreso si se proporciona
      if (onProgressUpdate) {
        config.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgressUpdate(percentCompleted);
        };
      }
      
      const response = await api.post('/documents', formData, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Actualizar un documento existente
  updateDocument: async (id, documentData) => {
    try {
      // Filtrar campos nulos o indefinidos
      const cleanedData = {};
      Object.keys(documentData).forEach(key => {
        if (documentData[key] !== null && documentData[key] !== undefined) {
          cleanedData[key] = documentData[key];
        }
      });
      
      // Enviar como JSON normal - enviar directamente el objeto de datos
      const response = await api.put(`/documents/${id}`, cleanedData);
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Crear una nueva versión de un documento existente
  createDocumentVersion: async (id, documentData, onProgressUpdate = null) => {
    try {
      const formData = new FormData();
      
      // Añadir campos del documento de manera explícita
      // Esto asegura que los campos se añadan correctamente al FormData
      if (documentData.titulo !== null && documentData.titulo !== undefined) {
        formData.append('titulo', documentData.titulo);
      }
      
      if (documentData.numero_expediente !== null && documentData.numero_expediente !== undefined) {
        formData.append('numero_expediente', documentData.numero_expediente);
      }
      
      if (documentData.descripcion !== null && documentData.descripcion !== undefined) {
        formData.append('descripcion', documentData.descripcion);
      }
      
      if (documentData.categoria_id !== null && documentData.categoria_id !== undefined) {
        formData.append('categoria_id', documentData.categoria_id);
      }
      
      if (documentData.tipo_documento_id !== null && documentData.tipo_documento_id !== undefined) {
        formData.append('tipo_documento_id', documentData.tipo_documento_id);
      }
      
      // Añadir el archivo (obligatorio)
      if (documentData.archivo) {
        formData.append('archivo', documentData.archivo);
      } else {
        throw new Error('El archivo es obligatorio para crear una nueva versión');
      }
      
      // Configuración para seguimiento de progreso
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      };
      
      // Añadir handler de progreso si se proporciona
      if (onProgressUpdate) {
        config.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgressUpdate(percentCompleted);
        };
      }
      
      // Llamar al endpoint para crear una nueva versión
      const response = await api.post(`/documents/${id}/versions`, formData, config);
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