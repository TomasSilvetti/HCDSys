import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthContext } from '../../../context/AuthContext';
import ProtectedRoute from '../../../components/auth/ProtectedRoute';

const MockChildComponent = () => <div>Protected Content</div>;

describe('ProtectedRoute Component', () => {
  test('redirects to login when user is not authenticated', () => {
    render(
      <AuthContext.Provider value={{ isAuthenticated: false }}>
        <MemoryRouter initialEntries={['/protected']}>
          <Routes>
            <Route path="/login" element={<div>Login Page</div>} />
            <Route
              path="/protected"
              element={
                <ProtectedRoute>
                  <MockChildComponent />
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );
    
    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });
  
  test('renders children when user is authenticated', () => {
    render(
      <AuthContext.Provider value={{ isAuthenticated: true }}>
        <MemoryRouter initialEntries={['/protected']}>
          <Routes>
            <Route path="/login" element={<div>Login Page</div>} />
            <Route
              path="/protected"
              element={
                <ProtectedRoute>
                  <MockChildComponent />
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );
    
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });
});
