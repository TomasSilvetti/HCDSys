import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { FiMenu, FiX, FiSearch } from 'react-icons/fi'
import { useAuth } from '../../context/AuthContext'
import { toast } from 'react-toastify'
import RoleBasedMenu from './RoleBasedMenu'

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { currentUser, isAuthenticated, logout } = useAuth()
  
  // Efecto para cerrar el menú al cambiar de ruta
  useEffect(() => {
    setIsOpen(false)
  }, [location.pathname])

  // Efecto para detectar scroll y aplicar estilos
  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 10
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled)
      }
    }

    window.addEventListener('scroll', handleScroll)
    
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [scrolled])

  const toggleMenu = () => {
    setIsOpen(!isOpen)
  }

  const handleLogout = () => {
    logout()
    toast.success('Sesión cerrada correctamente')
    navigate('/')
  }

  return (
    <nav className={`bg-primary-700 text-white navbar-sticky ${scrolled ? 'navbar-scrolled' : ''}`}>
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link 
            to="/" 
            className="flex items-center space-x-2 animate-fadeInLeft"
            style={{ animationDuration: '0.5s' }}
          >
            <img src="/images/logo.svg" alt="HCD Lules Logo" className="h-8 transition-transform duration-300 hover:scale-105" />
          </Link>

          {/* Menú de escritorio */}
          <div className="hidden md:flex items-center space-x-6 animate-fadeInRight" style={{ animationDuration: '0.5s' }}>
            <Link 
              to="/buscar" 
              className="nav-link hover:text-primary-200 flex items-center gap-1 transition-colors duration-200"
            >
              <FiSearch className="transition-transform duration-300 group-hover:scale-110" /> 
              <span>Buscar</span>
            </Link>
            
            {isAuthenticated ? (
              <RoleBasedMenu 
                userRole={currentUser?.role || 'consulta'} 
                userName={currentUser?.nombre || 'Usuario'} 
                onLogout={handleLogout} 
              />
            ) : (
              <>
                <Link 
                  to="/login" 
                  className="nav-link hover:text-primary-200 flex items-center gap-1 transition-colors duration-200"
                >
                  Iniciar Sesión
                </Link>
                <Link 
                  to="/registro" 
                  className="bg-white text-primary-700 px-4 py-2 rounded-md hover:bg-primary-50 transition-all duration-300 hover:shadow-md"
                >
                  Registrarse
                </Link>
              </>
            )}
          </div>

          {/* Botón de menú móvil */}
          <div className="md:hidden">
            <button 
              onClick={toggleMenu} 
              className="focus:outline-none transition-transform duration-300 hover:scale-110"
              aria-label={isOpen ? "Cerrar menú" : "Abrir menú"}
              aria-expanded={isOpen}
            >
              {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>
          </div>
        </div>

        {/* Menú móvil */}
        {isOpen && (
          <div className="md:hidden py-4 space-y-4 animate-slideDown">
            <Link 
              to="/buscar" 
              className="block hover:text-primary-200 py-2 transition-colors duration-200 hover:pl-2"
              onClick={() => setIsOpen(false)}
            >
              <FiSearch className="inline mr-2" /> Buscar
            </Link>
            
            {isAuthenticated ? (
              <RoleBasedMenu 
                userRole={currentUser?.role || 'consulta'} 
                userName={currentUser?.nombre || 'Usuario'} 
                onLogout={handleLogout}
                isMobile={true}
              />
            ) : (
              <>
                <Link 
                  to="/login" 
                  className="block hover:text-primary-200 py-2 transition-colors duration-200 hover:pl-2"
                  onClick={() => setIsOpen(false)}
                >
                  Iniciar Sesión
                </Link>
                <Link 
                  to="/registro" 
                  className="block bg-white text-primary-700 px-4 py-2 rounded-md hover:bg-primary-50 text-center transition-colors duration-200"
                  onClick={() => setIsOpen(false)}
                >
                  Registrarse
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar