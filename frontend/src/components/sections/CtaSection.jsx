import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const CtaSection = () => {
  const { isAuthenticated } = useAuth();
  
  if (isAuthenticated) {
    return null; // No mostrar CTA si el usuario ya está autenticado
  }
  
  return (
    <section className="bg-gradient-to-r from-primary-700 to-primary-900 text-white rounded-lg p-8 text-center">
      <h2 className="text-2xl md:text-3xl font-bold mb-4">¿Listo para comenzar?</h2>
      <p className="text-lg mb-6 max-w-2xl mx-auto">
        Regístrese ahora para acceder a todas las funcionalidades del sistema o inicie sesión si ya tiene una cuenta.
      </p>
      <div className="flex flex-col sm:flex-row justify-center gap-4">
        <Link 
          to="/registro" 
          className="btn bg-white text-primary-700 hover:bg-primary-50 text-lg px-6 py-3 hover:scale-105 transition-transform"
          aria-label="Crear una cuenta nueva"
        >
          Crear Cuenta
        </Link>
        <Link 
          to="/login" 
          className="btn bg-primary-600 text-white border border-white hover:bg-primary-800 text-lg px-6 py-3 hover:scale-105 transition-transform"
          aria-label="Iniciar sesión con cuenta existente"
        >
          Iniciar Sesión
        </Link>
      </div>
    </section>
  );
};

export default CtaSection;
