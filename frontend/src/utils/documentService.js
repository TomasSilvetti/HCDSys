import api from './api';

// Servicio para gestión de documentos
export const documentService = {
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
  
  // Cargar un nuevo documento
  uploadDocument: async (documentData, onProgress) => {
    try {
      // Crear FormData para enviar archivo
      const formData = new FormData();
      formData.append('titulo', documentData.titulo);
      formData.append('numero_expediente', documentData.numero_expediente);
      
      if (documentData.descripcion) {
        formData.append('descripcion', documentData.descripcion);
      }
      
      if (documentData.categoria_id) {
        formData.append('categoria_id', documentData.categoria_id);
      }
      
      formData.append('tipo_documento_id', documentData.tipo_documento_id);
      formData.append('archivo', documentData.archivo);
      
      // Configurar opciones para seguimiento de progreso
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: progressEvent => {
          if (onProgress) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(percentCompleted);
          }
        }
      };
      
      const response = await api.post('/documents', formData, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Obtener un documento específico
  getDocument: async (id) => {
    try {
      const response = await api.get(`/documents/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Buscar documentos
  searchDocuments: async (params) => {
    try {
      const response = await api.get('/documents', { params });
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
