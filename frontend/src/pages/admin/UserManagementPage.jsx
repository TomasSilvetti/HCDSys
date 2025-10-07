import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiSearch, FiEdit, FiUser, FiUserCheck, FiUserX, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [roles, setRoles] = useState([]);
  
  // Paginación
  const [currentPage, setCurrentPage] = useState(1);
  const [usersPerPage] = useState(10);
  
  const { isAuthenticated, userRole } = useAuth();
  const navigate = useNavigate();
  
  // Cargar usuarios y roles al montar el componente
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
        // Cargar usuarios
        const usersResponse = await api.get('/users');
        setUsers(usersResponse.data);
        setFilteredUsers(usersResponse.data);
        
        // Cargar roles
        const rolesResponse = await api.get('/roles');
        setRoles(rolesResponse.data);
      } catch (err) {
        console.error('Error al cargar datos:', err);
        setError('Error al cargar usuarios. Por favor, inténtelo de nuevo.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [isAuthenticated, userRole, navigate]);
  
  // Filtrar usuarios según término de búsqueda
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredUsers(users);
      return;
    }
    
    const lowerSearchTerm = searchTerm.toLowerCase();
    const filtered = users.filter(user => 
      user.nombre.toLowerCase().includes(lowerSearchTerm) || 
      user.apellido.toLowerCase().includes(lowerSearchTerm) || 
      user.email.toLowerCase().includes(lowerSearchTerm)
    );
    
    setFilteredUsers(filtered);
    setCurrentPage(1); // Resetear a la primera página al buscar
  }, [searchTerm, users]);
  
  // Obtener usuarios actuales para la página
  const indexOfLastUser = currentPage * usersPerPage;
  const indexOfFirstUser = indexOfLastUser - usersPerPage;
  const currentUsers = filteredUsers.slice(indexOfFirstUser, indexOfLastUser);
  
  // Cambiar de página
  const paginate = (pageNumber) => setCurrentPage(pageNumber);
  
  // Obtener nombre del rol
  const getRoleName = (roleId) => {
    const role = roles.find(r => r.id === roleId);
    return role ? role.nombre : 'Desconocido';
  };
  
  // Seleccionar usuario para ver detalles
  const handleSelectUser = (user) => {
    setSelectedUser(user);
  };
  
  // Renderizar página de carga
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  // Renderizar página de error
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
          <button 
            className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            onClick={() => window.location.reload()}
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Gestión de Usuarios</h1>
      
      {/* Barra de búsqueda */}
      <div className="mb-6">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <FiSearch className="text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Buscar por nombre, apellido o email..."
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
      
      <div className="flex flex-col md:flex-row gap-6">
        {/* Lista de usuarios */}
        <div className="w-full md:w-2/3">
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Usuario
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rol
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentUsers.length > 0 ? (
                  currentUsers.map((user) => (
                    <tr 
                      key={user.id} 
                      className={`hover:bg-gray-50 ${selectedUser?.id === user.id ? 'bg-primary-50' : ''}`}
                      onClick={() => handleSelectUser(user)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center">
                            <FiUser className="h-5 w-5 text-gray-500" />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {user.nombre} {user.apellido}
                            </div>
                            <div className="text-sm text-gray-500">
                              DNI: {user.dni}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{user.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                          ${user.role_id === 1 ? 'bg-purple-100 text-purple-800' : 
                            user.role_id === 2 ? 'bg-blue-100 text-blue-800' : 
                            'bg-green-100 text-green-800'}`}>
                          {getRoleName(user.role_id)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                          ${user.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {user.activo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button 
                          className="text-primary-600 hover:text-primary-900"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSelectUser(user);
                          }}
                        >
                          <FiEdit className="h-5 w-5" />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                      No se encontraron usuarios
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
            
            {/* Paginación */}
            {filteredUsers.length > usersPerPage && (
              <div className="px-6 py-3 flex items-center justify-between border-t border-gray-200">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() => paginate(currentPage - 1)}
                    disabled={currentPage === 1}
                    className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                      currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    Anterior
                  </button>
                  <button
                    onClick={() => paginate(currentPage + 1)}
                    disabled={currentPage === Math.ceil(filteredUsers.length / usersPerPage)}
                    className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                      currentPage === Math.ceil(filteredUsers.length / usersPerPage) ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    Siguiente
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Mostrando <span className="font-medium">{indexOfFirstUser + 1}</span> a{' '}
                      <span className="font-medium">
                        {Math.min(indexOfLastUser, filteredUsers.length)}
                      </span>{' '}
                      de <span className="font-medium">{filteredUsers.length}</span> usuarios
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                      <button
                        onClick={() => paginate(currentPage - 1)}
                        disabled={currentPage === 1}
                        className={`relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium ${
                          currentPage === 1 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        <span className="sr-only">Anterior</span>
                        <FiChevronLeft className="h-5 w-5" />
                      </button>
                      
                      {/* Botones de página */}
                      {[...Array(Math.ceil(filteredUsers.length / usersPerPage)).keys()].map(number => (
                        <button
                          key={number + 1}
                          onClick={() => paginate(number + 1)}
                          className={`relative inline-flex items-center px-4 py-2 border ${
                            currentPage === number + 1
                              ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          } text-sm font-medium`}
                        >
                          {number + 1}
                        </button>
                      ))}
                      
                      <button
                        onClick={() => paginate(currentPage + 1)}
                        disabled={currentPage === Math.ceil(filteredUsers.length / usersPerPage)}
                        className={`relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium ${
                          currentPage === Math.ceil(filteredUsers.length / usersPerPage) ? 'text-gray-300 cursor-not-allowed' : 'text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        <span className="sr-only">Siguiente</span>
                        <FiChevronRight className="h-5 w-5" />
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Panel de detalles del usuario */}
        <div className="w-full md:w-1/3">
          {selectedUser ? (
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Detalles del Usuario</h2>
              
              <div className="flex justify-center mb-6">
                <div className="h-24 w-24 bg-gray-200 rounded-full flex items-center justify-center">
                  {selectedUser.activo ? (
                    <FiUserCheck className="h-12 w-12 text-green-600" />
                  ) : (
                    <FiUserX className="h-12 w-12 text-red-600" />
                  )}
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Nombre Completo</h3>
                  <p className="text-base">{selectedUser.nombre} {selectedUser.apellido}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Email</h3>
                  <p className="text-base">{selectedUser.email}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">DNI</h3>
                  <p className="text-base">{selectedUser.dni}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Rol</h3>
                  <div className="flex items-center justify-between">
                    <p className="text-base">{getRoleName(selectedUser.role_id)}</p>
                    <button 
                      className="text-sm text-primary-600 hover:text-primary-800"
                      onClick={() => navigate(`/admin/users/${selectedUser.id}/edit-role`)}
                    >
                      Cambiar Rol
                    </button>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Estado</h3>
                  <p className={`text-base ${selectedUser.activo ? 'text-green-600' : 'text-red-600'}`}>
                    {selectedUser.activo ? 'Activo' : 'Inactivo'}
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Fecha de Registro</h3>
                  <p className="text-base">
                    {new Date(selectedUser.fecha_registro).toLocaleDateString('es-ES')}
                  </p>
                </div>
                
                {selectedUser.ultimo_acceso && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Último Acceso</h3>
                    <p className="text-base">
                      {new Date(selectedUser.ultimo_acceso).toLocaleDateString('es-ES', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                )}
              </div>
              
              <div className="mt-6 flex space-x-3">
                <button 
                  className="flex-1 bg-primary-600 text-white py-2 px-4 rounded hover:bg-primary-700"
                  onClick={() => navigate(`/admin/users/${selectedUser.id}/edit-role`)}
                >
                  Editar Rol
                </button>
                <button 
                  className="flex-1 border border-gray-300 text-gray-700 py-2 px-4 rounded hover:bg-gray-50"
                  onClick={() => navigate(`/admin/users/${selectedUser.id}/history`)}
                >
                  Ver Historial
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-white shadow-md rounded-lg p-6 text-center text-gray-500">
              <FiUser className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Seleccione un usuario para ver sus detalles</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserManagementPage;
