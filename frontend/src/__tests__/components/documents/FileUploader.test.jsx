import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FileUploader from '../../../components/documents/FileUploader';

// Mock para el evento de arrastrar y soltar
const createFileDropEvent = (files) => {
  return {
    preventDefault: jest.fn(),
    stopPropagation: jest.fn(),
    dataTransfer: {
      files,
      items: files.map(file => ({
        kind: 'file',
        type: file.type,
        getAsFile: () => file
      })),
      types: ['Files']
    }
  };
};

describe('FileUploader Component', () => {
  const mockOnFileSelect = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders uploader in initial state', () => {
    render(<FileUploader onFileSelect={mockOnFileSelect} />);
    
    // Verificar que se muestra el área de arrastrar y soltar
    expect(screen.getByText(/arrastra y suelta/i)).toBeInTheDocument();
    expect(screen.getByText(/o haz clic para seleccionar/i)).toBeInTheDocument();
  });
  
  test('handles file selection via input', async () => {
    render(<FileUploader onFileSelect={mockOnFileSelect} />);
    
    // Crear un archivo de prueba
    const file = new File(['contenido de prueba'], 'test.pdf', { type: 'application/pdf' });
    
    // Simular la selección de archivo
    const input = screen.getByLabelText(/seleccionar archivo/i);
    Object.defineProperty(input, 'files', {
      value: [file]
    });
    
    fireEvent.change(input);
    
    // Verificar que se llamó la función onFileSelect con el archivo correcto
    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(file);
    });
  });
  
  test('handles drag and drop file upload', async () => {
    render(<FileUploader onFileSelect={mockOnFileSelect} />);
    
    // Crear un archivo de prueba
    const file = new File(['contenido de prueba'], 'test.pdf', { type: 'application/pdf' });
    
    // Simular el evento de arrastrar y soltar
    const dropZone = screen.getByTestId('drop-zone');
    
    // Simular dragover
    fireEvent.dragOver(dropZone, createFileDropEvent([file]));
    
    // Verificar que se muestra el estado de "soltar para cargar"
    expect(screen.getByText(/suelta para cargar/i)).toBeInTheDocument();
    
    // Simular drop
    fireEvent.drop(dropZone, createFileDropEvent([file]));
    
    // Verificar que se llamó la función onFileSelect con el archivo correcto
    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(file);
    });
  });
  
  test('shows error message for invalid file type', async () => {
    render(<FileUploader onFileSelect={mockOnFileSelect} acceptedFileTypes={['.pdf', '.docx']} />);
    
    // Crear un archivo de tipo no aceptado
    const file = new File(['contenido de prueba'], 'test.jpg', { type: 'image/jpeg' });
    
    // Simular la selección de archivo
    const input = screen.getByLabelText(/seleccionar archivo/i);
    Object.defineProperty(input, 'files', {
      value: [file]
    });
    
    fireEvent.change(input);
    
    // Verificar que se muestra el mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/tipo de archivo no válido/i)).toBeInTheDocument();
    });
    
    // Verificar que no se llamó la función onFileSelect
    expect(mockOnFileSelect).not.toHaveBeenCalled();
  });
  
  test('shows error message for file size exceeding limit', async () => {
    render(<FileUploader onFileSelect={mockOnFileSelect} maxSizeMB={1} />);
    
    // Crear un archivo grande (2MB)
    const largeFile = new File([new ArrayBuffer(2 * 1024 * 1024)], 'large.pdf', { type: 'application/pdf' });
    
    // Simular la selección de archivo
    const input = screen.getByLabelText(/seleccionar archivo/i);
    Object.defineProperty(input, 'files', {
      value: [largeFile]
    });
    
    fireEvent.change(input);
    
    // Verificar que se muestra el mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/archivo demasiado grande/i)).toBeInTheDocument();
    });
    
    // Verificar que no se llamó la función onFileSelect
    expect(mockOnFileSelect).not.toHaveBeenCalled();
  });
});
