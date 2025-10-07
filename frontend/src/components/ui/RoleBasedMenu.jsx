import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';
import { 
  FiUser, 
  FiUsers, 
  FiSettings, 
  FiUpload, 
  FiList, 
  FiFileText, 
  FiShield, 
  FiLogOut,
  FiChevronDown,
  FiChevronUp
} from 'react-icons/fi';

const RoleBasedMenu = ({ userRole, userName, onLogout, isMobile = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  // Cerrar el menú al hacer clic fuera de él
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Opciones de menú según el rol
  const menuOptions = {
    admin: [
      { 
        icon: <FiUsers />, 
        text: 'Gestionar Usuarios', 
        to: '/admin/usuarios',
        description: 'Administrar usuarios y roles'
      },
      { 
        icon: <FiSettings />, 
        text: 'Configuración', 
        to: '/admin/configuracion',
        description: 'Configuración del sistema'
      },
      { 
        icon: <FiShield />, 
        text: 'Permisos', 
        to: '/admin/permisos',
        description: 'Gestionar permisos y roles'
      },
      { 
        icon: <FiList />, 
        text: 'Todos los Documentos', 
        to: '/admin/documentos',
        description: 'Ver todos los documentos'
      }
    ],
    gestor: [
      { 
        icon: <FiUpload />, 
        text: 'Cargar Documento', 
        to: '/documentos/cargar',
        description: 'Subir un nuevo documento'
      },
      { 
        icon: <FiFileText />, 
        text: 'Mis Documentos', 
        to: '/documentos/mis-documentos',
        description: 'Ver documentos subidos'
      },
      { 
        icon: <FiList />, 
        text: 'Categorías', 
        to: '/documentos/categorias',
        description: 'Gestionar categorías'
      }
    ],
    consulta: [
      { 
        icon: <FiFileText />, 
        text: 'Documentos Recientes', 
        to: '/documentos/recientes',
        description: 'Ver documentos recientes'
      }
    ]
  };

  // Obtener las opciones según el rol (si no existe el rol, usar opciones de consulta)
  const roleOptions = menuOptions[userRole] || menuOptions.consulta;
  
  // Color del indicador según el rol
  const getRoleBadgeColor = () => {
    switch (userRole) {
      case 'admin':
        return 'bg-red-500';
      case 'gestor':
        return 'bg-green-500';
      default:
        return 'bg-blue-500';
    }
  };

  // Texto del rol en español
  const getRoleText = () => {
    switch (userRole) {
      case 'admin':
        return 'Administrador';
      case 'gestor':
        return 'Gestor';
      default:
        return 'Usuario';
    }
  };

  // Renderizado para versión móvil
  if (isMobile) {
    return (
      <div className="py-2 border-t border-primary-600 mt-2 animate-fadeIn">
        <div className="flex items-center gap-2 mb-2">
          <span className={`h-2 w-2 rounded-full ${getRoleBadgeColor()}`} aria-hidden="true"></span>
          <span className="text-sm font-medium">{userName} ({getRoleText()})</span>
        </div>
        
        {/* Opciones específicas del rol */}
        {roleOptions.map((option, index) => (
          <Link 
            key={index}
            to={option.to} 
            className="block hover:text-primary-200 py-2 transition-all duration-200 hover:pl-2"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            {option.icon} {option.text}
          </Link>
        ))}
        
        {/* Opciones estándar */}
        <Link 
          to="/perfil" 
          className="block hover:text-primary-200 py-2 transition-all duration-200 hover:pl-2"
          style={{ animationDelay: `${roleOptions.length * 50}ms` }}
        >
          <FiUser /> Mi Perfil
        </Link>
        <button 
          onClick={onLogout} 
          className="block hover:text-primary-200 py-2 w-full text-left transition-all duration-200 hover:pl-2"
          style={{ animationDelay: `${(roleOptions.length + 1) * 50}ms` }}
        >
          <FiLogOut /> Cerrar Sesión
        </button>
      </div>
    );
  }

  // Renderizado para versión desktop
  return (
    <div className="relative" ref={menuRef}>
      <button 
        className="hover:text-primary-200 flex items-center gap-1 transition-colors duration-200"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-label="Menú de usuario"
      >
        <span className={`h-2 w-2 rounded-full ${getRoleBadgeColor()} inline-block mr-1`} 
          aria-hidden="true"></span>
        <FiUser /> 
        <span className="max-w-[120px] truncate">{userName}</span>
        {isOpen ? 
          <FiChevronUp className="ml-1 transition-transform duration-200" /> : 
          <FiChevronDown className="ml-1 transition-transform duration-200" />
        }
      </button>
      
      {isOpen && (
        <div 
          className="absolute right-0 mt-2 w-64 bg-white text-secondary-800 rounded-md shadow-lg py-1 z-10 animate-slideDown"
        >
          <div className="px-4 py-2 border-b border-gray-100">
            <p className="text-sm font-medium">{userName}</p>
            <p className="text-xs text-gray-500 flex items-center gap-1">
              <span className={`h-2 w-2 rounded-full ${getRoleBadgeColor()}`}></span>
              {getRoleText()}
            </p>
          </div>
          
          {/* Opciones específicas del rol */}
          {roleOptions.length > 0 && (
            <div className="py-1 border-b border-gray-100">
              {roleOptions.map((option, index) => (
                <Link 
                  key={index}
                  to={option.to} 
                  className="block px-4 py-2 hover:bg-secondary-100 transition-all duration-200 hover:pl-6"
                  onClick={() => setIsOpen(false)}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="flex items-start gap-2">
                    <div className="text-primary-600 mt-0.5">{option.icon}</div>
                    <div>
                      <div className="font-medium">{option.text}</div>
                      <div className="text-xs text-gray-500">{option.description}</div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
          
          {/* Opciones estándar */}
          <Link 
            to="/perfil" 
            className="block px-4 py-2 hover:bg-secondary-100 transition-all duration-200 hover:pl-6 flex items-center gap-2"
            onClick={() => setIsOpen(false)}
            style={{ animationDelay: `${roleOptions.length * 50}ms` }}
          >
            <FiUser size={14} /> Mi Perfil
          </Link>
          <button 
            onClick={() => {
              onLogout();
              setIsOpen(false);
            }} 
            className="block w-full text-left px-4 py-2 hover:bg-secondary-100 transition-all duration-200 hover:pl-6 flex items-center gap-2 text-red-600"
            style={{ animationDelay: `${(roleOptions.length + 1) * 50}ms` }}
          >
            <FiLogOut size={14} /> Cerrar Sesión
          </button>
        </div>
      )}
    </div>
  );
};

RoleBasedMenu.propTypes = {
  userRole: PropTypes.string.isRequired,
  userName: PropTypes.string.isRequired,
  onLogout: PropTypes.func.isRequired,
  isMobile: PropTypes.bool
};

export default RoleBasedMenu;