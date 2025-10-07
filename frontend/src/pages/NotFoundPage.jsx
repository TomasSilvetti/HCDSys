import { Link } from 'react-router-dom'
import { FiArrowLeft } from 'react-icons/fi'

const NotFoundPage = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <h1 className="text-9xl font-bold text-primary-600">404</h1>
      <h2 className="text-2xl font-semibold mt-6 mb-4">Página no encontrada</h2>
      <p className="text-secondary-600 max-w-md mb-8">
        Lo sentimos, la página que estás buscando no existe o ha sido movida.
      </p>
      <Link 
        to="/" 
        className="btn btn-primary flex items-center gap-2"
      >
        <FiArrowLeft /> Volver al inicio
      </Link>
    </div>
  )
}

export default NotFoundPage
