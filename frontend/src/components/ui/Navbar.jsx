import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FiMenu, FiX, FiUser, FiLogIn, FiSearch } from 'react-icons/fi'

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false)
  const navigate = useNavigate()
  
  // Estado de autenticación simulado - reemplazar con lógica real
  const isAuthenticated = false
  const userName = "Usuario"

  const toggleMenu = () => {
    setIsOpen(!isOpen)
  }

  const handleLogout = () => {
    // Implementar lógica de cierre de sesión
    navigate('/')
  }

  return (
    <nav className="bg-primary-700 text-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link to="/" className="text-xl font-bold">
            HCDSys
          </Link>

          {/* Menú de escritorio */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/buscar" className="hover:text-primary-200 flex items-center gap-1">
              <FiSearch /> Buscar
            </Link>
            
            {isAuthenticated ? (
              <>
                <div className="relative group">
                  <button className="hover:text-primary-200 flex items-center gap-1">
                    <FiUser /> {userName}
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white text-secondary-800 rounded-md shadow-lg py-1 z-10 hidden group-hover:block">
                    <Link to="/perfil" className="block px-4 py-2 hover:bg-secondary-100">Mi Perfil</Link>
                    <button 
                      onClick={handleLogout} 
                      className="block w-full text-left px-4 py-2 hover:bg-secondary-100"
                    >
                      Cerrar Sesión
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:text-primary-200 flex items-center gap-1">
                  <FiLogIn /> Iniciar Sesión
                </Link>
                <Link to="/registro" className="bg-white text-primary-700 px-4 py-2 rounded-md hover:bg-primary-50">
                  Registrarse
                </Link>
              </>
            )}
          </div>

          {/* Botón de menú móvil */}
          <div className="md:hidden">
            <button onClick={toggleMenu} className="focus:outline-none">
              {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>
          </div>
        </div>

        {/* Menú móvil */}
        {isOpen && (
          <div className="md:hidden py-4 space-y-4">
            <Link 
              to="/buscar" 
              className="block hover:text-primary-200 py-2"
              onClick={() => setIsOpen(false)}
            >
              <FiSearch className="inline mr-2" /> Buscar
            </Link>
            
            {isAuthenticated ? (
              <>
                <Link 
                  to="/perfil" 
                  className="block hover:text-primary-200 py-2"
                  onClick={() => setIsOpen(false)}
                >
                  <FiUser className="inline mr-2" /> Mi Perfil
                </Link>
                <button 
                  onClick={() => {
                    handleLogout()
                    setIsOpen(false)
                  }} 
                  className="block hover:text-primary-200 py-2 w-full text-left"
                >
                  Cerrar Sesión
                </button>
              </>
            ) : (
              <>
                <Link 
                  to="/login" 
                  className="block hover:text-primary-200 py-2"
                  onClick={() => setIsOpen(false)}
                >
                  <FiLogIn className="inline mr-2" /> Iniciar Sesión
                </Link>
                <Link 
                  to="/registro" 
                  className="block bg-white text-primary-700 px-4 py-2 rounded-md hover:bg-primary-50 text-center"
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
