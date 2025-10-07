import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiClock } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

const UserRoleHistoryPage = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, userRole } = useAuth();
  
  const [user, setUser] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Cargar datos del usuario y su historial de roles
  useEffect(() => {
    // Verificar autenticación y permisos
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    if (userRole !== 1) { // Asumiendo que el rol 1 es Administrador
      navigate('/');
      return;
    }
    
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Cargar usuario
        const userResponse = await api.get(`/users/${userId}`);
        setUser(userResponse.data);
        
        // Cargar historial de roles
        const historyResponse = await api.get(`/roles/users/${userId}/history`);
        setHistory(historyResponse.data);
      } catch (err) {
        console.error('Error al cargar datos:', err);
        setError('Error al cargar historial. Por favor, inténtelo de nuevo.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [isAuthenticated, userRole, userId, navigate]);
  
  // Formatear fecha
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  // Renderizar página de carga
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  // Renderizar página de error si no se encuentra el usuario
  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>Usuario no encontrado.</p>
          <button 
            className="mt-2 bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700"
            onClick={() => navigate('/admin/users')}
          >
            Volver a la lista de usuarios
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        {/* Botón para volver */}
        <button
          onClick={() => navigate('/admin/users')}
          className="flex items-center text-gray-600 hover:text-gray-800 mb-6"
        >
          <FiArrowLeft className="mr-2" /> Volver a la lista de usuarios
        </button>
        
        <div className="bg-white shadow-md rounded-lg p-6">
          <h1 className="text-2xl font-bold mb-6">Historial de Cambios de Rol</h1>
          
          {/* Información del usuario */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Información del Usuario</h2>
            <p><strong>Nombre:</strong> {user.nombre} {user.apellido}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>DNI:</strong> {user.dni}</p>
          </div>
          
          {/* Mensajes de error */}
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              <p>{error}</p>
            </div>
          )}
          
          {/* Historial de cambios */}
          <div className="mt-6">
            <h2 className="text-lg font-semibold mb-4">Cambios de Rol</h2>
            
            {history.length > 0 ? (
              <div className="border rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fecha
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Rol Anterior
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Rol Nuevo
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Modificado Por
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {history.map((entry) => (
                      <tr key={entry.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div className="flex items-center">
                            <FiClock className="mr-2 text-gray-400" />
                            {formatDate(entry.fecha_cambio)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                            ${entry.rol_anterior.id === 1 ? 'bg-purple-100 text-purple-800' : 
                              entry.rol_anterior.id === 2 ? 'bg-blue-100 text-blue-800' : 
                              'bg-green-100 text-green-800'}`}>
                            {entry.rol_anterior.nombre}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                            ${entry.rol_nuevo.id === 1 ? 'bg-purple-100 text-purple-800' : 
                              entry.rol_nuevo.id === 2 ? 'bg-blue-100 text-blue-800' : 
                              'bg-green-100 text-green-800'}`}>
                            {entry.rol_nuevo.nombre}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {entry.modificado_por.nombre} {entry.modificado_por.apellido}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No hay cambios de rol registrados para este usuario.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserRoleHistoryPage;
