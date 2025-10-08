import { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { FiUpload, FiFile, FiTrash2 } from 'react-icons/fi';

const FileUploader = ({ onFileSelected, selectedFile, disabled, allowedFileTypes, maxSizeMB }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [fileError, setFileError] = useState('');
  const fileInputRef = useRef(null);
  
  // Convertir MB a bytes
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  
  // Formatear tamaño de archivo para mostrar
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    else return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };
  
  // Obtener extensión del archivo
  const getFileExtension = (filename) => {
    return filename.split('.').pop().toLowerCase();
  };
  
  // Validar archivo
  const validateFile = (file) => {
    // Validar tamaño
    if (file.size > maxSizeBytes) {
      setFileError(`El archivo excede el tamaño máximo permitido (${maxSizeMB} MB).`);
      return false;
    }
    
    // Validar tipo
    const fileExt = getFileExtension(file.name);
    if (allowedFileTypes.length > 0 && !allowedFileTypes.includes('.' + fileExt)) {
      setFileError(`Tipo de archivo no permitido. Tipos permitidos: ${allowedFileTypes.join(', ')}`);
      return false;
    }
    
    setFileError('');
    return true;
  };
  
  // Manejar selección de archivo
  const handleFileSelect = (file) => {
    if (!file) return;
    
    if (validateFile(file)) {
      onFileSelected(file);
    } else {
      onFileSelected(null);
    }
  };
  
  // Manejar cambio en input de archivo
  const handleInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };
  
  // Manejar clic en área de drop
  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };
  
  // Manejar eventos de drag & drop
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  };
  
  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (disabled) return;
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };
  
  // Manejar eliminación de archivo
  const handleRemoveFile = () => {
    onFileSelected(null);
    setFileError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  // Limpiar error cuando se cambia el archivo seleccionado
  useEffect(() => {
    if (!selectedFile) {
      setFileError('');
    }
  }, [selectedFile]);
  
  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        Archivo <span className="text-red-500">*</span>
      </label>
      
      {/* Área de drag & drop */}
      <div
        className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer transition-colors
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        onClick={handleClick}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {!selectedFile ? (
          <>
            <FiUpload className="w-10 h-10 text-gray-400 mb-3" />
            <p className="text-gray-700 mb-1">Arrastre y suelte un archivo aquí</p>
            <p className="text-sm text-gray-500">o haga clic para seleccionar un archivo</p>
            <p className="text-xs text-gray-500 mt-2">
              Tipos permitidos: {allowedFileTypes.join(', ')} - Tamaño máximo: {maxSizeMB} MB
            </p>
          </>
        ) : (
          <div className="flex items-center w-full">
            <FiFile className="w-8 h-8 text-blue-500 mr-3" />
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 truncate">{selectedFile.name}</p>
              <p className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</p>
            </div>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                handleRemoveFile();
              }}
              className="p-1 text-gray-500 hover:text-red-500"
              disabled={disabled}
            >
              <FiTrash2 className="w-5 h-5" />
            </button>
          </div>
        )}
        
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleInputChange}
          className="hidden"
          disabled={disabled}
          accept={allowedFileTypes.join(',')}
        />
      </div>
      
      {/* Mensaje de error */}
      {fileError && (
        <p className="text-sm text-red-600 mt-1">{fileError}</p>
      )}
    </div>
  );
};

FileUploader.propTypes = {
  onFileSelected: PropTypes.func.isRequired,
  selectedFile: PropTypes.object,
  disabled: PropTypes.bool,
  allowedFileTypes: PropTypes.arrayOf(PropTypes.string),
  maxSizeMB: PropTypes.number
};

FileUploader.defaultProps = {
  disabled: false,
  selectedFile: null,
  allowedFileTypes: ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'],
  maxSizeMB: 10
};

export default FileUploader;
