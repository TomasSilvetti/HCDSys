import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

/**
 * Componente para proteger rutas que requieren permisos de administrador
 */
const AdminRoute = () => {
  const { isAuthenticated, userRole, loading } = useAuth();

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
    return <Navigate to="/login" replace />;
  }

  // Si no es administrador, redirigir a la página principal
  if (userRole !== 1) { // Asumiendo que el rol 1 es Administrador
    return (
      <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Acceso Denegado</h1>
        <p className="mb-4">No tienes permisos de administrador para acceder a esta página.</p>
        <button
          onClick={() => window.history.back()}
          className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
        >
          Volver
        </button>
      </div>
    );
  }

  // Si está autenticado y es administrador, mostrar el contenido
  return <Outlet />;
};

export default AdminRoute;
