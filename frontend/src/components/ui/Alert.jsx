import PropTypes from 'prop-types';
import { FiAlertCircle, FiCheckCircle, FiInfo, FiX } from 'react-icons/fi';

const Alert = ({ type, message, onClose }) => {
  const alertStyles = {
    success: {
      bg: 'bg-green-50',
      border: 'border-green-400',
      text: 'text-green-800',
      icon: <FiCheckCircle className="h-5 w-5 text-green-500" />
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-400',
      text: 'text-red-800',
      icon: <FiAlertCircle className="h-5 w-5 text-red-500" />
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-400',
      text: 'text-yellow-800',
      icon: <FiInfo className="h-5 w-5 text-yellow-500" />
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-400',
      text: 'text-blue-800',
      icon: <FiInfo className="h-5 w-5 text-blue-500" />
    }
  };

  const style = alertStyles[type] || alertStyles.info;

  return (
    <div className={`${style.bg} ${style.border} border-l-4 p-4 mb-4 rounded`}>
      <div className="flex items-start">
        <div className="flex-shrink-0 mr-3">
          {style.icon}
        </div>
        <div className={`flex-1 ${style.text}`}>
          <p>{message}</p>
        </div>
        {onClose && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                onClick={onClose}
                className={`inline-flex rounded-md p-1.5 ${style.text} hover:bg-opacity-20 hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-${type}-50 focus:ring-${type}-600`}
              >
                <span className="sr-only">Cerrar</span>
                <FiX className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

Alert.propTypes = {
  type: PropTypes.oneOf(['success', 'error', 'warning', 'info']),
  message: PropTypes.string.isRequired,
  onClose: PropTypes.func
};

Alert.defaultProps = {
  type: 'info'
};

export default Alert;
