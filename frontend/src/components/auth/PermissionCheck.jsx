import { useAuth } from '../../context/AuthContext';
import PropTypes from 'prop-types';

/**
 * Componente para verificar permisos del usuario
 * 
 * @param {Object} props - Propiedades del componente
 * @param {string|Array} props.permission - Permiso o array de permisos requeridos
 * @param {boolean} props.requireAll - Si es true, se requieren todos los permisos; si es false, basta con uno
 * @param {React.ReactNode} props.children - Contenido a mostrar si el usuario tiene los permisos
 * @param {React.ReactNode} props.fallback - Contenido a mostrar si el usuario no tiene los permisos
 * @returns {React.ReactNode} Contenido condicionado a los permisos
 */
const PermissionCheck = ({ permission, requireAll = false, children, fallback = null }) => {
  const { currentUser, isAuthenticated } = useAuth();
  
  // Si no está autenticado, no tiene permisos
  if (!isAuthenticated || !currentUser) {
    return fallback;
  }
  
  // Administradores tienen todos los permisos
  if (currentUser.role_id === 1) {
    return children;
  }
  
  // Verificar permisos
  const userPermissions = currentUser.permissions || [];
  
  if (Array.isArray(permission)) {
    if (requireAll) {
      // Debe tener todos los permisos
      const hasAllPermissions = permission.every(perm => 
        userPermissions.includes(perm)
      );
      
      return hasAllPermissions ? children : fallback;
    } else {
      // Basta con tener uno de los permisos
      const hasAnyPermission = permission.some(perm => 
        userPermissions.includes(perm)
      );
      
      return hasAnyPermission ? children : fallback;
    }
  } else {
    // Un solo permiso
    const hasPermission = userPermissions.includes(permission);
    return hasPermission ? children : fallback;
  }
};

PermissionCheck.propTypes = {
  permission: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string)
  ]).isRequired,
  requireAll: PropTypes.bool,
  children: PropTypes.node.isRequired,
  fallback: PropTypes.node
};

export default PermissionCheck;
