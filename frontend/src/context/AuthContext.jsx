import { createContext, useState, useContext, useEffect } from 'react';

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

  // Simular carga inicial del usuario desde localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setCurrentUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  // Función para iniciar sesión
  const login = (userData) => {
    // En una aplicación real, aquí se haría la llamada a la API
    // y se guardaría el token JWT
    setCurrentUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  // Función para cerrar sesión
  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('user');
  };

  // Función para registrar un nuevo usuario
  const register = async (userData) => {
    // En una aplicación real, aquí se haría la llamada a la API
    // Por ahora, simulamos un registro exitoso
    return { success: true, message: 'Usuario registrado correctamente' };
  };

  // Valores que se proporcionarán a través del contexto
  const value = {
    currentUser,
    login,
    logout,
    register,
    isAuthenticated: !!currentUser,
    userRole: currentUser?.role || 'guest',
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
