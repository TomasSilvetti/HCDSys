import React from 'react';
import { AuthContext } from '../../context/AuthContext';

// Mock para el contexto de autenticación
export const MockAuthProvider = ({ children, isAuthenticated = false, user = null }) => {
  const mockLogin = jest.fn((userData) => {
    console.log('Mock login called with:', userData);
    return Promise.resolve();
  });

  const mockLogout = jest.fn(() => {
    console.log('Mock logout called');
    return Promise.resolve();
  });

  const mockRegister = jest.fn((userData) => {
    console.log('Mock register called with:', userData);
    return Promise.resolve();
  });

  const mockUpdateUser = jest.fn((userData) => {
    console.log('Mock updateUser called with:', userData);
    return Promise.resolve();
  });

  const defaultUser = user || {
    id: '1',
    email: 'test@example.com',
    fullName: 'Test User',
    role: {
      id: '1',
      name: 'usuario',
      permissions: ['read:document']
    }
  };

  const authContextValue = {
    isAuthenticated,
    user: isAuthenticated ? defaultUser : null,
    login: mockLogin,
    logout: mockLogout,
    register: mockRegister,
    updateUser: mockUpdateUser,
    loading: false,
    error: null
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Función de ayuda para crear un wrapper de prueba con autenticación
export const createAuthWrapper = (options = {}) => {
  const { isAuthenticated = false, user = null } = options;
  
  return ({ children }) => (
    <MockAuthProvider isAuthenticated={isAuthenticated} user={user}>
      {children}
    </MockAuthProvider>
  );
};
