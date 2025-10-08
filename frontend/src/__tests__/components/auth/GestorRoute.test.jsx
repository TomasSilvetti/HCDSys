import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthContext } from '../../../context/AuthContext';
import GestorRoute from '../../../components/auth/GestorRoute';

describe('GestorRoute Component', () => {
  // Mock para el contexto de autenticación
  const createMockAuthContext = (isAuthenticated = true, role = 'usuario') => ({
    isAuthenticated,
    user: isAuthenticated ? {
      id: '1',
      email: 'test@example.com',
      role: {
        id: role === 'admin' ? '1' : (role === 'gestor' ? '2' : '3'),
        name: role
      }
    } : null
  });
  
  const MockChildComponent = () => <div>Contenido de gestor</div>;
  
  test('renders children when user is gestor', () => {
    const authContext = createMockAuthContext(true, 'gestor');
    
    render(
      <AuthContext.Provider value={authContext}>
        <MemoryRouter initialEntries={['/gestor']}>
          <Routes>
            <Route path="/access-denied" element={<div>Acceso denegado</div>} />
            <Route
              path="/gestor"
              element={
                <GestorRoute>
                  <MockChildComponent />
                </GestorRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );
    
    expect(screen.getByText('Contenido de gestor')).toBeInTheDocument();
    expect(screen.queryByText('Acceso denegado')).not.toBeInTheDocument();
  });
  
  test('renders children when user is admin', () => {
    const authContext = createMockAuthContext(true, 'admin');
    
    render(
      <AuthContext.Provider value={authContext}>
        <MemoryRouter initialEntries={['/gestor']}>
          <Routes>
            <Route path="/access-denied" element={<div>Acceso denegado</div>} />
            <Route
              path="/gestor"
              element={
                <GestorRoute>
                  <MockChildComponent />
                </GestorRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );
    
    expect(screen.getByText('Contenido de gestor')).toBeInTheDocument();
    expect(screen.queryByText('Acceso denegado')).not.toBeInTheDocument();
  });
  
  test('redirects to access denied page when user is regular usuario', () => {
    const authContext = createMockAuthContext(true, 'usuario');
    
    render(
      <AuthContext.Provider value={authContext}>
        <MemoryRouter initialEntries={['/gestor']}>
          <Routes>
            <Route path="/access-denied" element={<div>Acceso denegado</div>} />
            <Route
              path="/gestor"
              element={
                <GestorRoute>
                  <MockChildComponent />
                </GestorRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );
    
    expect(screen.queryByText('Contenido de gestor')).not.toBeInTheDocument();
    expect(screen.getByText('Acceso denegado')).toBeInTheDocument();
  });
  
  test('redirects to access denied page when user is not authenticated', () => {
    const authContext = createMockAuthContext(false);
    
    render(
      <AuthContext.Provider value={authContext}>
        <MemoryRouter initialEntries={['/gestor']}>
          <Routes>
            <Route path="/access-denied" element={<div>Acceso denegado</div>} />
            <Route
              path="/gestor"
              element={
                <GestorRoute>
                  <MockChildComponent />
                </GestorRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );
    
    expect(screen.queryByText('Contenido de gestor')).not.toBeInTheDocument();
    expect(screen.getByText('Acceso denegado')).toBeInTheDocument();
  });
  
  test('redirects to custom path when specified', () => {
    const authContext = createMockAuthContext(true, 'usuario');
    
    render(
      <AuthContext.Provider value={authContext}>
        <MemoryRouter initialEntries={['/gestor']}>
          <Routes>
            <Route path="/custom-denied" element={<div>Acceso personalizado denegado</div>} />
            <Route
              path="/gestor"
              element={
                <GestorRoute redirectTo="/custom-denied">
                  <MockChildComponent />
                </GestorRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );
    
    expect(screen.queryByText('Contenido de gestor')).not.toBeInTheDocument();
    expect(screen.getByText('Acceso personalizado denegado')).toBeInTheDocument();
  });
});
