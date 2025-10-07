import { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';

const FeatureCard = ({ icon, title, description, delay = 0 }) => {
  const [isVisible, setIsVisible] = useState(false);
  const cardRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        // Cuando el componente entra en el viewport
        if (entry.isIntersecting) {
          // Añadimos un pequeño retraso para crear un efecto escalonado
          setTimeout(() => {
            setIsVisible(true);
          }, delay);
          // Dejar de observar una vez que se ha hecho visible
          observer.unobserve(cardRef.current);
        }
      },
      { threshold: 0.1 } // Trigger cuando al menos 10% del elemento es visible
    );

    if (cardRef.current) {
      observer.observe(cardRef.current);
    }

    return () => {
      if (cardRef.current) {
        observer.unobserve(cardRef.current);
      }
    };
  }, [delay]);

  return (
    <div 
      ref={cardRef}
      className={`bg-white p-6 rounded-lg shadow-md border border-secondary-200 hover:shadow-lg transition-all duration-500 ${
        isVisible 
          ? 'opacity-100 transform translate-y-0' 
          : 'opacity-0 transform translate-y-10'
      }`}
    >
      <div className="bg-primary-100 p-3 rounded-full w-14 h-14 flex items-center justify-center mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-secondary-600">
        {description}
      </p>
    </div>
  );
};

FeatureCard.propTypes = {
  icon: PropTypes.node.isRequired,
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  delay: PropTypes.number
};

export default FeatureCard;
