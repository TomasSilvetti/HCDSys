import { Link } from 'react-router-dom';
import { FiSearch, FiUpload } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';

const HeroSection = () => {
  const { isAuthenticated, userRole } = useAuth();

  return (
    <section className="hero-wave-bg bg-gradient-to-r from-primary-700 to-primary-900 text-white rounded-lg p-8 md:p-12 relative overflow-hidden">
      <div className="max-w-3xl mx-auto text-center relative z-10">
        <div className="flex justify-center mb-6">
          <img src="/images/logo.svg" alt="HCD Lules Logo" className="h-16 md:h-20" />
        </div>
        <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 animate-fadeIn">
          Sistema de Gestión Documental Municipal
        </h1>
        <p className="text-lg md:text-xl mb-8 animate-fadeIn" style={{ animationDelay: '0.2s' }}>
          Bienvenido al sistema de gestión documental del Honorable Concejo Deliberante de Lules.
          Acceda, busque y gestione documentos municipales de manera eficiente.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fadeIn" style={{ animationDelay: '0.4s' }}>
          <Link 
            to="/buscar" 
            className="btn btn-secondary flex items-center justify-center gap-2 text-lg hover:scale-105 transition-transform"
            aria-label="Ir a búsqueda de documentos"
          >
            <FiSearch /> Buscar Documentos
          </Link>
          <Link 
            to={isAuthenticated && (userRole === 'admin' || userRole === 'gestor') ? "/documentos/cargar" : "/login"} 
            className="btn btn-primary flex items-center justify-center gap-2 text-lg hover:scale-105 transition-transform"
            aria-label="Ir a gestión de documentos o iniciar sesión"
          >
            <FiUpload /> Gestionar Documentos
          </Link>
        </div>
      </div>
      
      {/* Elementos decorativos */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-primary-500 opacity-10 rounded-full -translate-y-1/2 translate-x-1/4"></div>
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-primary-500 opacity-10 rounded-full translate-y-1/2 -translate-x-1/4"></div>
    </section>
  );
};

export default HeroSection;
