import PropTypes from 'prop-types';

const DocumentForm = ({ formData, handleChange, categories, documentTypes, disabled }) => {
  return (
    <div className="space-y-4">
      {/* Campo de título */}
      <div>
        <label htmlFor="titulo" className="block text-sm font-medium text-gray-700 mb-1">
          Título del documento <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="titulo"
          name="titulo"
          value={formData.titulo}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ingrese el título del documento"
          disabled={disabled}
          required
        />
      </div>
      
      {/* Campo de número de expediente */}
      <div>
        <label htmlFor="numero_expediente" className="block text-sm font-medium text-gray-700 mb-1">
          Número de expediente <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="numero_expediente"
          name="numero_expediente"
          value={formData.numero_expediente}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ej: EXP-2023-12345"
          disabled={disabled}
          required
        />
      </div>
      
      {/* Campo de descripción */}
      <div>
        <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700 mb-1">
          Descripción
        </label>
        <textarea
          id="descripcion"
          name="descripcion"
          value={formData.descripcion}
          onChange={handleChange}
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ingrese una descripción del documento"
          disabled={disabled}
        />
      </div>
      
      {/* Selector de categoría */}
      <div>
        <label htmlFor="categoria_id" className="block text-sm font-medium text-gray-700 mb-1">
          Categoría
        </label>
        <select
          id="categoria_id"
          name="categoria_id"
          value={formData.categoria_id}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={disabled}
        >
          <option value="">Seleccione una categoría</option>
          {categories.map(category => (
            <option key={category.id} value={category.id}>
              {category.nombre}
            </option>
          ))}
        </select>
      </div>
      
      {/* Selector de tipo de documento */}
      <div>
        <label htmlFor="tipo_documento_id" className="block text-sm font-medium text-gray-700 mb-1">
          Tipo de documento <span className="text-red-500">*</span>
        </label>
        <select
          id="tipo_documento_id"
          name="tipo_documento_id"
          value={formData.tipo_documento_id}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={disabled}
          required
        >
          <option value="">Seleccione un tipo de documento</option>
          {documentTypes.map(type => (
            <option key={type.id} value={type.id}>
              {type.nombre} ({type.extensiones_permitidas})
            </option>
          ))}
        </select>
        <p className="text-sm text-gray-500 mt-1">
          El tipo de documento determina qué formatos de archivo están permitidos.
        </p>
      </div>
    </div>
  );
};

DocumentForm.propTypes = {
  formData: PropTypes.shape({
    titulo: PropTypes.string.isRequired,
    numero_expediente: PropTypes.string.isRequired,
    descripcion: PropTypes.string,
    categoria_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    tipo_documento_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
  }).isRequired,
  handleChange: PropTypes.func.isRequired,
  categories: PropTypes.array.isRequired,
  documentTypes: PropTypes.array.isRequired,
  disabled: PropTypes.bool
};

DocumentForm.defaultProps = {
  disabled: false,
  categories: [],
  documentTypes: []
};

export default DocumentForm;
