import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

/**
 * Componente para mostrar notificaciones de errores de autenticación/autorización
 * Se debe incluir en el componente principal de la aplicación
 */
const AuthErrorNotification = () => {
  const navigate = useNavigate();

  // Configurar escucha de eventos personalizados para errores de autenticación
  useEffect(() => {
    const handleAuthError = (event) => {
      const { type, message } = event.detail;
      
      switch (type) {
        case 'unauthorized':
          toast.error(message || 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
          navigate('/login');
          break;
        case 'forbidden':
          toast.error(message || 'No tienes permisos para realizar esta acción.');
          navigate('/acceso-denegado');
          break;
        default:
          toast.error(message || 'Ha ocurrido un error de autenticación.');
      }
    };

    // Registrar el evento personalizado
    window.addEventListener('auth-error', handleAuthError);

    // Limpiar el evento al desmontar el componente
    return () => {
      window.removeEventListener('auth-error', handleAuthError);
    };
  }, [navigate]);

  return <ToastContainer position="top-right" autoClose={5000} />;
};

export default AuthErrorNotification;
