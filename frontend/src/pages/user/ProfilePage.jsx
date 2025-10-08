import { useAuth } from '../../context/AuthContext';
import { FiUser, FiMail, FiCalendar, FiShield } from 'react-icons/fi';

const ProfilePage = () => {
  const { currentUser } = useAuth();

  // Si no hay usuario, mostrar mensaje
  if (!currentUser) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">No se ha podido cargar la información del usuario.</span>
        </div>
      </div>
    );
  }

  // Obtener el nombre del rol
  const getRoleName = (roleId) => {
    switch (Number(roleId)) {
      case 1:
        return 'Administrador';
      case 2:
        return 'Gestor de Documentos';
      case 3:
        return 'Usuario de Consulta';
      default:
        return 'Rol desconocido';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Mi Perfil</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center mb-6">
          <div className="bg-primary-100 text-primary-600 rounded-full p-4">
            <FiUser size={40} />
          </div>
          <div className="ml-4">
            <h2 className="text-2xl font-semibold">{currentUser.email}</h2>
            <p className="text-gray-600">
              {getRoleName(currentUser.role_id)}
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <FiMail className="mr-2" /> Información de Cuenta
            </h3>
            <div className="space-y-2">
              <p><span className="font-medium">Email:</span> {currentUser.email}</p>
              <p><span className="font-medium">Sub:</span> {currentUser.sub || 'No disponible'}</p>
              <p><span className="font-medium">ID de Rol:</span> {currentUser.role_id} ({getRoleName(currentUser.role_id)})</p>
            </div>
          </div>
          
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <FiShield className="mr-2" /> Información del Token
            </h3>
            <div className="space-y-2">
              <p><span className="font-medium">Expiración:</span> {currentUser.exp ? new Date(currentUser.exp * 1000).toLocaleString() : 'No disponible'}</p>
              <p><span className="font-medium">Token almacenado:</span> {localStorage.getItem('token') ? 'Sí' : 'No'}</p>
            </div>
          </div>
        </div>

        <div className="mt-6 border rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-3">Información Completa del Usuario</h3>
          <pre className="bg-gray-100 p-4 rounded overflow-auto text-xs">
            {JSON.stringify(currentUser, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
