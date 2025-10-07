import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiAlertCircle, FiArrowLeft, FiCheckCircle } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

const EditUserRolePage = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, userRole, currentUser } = useAuth();
  
  const [user, setUser] = useState(null);
  const [roles, setRoles] = useState([]);
  const [selectedRoleId, setSelectedRoleId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  // Cargar datos del usuario y roles disponibles
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
        setSelectedRoleId(userResponse.data.role_id);
        
        // Cargar roles
        const rolesResponse = await api.get('/roles');
        setRoles(rolesResponse.data);
      } catch (err) {
        console.error('Error al cargar datos:', err);
        setError('Error al cargar información del usuario. Por favor, inténtelo de nuevo.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [isAuthenticated, userRole, userId, navigate]);
  
  // Manejar cambio de rol
  const handleRoleChange = (e) => {
    setSelectedRoleId(Number(e.target.value));
  };
  
  // Guardar cambios
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Verificar si el rol ha cambiado
    if (selectedRoleId === user.role_id) {
      setError('El rol seleccionado es el mismo que el actual.');
      return;
    }
    
    // Verificar si el usuario intenta cambiar su propio rol siendo administrador
    if (Number(userId) === currentUser.id && user.role_id === 1) {
      setError('No puede cambiar su propio rol de administrador.');
      return;
    }
    
    setIsSaving(true);
    setError(null);
    
    try {
      await api.put(`/roles/users/${userId}`, {
        role_id: selectedRoleId
      });
      
      setSuccess(true);
      
      // Redireccionar después de 2 segundos
      setTimeout(() => {
        navigate('/admin/users');
      }, 2000);
    } catch (err) {
      console.error('Error al actualizar rol:', err);
      setError(err.response?.data?.detail || 'Error al actualizar el rol. Por favor, inténtelo de nuevo.');
    } finally {
      setIsSaving(false);
    }
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
      <div className="max-w-2xl mx-auto">
        {/* Botón para volver */}
        <button
          onClick={() => navigate('/admin/users')}
          className="flex items-center text-gray-600 hover:text-gray-800 mb-6"
        >
          <FiArrowLeft className="mr-2" /> Volver a la lista de usuarios
        </button>
        
        <div className="bg-white shadow-md rounded-lg p-6">
          <h1 className="text-2xl font-bold mb-6">Editar Rol de Usuario</h1>
          
          {/* Información del usuario */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Información del Usuario</h2>
            <p><strong>Nombre:</strong> {user.nombre} {user.apellido}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>DNI:</strong> {user.dni}</p>
          </div>
          
          {/* Mensajes de error o éxito */}
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded flex items-start">
              <FiAlertCircle className="mr-2 mt-0.5 flex-shrink-0" />
              <p>{error}</p>
            </div>
          )}
          
          {success && (
            <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded flex items-start">
              <FiCheckCircle className="mr-2 mt-0.5 flex-shrink-0" />
              <p>Rol actualizado correctamente. Redirigiendo...</p>
            </div>
          )}
          
          {/* Formulario de edición de rol */}
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
                Rol Actual: <span className="font-semibold">{roles.find(r => r.id === user.role_id)?.nombre || 'Desconocido'}</span>
              </label>
              
              <div className="mt-1">
                <select
                  id="role"
                  name="role"
                  value={selectedRoleId}
                  onChange={handleRoleChange}
                  className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 rounded-md"
                  disabled={isSaving || success}
                >
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.nombre} - {role.descripcion}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            {/* Advertencia para administradores */}
            {user.role_id === 1 && (
              <div className="mb-6 p-3 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
                <p className="flex items-start">
                  <FiAlertCircle className="mr-2 mt-0.5 flex-shrink-0" />
                  <span>
                    Este usuario tiene rol de Administrador. Cambiar este rol puede afectar los permisos de acceso al sistema.
                    {Number(userId) === currentUser.id && (
                      <strong className="block mt-1">No puede cambiar su propio rol de administrador.</strong>
                    )}
                  </span>
                </p>
              </div>
            )}
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => navigate('/admin/users')}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                disabled={isSaving || success}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                disabled={isSaving || success || selectedRoleId === user.role_id || (Number(userId) === currentUser.id && user.role_id === 1)}
              >
                {isSaving ? 'Guardando...' : 'Guardar Cambios'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EditUserRolePage;
