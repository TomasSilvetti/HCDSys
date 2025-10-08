import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiSave, FiAlertTriangle } from 'react-icons/fi';
import { documentService } from '../../utils/documentService';
import { useAuth } from '../../context/AuthContext';
import DocumentForm from '../../components/documents/DocumentForm';
import Alert from '../../components/ui/Alert';

const EditDocumentPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  
  // Estado para el formulario
  const [formData, setFormData] = useState({
    titulo: '',
    numero_expediente: '',
    descripcion: '',
    categoria_id: '',
    tipo_documento_id: '',
  });
  
  // Estado para las opciones de los selectores
  const [categories, setCategories] = useState([]);
  const [documentTypes, setDocumentTypes] = useState([]);
  
  // Estados para manejo de carga y errores
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Estado para cambios no guardados
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  
  // Cargar datos del documento y opciones al montar el componente
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Cargar datos del documento, categorías y tipos de documentos en paralelo
        const [documentData, categoriesData, typesData] = await Promise.all([
          documentService.getDocument(id),
          documentService.getCategories(),
          documentService.getDocumentTypes()
        ]);
        
        // Verificar permisos
        const isOwner = documentData.usuario_id === currentUser?.id;
        const hasEditPermission = currentUser?.permissions?.includes('DOCUMENT_EDIT');
        
        if (!isOwner && !hasEditPermission) {
          navigate('/acceso-denegado');
          return;
        }
        
        // Establecer datos del formulario
        setFormData({
          titulo: documentData.titulo || '',
          numero_expediente: documentData.numero_expediente || '',
          descripcion: documentData.descripcion || '',
          categoria_id: documentData.categoria_id || '',
          tipo_documento_id: documentData.tipo_documento_id || '',
        });
        
        setCategories(categoriesData);
        setDocumentTypes(typesData);
        
      } catch (error) {
        console.error('Error al cargar datos:', error);
        setError('Error al cargar los datos del documento: ' + error.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [id, currentUser, navigate]);
  
  // Manejar cambios en los campos del formulario
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setHasUnsavedChanges(true);
  };
  
  // Manejar envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validar campos obligatorios
    if (!formData.titulo || !formData.numero_expediente || !formData.tipo_documento_id) {
      setError('Por favor complete todos los campos obligatorios');
      return;
    }
    
    try {
      setSaving(true);
      
      // Actualizar documento en el backend
      await documentService.updateDocument(id, formData);
      
      setSuccess('Documento actualizado correctamente');
      setHasUnsavedChanges(false);
      
      // Redirigir a la vista de detalle después de un breve retraso
      setTimeout(() => {
        navigate(`/documentos/${id}`);
      }, 1500);
      
    } catch (error) {
      console.error('Error al actualizar documento:', error);
      setError('Error al actualizar el documento: ' + error.message);
    } finally {
      setSaving(false);
    }
  };
  
  // Manejar cancelación de edición
  const handleCancel = () => {
    if (hasUnsavedChanges) {
      setShowConfirmDialog(true);
    } else {
      navigate(`/documentos/${id}`);
    }
  };
  
  // Confirmar cancelación y descartar cambios
  const confirmCancel = () => {
    setShowConfirmDialog(false);
    navigate(`/documentos/${id}`);
  };
  
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <button 
          onClick={handleCancel}
          className="flex items-center text-gray-600 hover:text-gray-900"
        >
          <FiArrowLeft className="mr-2" /> Volver al documento
        </button>
        <h1 className="text-2xl font-bold">Editar Documento</h1>
      </div>
      
      {/* Mostrar mensajes de error o éxito */}
      {error && <Alert type="error" message={error} onClose={() => setError('')} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit}>
          {/* Componente de formulario con campos */}
          <DocumentForm 
            formData={formData} 
            handleChange={handleChange}
            categories={categories}
            documentTypes={documentTypes}
            disabled={saving}
          />
          
          {/* Botones de acción */}
          <div className="mt-6 flex justify-end space-x-4">
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              disabled={saving}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 flex items-center"
              disabled={saving}
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
                  Guardando...
                </>
              ) : (
                <>
                  <FiSave className="mr-2" />
                  Guardar Cambios
                </>
              )}
            </button>
          </div>
        </form>
      </div>
      
      {/* Diálogo de confirmación para cambios no guardados */}
      {showConfirmDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
            <div className="flex items-center text-amber-500 mb-4">
              <FiAlertTriangle className="h-6 w-6 mr-2" />
              <h3 className="text-lg font-medium">¿Descartar cambios?</h3>
            </div>
            <p className="mb-4 text-gray-600">
              Tiene cambios no guardados. ¿Está seguro de que desea salir sin guardar?
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowConfirmDialog(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Continuar editando
              </button>
              <button
                onClick={confirmCancel}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Descartar cambios
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EditDocumentPage;
