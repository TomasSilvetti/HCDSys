import { Outlet } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';

/**
 * Componente para proteger rutas que requieren permisos de gestor de documentos
 * Utiliza ProtectedRoute con configuración específica para gestores
 * 
 * @param {Object} props - Propiedades del componente
 * @param {JSX.Element} props.children - Componente hijo a renderizar
 * @returns {JSX.Element} Ruta protegida para gestores de documentos
 */
const GestorRoute = ({ children }) => {
  console.log('Renderizando GestorRoute - Requiere roles 1 o 2');
  return (
    <ProtectedRoute allowedRoles={['1', '2']}>
      {children || <Outlet />}
    </ProtectedRoute>
  );
};

export default GestorRoute;
