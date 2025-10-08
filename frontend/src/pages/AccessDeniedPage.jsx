import { useNavigate } from 'react-router-dom';
import { FiShield, FiHome, FiArrowLeft } from 'react-icons/fi';

/**
 * Página de acceso denegado (403)
 * Muestra un mensaje de error cuando el usuario intenta acceder a una página sin permisos
 */
const AccessDeniedPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            <FiShield className="mx-auto h-16 w-16 text-red-500" />
            <h1 className="mt-2 text-3xl font-bold text-gray-900">Acceso Denegado</h1>
            <p className="mt-2 text-base text-gray-500">
              No tienes permisos para acceder a esta página.
            </p>
          </div>
          
          <div className="mt-8 space-y-4">
            <button
              onClick={() => navigate(-1)}
              className="w-full flex justify-center items-center gap-2 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <FiArrowLeft /> Volver a la página anterior
            </button>
            
            <button
              onClick={() => navigate('/')}
              className="w-full flex justify-center items-center gap-2 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <FiHome /> Ir a la página principal
            </button>
          </div>
          
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500">
              Si crees que deberías tener acceso a esta página, contacta con el administrador.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccessDeniedPage;
