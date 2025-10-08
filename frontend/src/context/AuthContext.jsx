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
      if (authService.isAuthenticated()) {
        const user = authService.getCurrentUser();
        setCurrentUser(user);
      }
      setLoading(false);
    };
    
    initAuth();
  }, []);

  // Función para iniciar sesión
  const login = async (credentials) => {
    try {
      const data = await authService.login(credentials);
      const user = authService.getCurrentUser();
      setCurrentUser(user);
      return { success: true, user };
    } catch (error) {
      console.error('Error de inicio de sesión:', error);
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
  const value = {
    currentUser,
    login,
    logout,
    register,
    isAuthenticated: !!currentUser,
    userRole: currentUser?.role_id || 'guest',
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
