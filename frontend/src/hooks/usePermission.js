import { useAuth } from '../context/AuthContext';

/**
 * Hook personalizado para verificar permisos del usuario
 * 
 * @param {string|Array} permission - Permiso o array de permisos a verificar
 * @param {boolean} requireAll - Si es true, se requieren todos los permisos; si es false, basta con uno
 * @returns {boolean} True si el usuario tiene los permisos requeridos, false en caso contrario
 */
const usePermission = (permission, requireAll = false) => {
  const { currentUser, isAuthenticated } = useAuth();
  
  // Si no está autenticado, no tiene permisos
  if (!isAuthenticated || !currentUser) {
    return false;
  }
  
  // Administradores tienen todos los permisos
  if (currentUser.role_id === 1) {
    return true;
  }
  
  // Verificar permisos
  const userPermissions = currentUser.permissions || [];
  
  if (Array.isArray(permission)) {
    if (requireAll) {
      // Debe tener todos los permisos
      return permission.every(perm => userPermissions.includes(perm));
    } else {
      // Basta con tener uno de los permisos
      return permission.some(perm => userPermissions.includes(perm));
    }
  } else {
    // Un solo permiso
    return userPermissions.includes(permission);
  }
};

export default usePermission;
