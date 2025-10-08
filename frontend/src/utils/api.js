import axios from 'axios';
import { setupAuthInterceptors } from './authInterceptor';

// Crear instancia de axios con configuración base
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para incluir el token en las solicitudes
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Servicios de autenticación
export const authService = {
  // Registro de usuario
  register: async (userData) => {
    try {
      const { nombre, apellido, email, password, dni } = userData;
      const response = await api.post('/auth/register', {
        nombre,
        apellido,
        email,
        password,
        dni
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Inicio de sesión
  login: async (credentials) => {
    try {
      // FastAPI OAuth2 espera un formato específico para login
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);
      
      const response = await axios.post(`${api.defaults.baseURL}/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        
        // Decodificar el token para obtener información del usuario
        const user = parseJwt(response.data.access_token);
        localStorage.setItem('user', JSON.stringify(user));
      }
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Cerrar sesión
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  // Verificar si el usuario está autenticado
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    try {
      const decoded = parseJwt(token);
      const currentTime = Date.now() / 1000;
      
      // Verificar si el token ha expirado
      if (decoded.exp < currentTime) {
        authService.logout();
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('Error al verificar autenticación:', error);
      return false;
    }
  },

  // Obtener usuario actual
  getCurrentUser: () => {
    try {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        return JSON.parse(userStr);
      }
      return null;
    } catch (error) {
      console.error('Error al obtener usuario actual:', error);
      return null;
    }
  },
};

// Función para parsear token JWT
function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error al parsear JWT:', error);
    return {};
  }
}

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

export default api;
