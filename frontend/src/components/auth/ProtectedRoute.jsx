import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

/**
 * Componente para proteger rutas que requieren autenticación
 * 
 * @param {Object} props - Propiedades del componente
 * @param {JSX.Element} props.children - Componente hijo a renderizar si el usuario está autenticado
 * @param {Array<string>} [props.allowedRoles] - Roles permitidos para acceder a la ruta
 * @returns {JSX.Element} El componente hijo si el usuario está autenticado, o redirección a login
 */
const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, userRole, loading } = useAuth();
  const location = useLocation();

  // Si aún está cargando la autenticación, mostrar un indicador de carga
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Si no está autenticado, redirigir a login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Si hay roles permitidos y el usuario no tiene uno de ellos, mostrar acceso denegado
  if (allowedRoles.length > 0 && !allowedRoles.includes(userRole)) {
    return (
      <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Acceso Denegado</h1>
        <p className="mb-4">No tienes permisos para acceder a esta página.</p>
        <button
          onClick={() => window.history.back()}
          className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
        >
          Volver
        </button>
      </div>
    );
  }

  // Si está autenticado y tiene los roles permitidos (o no hay restricción de roles), mostrar el contenido
  return children || <Outlet />;
};

export default ProtectedRoute;
