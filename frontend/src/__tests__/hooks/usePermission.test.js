import { renderHook } from '@testing-library/react';
import { AuthContext } from '../../context/AuthContext';
import usePermission from '../../hooks/usePermission';

// Mock del contexto de autenticación
const mockAuthContext = {
  user: {
    id: '1',
    email: 'test@example.com',
    role: {
      name: 'admin',
      permissions: ['create:document', 'read:document', 'update:document', 'delete:document']
    }
  },
  isAuthenticated: true
};

// Wrapper personalizado para proporcionar el contexto
const wrapper = ({ children }) => (
  <AuthContext.Provider value={mockAuthContext}>
    {children}
  </AuthContext.Provider>
);

describe('usePermission Hook', () => {
  test('returns true when user has the required permission', () => {
    const { result } = renderHook(() => usePermission('create:document'), { wrapper });
    expect(result.current).toBe(true);
  });

  test('returns false when user does not have the required permission', () => {
    const { result } = renderHook(() => usePermission('manage:users'), { wrapper });
    expect(result.current).toBe(false);
  });

  test('returns false when user is not authenticated', () => {
    const unauthenticatedWrapper = ({ children }) => (
      <AuthContext.Provider value={{ ...mockAuthContext, isAuthenticated: false }}>
        {children}
      </AuthContext.Provider>
    );
    
    const { result } = renderHook(() => usePermission('create:document'), { 
      wrapper: unauthenticatedWrapper 
    });
    
    expect(result.current).toBe(false);
  });

  test('returns false when user has no role', () => {
    const noRoleWrapper = ({ children }) => (
      <AuthContext.Provider value={{ 
        ...mockAuthContext, 
        user: { ...mockAuthContext.user, role: null } 
      }}>
        {children}
      </AuthContext.Provider>
    );
    
    const { result } = renderHook(() => usePermission('create:document'), { 
      wrapper: noRoleWrapper 
    });
    
    expect(result.current).toBe(false);
  });
});
