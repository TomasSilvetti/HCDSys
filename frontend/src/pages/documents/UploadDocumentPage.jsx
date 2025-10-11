import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { documentService } from '../../utils/documentService';
import { useAuth } from '../../context/AuthContext';

// Componentes que crearemos a continuación
import DocumentForm from '../../components/documents/DocumentForm';
import FileUploader from '../../components/documents/FileUploader';
import ProgressBar from '../../components/ui/ProgressBar';
import Alert from '../../components/ui/Alert';

const UploadDocumentPage = () => {
  // Estado para el formulario
  const [formData, setFormData] = useState({
    titulo: '',
    numero_expediente: '',
    descripcion: '',
    categoria_id: '',
    tipo_documento_id: '',
  });
  
  // Estado para el archivo
  const [file, setFile] = useState(null);
  
  // Estado para las opciones de los selectores
  const [categories, setCategories] = useState([]);
  const [documentTypes, setDocumentTypes] = useState([]);
  
  // Estados para manejo de carga y errores
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  
  // Cargar categorías y tipos de documentos al montar el componente
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [categoriesData, typesData] = await Promise.all([
          documentService.getCategories(),
          documentService.getDocumentTypes()
        ]);
        
        setCategories(categoriesData);
        setDocumentTypes(typesData);
      } catch (error) {
        setError('Error al cargar datos: ' + error.message);
      }
    };
    
    fetchData();
  }, []);
  
  // Manejar cambios en los campos del formulario
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };
  
  // Detectar tipo de documento basado en la extensión del archivo
  const detectDocumentType = (selectedFile) => {
    if (!selectedFile || !documentTypes.length) return null;
    
    // Obtener la extensión del archivo
    const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
    if (!fileExtension) return null;
    
    // Buscar un tipo de documento que permita esta extensión
    const matchingType = documentTypes.find(type => {
      const allowedExtensions = type.extensiones_permitidas.split(',').map(ext => ext.trim().toLowerCase());
      return allowedExtensions.includes(`.${fileExtension}`) || allowedExtensions.includes(fileExtension);
    });
    
    return matchingType ? matchingType.id : null;
  };
  
  // Extraer nombre de archivo sin extensión
  const extractFileNameWithoutExtension = (fileName) => {
    if (!fileName) return '';
    // Eliminar la extensión del archivo
    return fileName.split('.').slice(0, -1).join('.');
  };

  // Manejar selección de archivo
  const handleFileChange = (selectedFile) => {
    setFile(selectedFile);
    
    if (selectedFile) {
      // Extraer el título del nombre del archivo (sin extensión)
      const fileTitle = extractFileNameWithoutExtension(selectedFile.name);
      
      // Autodetectar tipo de documento
      const detectedTypeId = detectDocumentType(selectedFile);
      
      if (detectedTypeId) {
        setFormData(prevData => ({
          ...prevData,
          titulo: fileTitle, // Establecer el título automáticamente
          tipo_documento_id: detectedTypeId
        }));
      } else {
        // Si no se puede detectar el tipo, mostrar un error
        setError('No se pudo detectar el tipo de documento para esta extensión de archivo. Por favor, seleccione otro archivo.');
      }
    } else {
      // Si se elimina el archivo, limpiar el tipo de documento y el título
      setFormData(prevData => ({
        ...prevData,
        titulo: '',
        tipo_documento_id: ''
      }));
    }
  };
  
  // Manejar envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validar campos obligatorios
    if (!formData.titulo || !formData.numero_expediente || !formData.tipo_documento_id || !file) {
      setError('Por favor complete todos los campos obligatorios y seleccione un archivo.');
      return;
    }
    
    setLoading(true);
    setError('');
    setUploadProgress(0);
    
    try {
      // Preparar datos para envío
      const documentData = {
        ...formData,
        archivo: file
      };
      
      // Enviar documento con seguimiento de progreso
      const response = await documentService.uploadDocument(
        documentData, 
        (progress) => setUploadProgress(progress)
      );
      
      setSuccess('Documento cargado correctamente');
      
      // Redireccionar a la página de detalle del documento
      setTimeout(() => {
        navigate(`/documents/${response.id}`);
      }, 2000);
      
    } catch (error) {
      setError('Error al cargar documento: ' + error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Cargar Nuevo Documento</h1>
      
      {/* Mostrar mensajes de error o éxito */}
      {error && <Alert type="error" message={error} onClose={() => setError('')} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit}>
          {/* Componente de formulario con campos - sin selector de tipo de documento */}
          <DocumentForm 
            formData={formData} 
            handleChange={handleChange}
            categories={categories}
            documentTypes={documentTypes}
            disabled={loading}
            showDocumentTypeSelector={false}
          />
          
          {/* Componente para carga de archivos */}
          <div className="mt-6">
            <FileUploader 
              onFileSelected={handleFileChange}
              selectedFile={file}
              disabled={loading}
            />
          </div>
          
          {/* Barra de progreso */}
          {loading && (
            <div className="my-4">
              <ProgressBar progress={uploadProgress} />
              <p className="text-center text-sm text-gray-600 mt-2">
                Cargando documento... {uploadProgress}%
              </p>
            </div>
          )}
          
          {/* Botones de acción */}
          <div className="mt-6 flex justify-end">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="px-4 py-2 mr-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-blue-400"
              disabled={loading}
            >
              {loading ? 'Cargando...' : 'Cargar Documento'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UploadDocumentPage;
