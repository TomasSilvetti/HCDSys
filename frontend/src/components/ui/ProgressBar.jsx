import PropTypes from 'prop-types';

const ProgressBar = ({ progress, height, bgColor, progressColor }) => {
  return (
    <div 
      className={`w-full rounded-full overflow-hidden`}
      style={{ height: height }}
    >
      <div 
        className={`h-full transition-all duration-300 ease-out ${bgColor}`}
      >
        <div
          className={`h-full ${progressColor} transition-all duration-300 ease-out`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

ProgressBar.propTypes = {
  progress: PropTypes.number.isRequired,
  height: PropTypes.string,
  bgColor: PropTypes.string,
  progressColor: PropTypes.string
};

ProgressBar.defaultProps = {
  progress: 0,
  height: '0.5rem',
  bgColor: 'bg-gray-200',
  progressColor: 'bg-blue-600'
};

export default ProgressBar;
