import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthContext } from '../../../context/AuthContext';
import LoginPage from '../../../pages/auth/LoginPage';

// Mock de axios
jest.mock('axios', () => ({
  post: jest.fn(() => Promise.resolve({ data: { token: 'fake-token', user: { id: '1', email: 'test@example.com' } } }))
}));

// Mock de react-toastify
jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn()
  }
}));

// Mock del contexto de autenticación
const mockLogin = jest.fn();
const mockAuthContext = {
  login: mockLogin,
  isAuthenticated: false
};

describe('LoginPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form correctly', () => {
    render(
      <AuthContext.Provider value={mockAuthContext}>
        <BrowserRouter>
          <LoginPage />
        </BrowserRouter>
      </AuthContext.Provider>
    );
    
    expect(screen.getByLabelText(/correo electrónico/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  test('submits form with user credentials', async () => {
    render(
      <AuthContext.Provider value={mockAuthContext}>
        <BrowserRouter>
          <LoginPage />
        </BrowserRouter>
      </AuthContext.Provider>
    );
    
    // Completar el formulario
    fireEvent.change(screen.getByLabelText(/correo electrónico/i), {
      target: { value: 'test@example.com' }
    });
    
    fireEvent.change(screen.getByLabelText(/contraseña/i), {
      target: { value: 'password123' }
    });
    
    // Enviar el formulario
    fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));
    
    // Verificar que la función login fue llamada
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith(expect.objectContaining({
        token: 'fake-token',
        user: expect.objectContaining({
          email: 'test@example.com'
        })
      }));
    });
  });

  test('displays validation errors for empty fields', async () => {
    render(
      <AuthContext.Provider value={mockAuthContext}>
        <BrowserRouter>
          <LoginPage />
        </BrowserRouter>
      </AuthContext.Provider>
    );
    
    // Enviar formulario sin completar campos
    fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));
    
    // Verificar mensajes de error
    await waitFor(() => {
      expect(screen.getByText(/el correo electrónico es requerido/i)).toBeInTheDocument();
      expect(screen.getByText(/la contraseña es requerida/i)).toBeInTheDocument();
    });
  });
});
