import { render, screen } from '@testing-library/react';
import PermissionGate from '../../../components/auth/PermissionGate';
import { AuthContext } from '../../../context/AuthContext';

describe('PermissionGate Component', () => {
  // Mock para el contexto de autenticación
  const createMockAuthContext = (isAuthenticated = true, permissions = []) => ({
    isAuthenticated,
    user: isAuthenticated ? {
      id: '1',
      email: 'test@example.com',
      role: {
        id: '1',
        name: 'usuario',
        permissions
      }
    } : null
  });
  
  test('renders children when user has required permission', () => {
    const authContext = createMockAuthContext(true, ['read:document']);
    
    render(
      <AuthContext.Provider value={authContext}>
        <PermissionGate permission="read:document">
          <div>Contenido protegido</div>
        </PermissionGate>
      </AuthContext.Provider>
    );
    
    expect(screen.getByText('Contenido protegido')).toBeInTheDocument();
  });
  
  test('does not render children when user lacks required permission', () => {
    const authContext = createMockAuthContext(true, ['read:document']);
    
    render(
      <AuthContext.Provider value={authContext}>
        <PermissionGate permission="create:document">
          <div>Contenido protegido</div>
        </PermissionGate>
      </AuthContext.Provider>
    );
    
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument();
  });
  
  test('does not render children when user is not authenticated', () => {
    const authContext = createMockAuthContext(false);
    
    render(
      <AuthContext.Provider value={authContext}>
        <PermissionGate permission="read:document">
          <div>Contenido protegido</div>
        </PermissionGate>
      </AuthContext.Provider>
    );
    
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument();
  });
  
  test('renders fallback when provided and user lacks permission', () => {
    const authContext = createMockAuthContext(true, ['read:document']);
    
    render(
      <AuthContext.Provider value={authContext}>
        <PermissionGate 
          permission="create:document" 
          fallback={<div>Acceso denegado</div>}
        >
          <div>Contenido protegido</div>
        </PermissionGate>
      </AuthContext.Provider>
    );
    
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument();
    expect(screen.getByText('Acceso denegado')).toBeInTheDocument();
  });
  
  test('renders children when user has any of the required permissions', () => {
    const authContext = createMockAuthContext(true, ['read:document', 'update:document']);
    
    render(
      <AuthContext.Provider value={authContext}>
        <PermissionGate 
          permissions={['create:document', 'update:document']} 
          requireAll={false}
        >
          <div>Contenido protegido</div>
        </PermissionGate>
      </AuthContext.Provider>
    );
    
    expect(screen.getByText('Contenido protegido')).toBeInTheDocument();
  });
  
  test('does not render children when user lacks all required permissions', () => {
    const authContext = createMockAuthContext(true, ['read:document']);
    
    render(
      <AuthContext.Provider value={authContext}>
        <PermissionGate 
          permissions={['create:document', 'update:document']} 
          requireAll={false}
        >
          <div>Contenido protegido</div>
        </PermissionGate>
      </AuthContext.Provider>
    );
    
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument();
  });
  
  test('renders children when user has all required permissions', () => {
    const authContext = createMockAuthContext(true, ['create:document', 'update:document', 'delete:document']);
    
    render(
      <AuthContext.Provider value={authContext}>
        <PermissionGate 
          permissions={['create:document', 'update:document']} 
          requireAll={true}
        >
          <div>Contenido protegido</div>
        </PermissionGate>
      </AuthContext.Provider>
    );
    
    expect(screen.getByText('Contenido protegido')).toBeInTheDocument();
  });
  
  test('does not render children when user lacks any required permission', () => {
    const authContext = createMockAuthContext(true, ['create:document', 'read:document']);
    
    render(
      <AuthContext.Provider value={authContext}>
        <PermissionGate 
          permissions={['create:document', 'update:document']} 
          requireAll={true}
        >
          <div>Contenido protegido</div>
        </PermissionGate>
      </AuthContext.Provider>
    );
    
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument();
  });
});
