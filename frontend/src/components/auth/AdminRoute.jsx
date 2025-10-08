import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import ProtectedRoute from './ProtectedRoute';

/**
 * Componente para proteger rutas que requieren permisos de administrador
 * Utiliza ProtectedRoute con configuración específica para administradores
 */
const AdminRoute = ({ children }) => {
  return (
    <ProtectedRoute allowedRoles={['1']}>
      {children || <Outlet />}
    </ProtectedRoute>
  );
};

export default AdminRoute;
