import { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../utils/api';
import api from '../utils/api';
import { setupAuthInterceptors } from '../utils/authInterceptor';

// Crear el contexto de autenticación
const AuthContext = createContext();

// Hook personalizado para usar el contexto de autenticación
export const useAuth = () => {
  return useContext(AuthContext);
};

// Proveedor del contexto de autenticación
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Configurar interceptores para manejar errores de autenticación
  useEffect(() => {
    setupAuthInterceptors(api, logout, navigate);
  }, [navigate]);

  // Cargar usuario desde localStorage/token al iniciar
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const user = authService.getCurrentUser();
          console.log('Usuario cargado del localStorage:', user);
          setCurrentUser(user);
        } else {
          console.log('No hay sesión activa');
          // Limpiar cualquier dato de sesión anterior por si acaso
          authService.logout();
        }
      } catch (error) {
        console.error('Error al inicializar autenticación:', error);
        // Si hay un error, limpiar la sesión
        authService.logout();
      } finally {
        setLoading(false);
      }
    };
    
    initAuth();
  }, []);

  // Función para iniciar sesión
  const login = async (credentials) => {
    try {
      const data = await authService.login(credentials);
      // Esperar un momento para asegurar que localStorage se ha actualizado
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const user = authService.getCurrentUser();
      
      if (!user) {
        throw new Error('No se pudo obtener la información del usuario');
      }
      
      console.log('Usuario autenticado en contexto:', user);
      setCurrentUser(user);
      return { success: true, user };
    } catch (error) {
      console.error('Error de inicio de sesión:', error);
      // Limpiar cualquier dato de sesión parcial
      authService.logout();
      setCurrentUser(null);
      return { success: false, error: error.message };
    }
  };

  // Función para cerrar sesión
  const logout = () => {
    authService.logout();
    setCurrentUser(null);
  };

  // Función para registrar un nuevo usuario
  const register = async (userData) => {
    try {
      const response = await authService.register(userData);
      return { success: true, message: 'Usuario registrado correctamente', data: response };
    } catch (error) {
      console.error('Error de registro:', error);
      return { success: false, error: error.message };
    }
  };

  // Valores que se proporcionarán a través del contexto
  const userRole = currentUser?.role_id ? String(currentUser.role_id) : 'guest';
  
  console.log('AuthContext - Proporcionando contexto:', { 
    isAuthenticated: !!currentUser,
    userRole,
    currentUser
  });
  
  const value = {
    currentUser,
    login,
    logout,
    register,
    isAuthenticated: !!currentUser,
    userRole,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
