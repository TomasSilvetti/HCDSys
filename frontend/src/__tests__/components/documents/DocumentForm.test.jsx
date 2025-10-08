import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DocumentForm from '../../../components/documents/DocumentForm';

describe('DocumentForm Component', () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();
  
  const defaultProps = {
    onSubmit: mockOnSubmit,
    onCancel: mockOnCancel,
    isLoading: false
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders empty form correctly', () => {
    render(<DocumentForm {...defaultProps} />);
    
    // Verificar que se muestran los campos del formulario
    expect(screen.getByLabelText(/título/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/descripción/i)).toBeInTheDocument();
    
    // Verificar que se muestran los botones
    expect(screen.getByRole('button', { name: /guardar/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancelar/i })).toBeInTheDocument();
  });
  
  test('renders form with initial values', () => {
    const initialValues = {
      title: 'Documento de Prueba',
      description: 'Esta es una descripción de prueba',
      tags: ['prueba', 'documento']
    };
    
    render(<DocumentForm {...defaultProps} initialValues={initialValues} />);
    
    // Verificar que los campos tienen los valores iniciales
    expect(screen.getByLabelText(/título/i).value).toBe('Documento de Prueba');
    expect(screen.getByLabelText(/descripción/i).value).toBe('Esta es una descripción de prueba');
  });
  
  test('calls onSubmit with form values when submitted', async () => {
    render(<DocumentForm {...defaultProps} />);
    
    // Completar el formulario
    const titleInput = screen.getByLabelText(/título/i);
    const descriptionInput = screen.getByLabelText(/descripción/i);
    
    fireEvent.change(titleInput, { target: { value: 'Nuevo Documento' } });
    fireEvent.change(descriptionInput, { target: { value: 'Nueva descripción' } });
    
    // Enviar el formulario
    const submitButton = screen.getByRole('button', { name: /guardar/i });
    fireEvent.click(submitButton);
    
    // Verificar que se llamó la función onSubmit con los valores correctos
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Nuevo Documento',
          description: 'Nueva descripción'
        })
      );
    });
  });
  
  test('calls onCancel when cancel button is clicked', () => {
    render(<DocumentForm {...defaultProps} />);
    
    // Hacer clic en el botón Cancelar
    const cancelButton = screen.getByRole('button', { name: /cancelar/i });
    fireEvent.click(cancelButton);
    
    // Verificar que se llamó la función onCancel
    expect(mockOnCancel).toHaveBeenCalled();
  });
  
  test('displays loading state when isLoading is true', () => {
    render(<DocumentForm {...defaultProps} isLoading={true} />);
    
    // Verificar que el botón de guardar está deshabilitado y muestra un indicador de carga
    const submitButton = screen.getByRole('button', { name: /guardando/i });
    expect(submitButton).toBeDisabled();
    expect(submitButton).toHaveTextContent(/guardando/i);
  });
  
  test('displays validation errors for empty required fields', async () => {
    render(<DocumentForm {...defaultProps} />);
    
    // Enviar el formulario sin completar campos
    const submitButton = screen.getByRole('button', { name: /guardar/i });
    fireEvent.click(submitButton);
    
    // Verificar que se muestran los mensajes de error
    await waitFor(() => {
      expect(screen.getByText(/el título es requerido/i)).toBeInTheDocument();
    });
  });
});
