import { toast } from 'react-toastify';

/**
 * Interceptor para manejar errores de autorización en las respuestas HTTP
 * 
 * @param {Object} error - Error de la respuesta HTTP
 * @param {Function} logout - Función para cerrar sesión
 * @param {Function} navigate - Función para navegar a otra ruta
 * @returns {Promise} Promise rechazada con el error
 */
export const handleAuthError = (error, logout, navigate) => {
  // Si no hay respuesta, devolver el error
  if (!error.response) {
    return Promise.reject(error);
  }

  const { status } = error.response;

  // Manejar error 401 (No autorizado)
  if (status === 401) {
    // Si el token expiró o es inválido, cerrar sesión
    logout();
    toast.error('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
    navigate('/login');
  }

  // Manejar error 403 (Prohibido)
  if (status === 403) {
    toast.error('No tienes permisos para realizar esta acción.');
    navigate('/acceso-denegado');
  }

  return Promise.reject(error);
};

/**
 * Configurar interceptores para una instancia de axios
 * 
 * @param {Object} axiosInstance - Instancia de axios
 * @param {Function} logout - Función para cerrar sesión
 * @param {Function} navigate - Función para navegar a otra ruta
 */
export const setupAuthInterceptors = (axiosInstance, logout, navigate) => {
  // Interceptor de respuesta
  axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => handleAuthError(error, logout, navigate)
  );
};
