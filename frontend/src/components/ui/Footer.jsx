import { Link } from 'react-router-dom'

const Footer = () => {
  const currentYear = new Date().getFullYear()
  
  return (
    <footer className="bg-secondary-800 text-white py-8">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-bold mb-4">HCDSys</h3>
            <p className="text-secondary-300">
              Sistema de gestión documental para el Honorable Concejo Deliberante de Lules.
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-bold mb-4">Enlaces</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-secondary-300 hover:text-white">
                  Inicio
                </Link>
              </li>
              <li>
                <Link to="/buscar" className="text-secondary-300 hover:text-white">
                  Búsqueda
                </Link>
              </li>
              <li>
                <Link to="/login" className="text-secondary-300 hover:text-white">
                  Iniciar Sesión
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-bold mb-4">Contacto</h3>
            <address className="text-secondary-300 not-italic">
              <p>Honorable Concejo Deliberante</p>
              <p>Municipalidad de Lules</p>
              <p>Tucumán, Argentina</p>
            </address>
          </div>
        </div>
        
        <div className="border-t border-secondary-700 mt-8 pt-6 text-center text-secondary-400">
          <p>&copy; {currentYear} HCDSys - Todos los derechos reservados</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
