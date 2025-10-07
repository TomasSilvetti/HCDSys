import { FiSearch, FiUpload, FiShield, FiClock } from 'react-icons/fi';
import FeatureCard from '../ui/FeatureCard';

const FeaturesSection = () => {
  const features = [
    {
      icon: <FiSearch className="text-primary-600 text-2xl" />,
      title: "Búsqueda Avanzada",
      description: "Encuentre documentos rápidamente utilizando filtros por tipo, fecha, categoría y más."
    },
    {
      icon: <FiUpload className="text-primary-600 text-2xl" />,
      title: "Gestión Documental",
      description: "Cargue, actualice y organice documentos con un sistema intuitivo y seguro."
    },
    {
      icon: <FiClock className="text-primary-600 text-2xl" />,
      title: "Acceso Rápido",
      description: "Encuentre documentos al instante con nuestro potente motor de búsqueda optimizado."
    },
    {
      icon: <FiShield className="text-primary-600 text-2xl" />,
      title: "Acceso Controlado",
      description: "Control de acceso basado en roles para garantizar la seguridad de la información."
    }
  ];

  return (
    <section className="py-12">
      <div className="container mx-auto px-4">
        <h2 className="text-2xl md:text-3xl font-bold text-center mb-2">Funcionalidades Principales</h2>
        <p className="text-center text-secondary-600 mb-8 max-w-2xl mx-auto">
          Nuestro sistema ofrece herramientas completas para la gestión eficiente de documentos municipales
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              delay={index * 150} // Retraso escalonado para animación
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
