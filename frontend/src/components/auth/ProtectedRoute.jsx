import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import usePermission from '../../hooks/usePermission';

/**
 * Componente para proteger rutas que requieren autenticación y/o permisos específicos
 * 
 * @param {Object} props - Propiedades del componente
 * @param {JSX.Element} props.children - Componente hijo a renderizar si el usuario está autenticado
 * @param {Array<string>} [props.allowedRoles] - Roles permitidos para acceder a la ruta
 * @param {string|Array<string>} [props.requiredPermissions] - Permisos requeridos para acceder a la ruta
 * @param {boolean} [props.requireAllPermissions] - Si es true, se requieren todos los permisos; si es false, basta con uno
 * @returns {JSX.Element} El componente hijo si el usuario está autenticado y tiene permisos, o redirección
 */
const ProtectedRoute = ({ 
  children, 
  allowedRoles = [], 
  requiredPermissions = null,
  requireAllPermissions = false
}) => {
  const { isAuthenticated, userRole, loading } = useAuth();
  const location = useLocation();
  const hasPermission = requiredPermissions 
    ? usePermission(requiredPermissions, requireAllPermissions) 
    : true;

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

  // Si hay roles permitidos y el usuario no tiene uno de ellos, redirigir a acceso denegado
  if (allowedRoles.length > 0) {
    const userRoleStr = String(userRole);
    console.log('Verificando acceso: Usuario tiene rol', userRoleStr, 'necesita uno de estos roles:', allowedRoles);
    
    if (!allowedRoles.includes(userRoleStr)) {
      console.log('Acceso denegado: El usuario tiene rol', userRoleStr, 'pero se requiere uno de estos roles:', allowedRoles);
      return <Navigate to="/acceso-denegado" replace />;
    }
  }

  // Si se requieren permisos específicos y el usuario no los tiene, redirigir a acceso denegado
  if (requiredPermissions && !hasPermission) {
    return <Navigate to="/acceso-denegado" replace />;
  }

  // Si está autenticado y tiene los roles/permisos permitidos, mostrar el contenido
  return children || <Outlet />;
};

export default ProtectedRoute;
