import PropTypes from 'prop-types';
import usePermission from '../../hooks/usePermission';

/**
 * Componente para renderizado condicional basado en permisos
 * 
 * @param {Object} props - Propiedades del componente
 * @param {string|Array} props.permissions - Permiso o array de permisos requeridos
 * @param {boolean} props.requireAll - Si es true, se requieren todos los permisos; si es false, basta con uno
 * @param {React.ReactNode} props.children - Contenido a mostrar si el usuario tiene los permisos
 * @param {React.ReactNode} props.fallback - Contenido a mostrar si el usuario no tiene los permisos
 * @returns {React.ReactNode} Contenido condicionado a los permisos
 */
const PermissionGate = ({ 
  permissions, 
  requireAll = false, 
  children, 
  fallback = null 
}) => {
  const hasPermission = usePermission(permissions, requireAll);
  
  return hasPermission ? children : fallback;
};

PermissionGate.propTypes = {
  permissions: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string)
  ]).isRequired,
  requireAll: PropTypes.bool,
  children: PropTypes.node.isRequired,
  fallback: PropTypes.node
};

export default PermissionGate;
