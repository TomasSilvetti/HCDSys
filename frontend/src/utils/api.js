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
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
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
      const formData = new URLSearchParams();
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
        // Asegurar que el usuario tenga la información necesaria
        if (!user.sub) {
          throw new Error('Token inválido: falta información del usuario');
        }
        // Guardar información del usuario
        localStorage.setItem('user', JSON.stringify({
          email: user.sub,
          role_id: user.role_id,
          exp: user.exp
        }));
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
      return false;
    }
  },

  // Obtener usuario actual
  getCurrentUser: () => {
    try {
      const userStr = localStorage.getItem('user');
      const token = localStorage.getItem('token');
      
      if (!userStr || !token) {
        return null;
      }
      
      // Verificar si el token ha expirado
      const decoded = parseJwt(token);
      const currentTime = Date.now() / 1000;
      
      if (decoded.exp < currentTime) {
        // Token expirado, limpiar localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        return null;
      }
      
      // Log para depuración
      console.log('Token decodificado:', decoded);
      
      const user = JSON.parse(userStr);
      
      // Log para depuración
      console.log('Usuario del localStorage:', user);
      
      // Asegurarse de que el usuario tenga un role_id
      // Primero intentar obtener el role_id del token decodificado
      if (decoded.role_id !== undefined) {
        user.role_id = decoded.role_id;
        localStorage.setItem('user', JSON.stringify(user));
      }
      
      // Si aún no hay role_id, verificar si hay un campo 'role' en el token
      if (user.role_id === undefined && decoded.role) {
        if (typeof decoded.role === 'object' && decoded.role.id) {
          user.role_id = decoded.role.id;
        } else if (typeof decoded.role === 'string' || typeof decoded.role === 'number') {
          user.role_id = decoded.role;
        }
        localStorage.setItem('user', JSON.stringify(user));
      }
      
      // Asegurar que el role_id sea un valor válido (no undefined)
      if (user.role_id === undefined) {
        console.error('No se pudo determinar el role_id del usuario');
        // Si es administrador (verificar por email u otro campo)
        if (user.email === 'admin@example.com' || decoded.sub === 'admin@example.com') {
          console.log('Usuario detectado como administrador por email');
          user.role_id = 1; // Asignar rol de administrador
          localStorage.setItem('user', JSON.stringify(user));
        }
      }
      
      return user;
    } catch (error) {
      console.error('Error al obtener usuario actual:', error);
      // Limpiar localStorage en caso de error
      localStorage.removeItem('token');
      localStorage.removeItem('user');
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
