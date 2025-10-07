import { FiFileText } from 'react-icons/fi';

const DocumentTypesSection = () => {
  const documentTypes = [
    {
      title: "Ordenanzas",
      description: "Disposiciones normativas del Concejo Deliberante"
    },
    {
      title: "Resoluciones",
      description: "Decisiones sobre asuntos específicos"
    },
    {
      title: "Actas",
      description: "Registros de sesiones y reuniones"
    },
    {
      title: "Decretos",
      description: "Disposiciones del Ejecutivo Municipal"
    },
    {
      title: "Expedientes",
      description: "Documentación de trámites administrativos"
    },
    {
      title: "Comunicaciones",
      description: "Notificaciones oficiales del Concejo"
    }
  ];

  return (
    <section className="bg-secondary-50 py-8 px-4 rounded-lg">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold text-center mb-3">Tipos de Documentos</h2>
        <p className="text-center text-secondary-600 mb-8 max-w-2xl mx-auto">
          El sistema gestiona diversos tipos de documentos municipales
        </p>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {documentTypes.map((docType, index) => (
            <div 
              key={index} 
              className="flex items-start gap-3 hover:bg-white p-3 rounded-lg transition-colors duration-200"
            >
              <div className="bg-primary-100 p-2 rounded-md">
                <FiFileText className="text-primary-600 text-xl" />
              </div>
              <div>
                <h3 className="font-semibold">{docType.title}</h3>
                <p className="text-sm text-secondary-600">{docType.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default DocumentTypesSection;
