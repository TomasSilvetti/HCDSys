import { Link } from 'react-router-dom'
import { FiSearch, FiUpload, FiInfo } from 'react-icons/fi'

const HomePage = () => {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-700 to-primary-900 text-white rounded-lg p-8 md:p-12">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            Sistema de Gestión Documental Municipal
          </h1>
          <p className="text-lg md:text-xl mb-8">
            Bienvenido al sistema de gestión documental del Honorable Concejo Deliberante de Lules.
            Acceda, busque y gestione documentos municipales de manera eficiente.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/buscar" 
              className="btn btn-secondary flex items-center justify-center gap-2"
            >
              <FiSearch /> Buscar Documentos
            </Link>
            <Link 
              to="/login" 
              className="btn btn-primary flex items-center justify-center gap-2"
            >
              <FiUpload /> Gestionar Documentos
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section>
        <h2 className="text-2xl font-bold text-center mb-8">Funcionalidades Principales</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-secondary-200">
            <div className="bg-primary-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <FiSearch className="text-primary-600 text-xl" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Búsqueda Avanzada</h3>
            <p className="text-secondary-600">
              Encuentre documentos rápidamente utilizando filtros por tipo, fecha, categoría y más.
            </p>
          </div>
          
          {/* Feature 2 */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-secondary-200">
            <div className="bg-primary-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <FiUpload className="text-primary-600 text-xl" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Gestión Documental</h3>
            <p className="text-secondary-600">
              Cargue, actualice y organice documentos con un sistema intuitivo y seguro.
            </p>
          </div>
          
          {/* Feature 3 */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-secondary-200">
            <div className="bg-primary-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <FiInfo className="text-primary-600 text-xl" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Acceso Controlado</h3>
            <p className="text-secondary-600">
              Control de acceso basado en roles para garantizar la seguridad de la información.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-secondary-100 rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold mb-4">¿Listo para comenzar?</h2>
        <p className="text-lg mb-6">
          Regístrese ahora para acceder a todas las funcionalidades del sistema.
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/registro" className="btn btn-primary">
            Crear Cuenta
          </Link>
          <Link to="/login" className="btn btn-secondary">
            Iniciar Sesión
          </Link>
        </div>
      </section>
    </div>
  )
}

export default HomePage
