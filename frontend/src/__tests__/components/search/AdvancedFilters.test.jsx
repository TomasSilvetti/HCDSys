import { render, screen, fireEvent } from '@testing-library/react';
import AdvancedFilters from '../../../components/search/AdvancedFilters';

describe('AdvancedFilters Component', () => {
  const mockOnApplyFilters = jest.fn();
  const mockOnClearFilters = jest.fn();
  
  const defaultProps = {
    onApplyFilters: mockOnApplyFilters,
    onClearFilters: mockOnClearFilters,
    initialFilters: {}
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders filter options correctly', () => {
    render(<AdvancedFilters {...defaultProps} />);
    
    // Verificar que se muestran las opciones de filtro
    expect(screen.getByText(/tipo de documento/i)).toBeInTheDocument();
    expect(screen.getByText(/fecha de creación/i)).toBeInTheDocument();
    expect(screen.getByText(/creado por/i)).toBeInTheDocument();
    
    // Verificar que se muestran los botones de acción
    expect(screen.getByRole('button', { name: /aplicar filtros/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /limpiar filtros/i })).toBeInTheDocument();
  });
  
  test('calls onApplyFilters with selected filters when Apply button is clicked', () => {
    render(<AdvancedFilters {...defaultProps} />);
    
    // Seleccionar un tipo de documento
    const pdfCheckbox = screen.getByLabelText(/pdf/i);
    fireEvent.click(pdfCheckbox);
    
    // Hacer clic en el botón Aplicar
    const applyButton = screen.getByRole('button', { name: /aplicar filtros/i });
    fireEvent.click(applyButton);
    
    // Verificar que se llamó la función con los filtros correctos
    expect(mockOnApplyFilters).toHaveBeenCalledWith(
      expect.objectContaining({
        fileTypes: ['pdf']
      })
    );
  });
  
  test('calls onClearFilters when Clear button is clicked', () => {
    render(<AdvancedFilters {...defaultProps} />);
    
    // Seleccionar un tipo de documento
    const pdfCheckbox = screen.getByLabelText(/pdf/i);
    fireEvent.click(pdfCheckbox);
    
    // Hacer clic en el botón Limpiar
    const clearButton = screen.getByRole('button', { name: /limpiar filtros/i });
    fireEvent.click(clearButton);
    
    // Verificar que se llamó la función
    expect(mockOnClearFilters).toHaveBeenCalled();
  });
  
  test('renders with initial filters', () => {
    const initialFilters = {
      fileTypes: ['pdf', 'docx'],
      dateRange: {
        startDate: '2025-01-01',
        endDate: '2025-12-31'
      },
      createdBy: '1'
    };
    
    render(<AdvancedFilters {...defaultProps} initialFilters={initialFilters} />);
    
    // Verificar que los checkboxes están marcados
    expect(screen.getByLabelText(/pdf/i)).toBeChecked();
    expect(screen.getByLabelText(/docx/i)).toBeChecked();
    
    // Verificar que las fechas están establecidas
    const startDateInput = screen.getByLabelText(/fecha inicial/i);
    const endDateInput = screen.getByLabelText(/fecha final/i);
    expect(startDateInput.value).toBe('2025-01-01');
    expect(endDateInput.value).toBe('2025-12-31');
  });
  
  test('updates filters when user interacts with controls', () => {
    render(<AdvancedFilters {...defaultProps} />);
    
    // Seleccionar tipos de documento
    const pdfCheckbox = screen.getByLabelText(/pdf/i);
    const docxCheckbox = screen.getByLabelText(/docx/i);
    
    fireEvent.click(pdfCheckbox);
    fireEvent.click(docxCheckbox);
    
    // Establecer fechas
    const startDateInput = screen.getByLabelText(/fecha inicial/i);
    const endDateInput = screen.getByLabelText(/fecha final/i);
    
    fireEvent.change(startDateInput, { target: { value: '2025-03-01' } });
    fireEvent.change(endDateInput, { target: { value: '2025-03-31' } });
    
    // Hacer clic en el botón Aplicar
    const applyButton = screen.getByRole('button', { name: /aplicar filtros/i });
    fireEvent.click(applyButton);
    
    // Verificar que se llamó la función con los filtros correctos
    expect(mockOnApplyFilters).toHaveBeenCalledWith(
      expect.objectContaining({
        fileTypes: ['pdf', 'docx'],
        dateRange: {
          startDate: '2025-03-01',
          endDate: '2025-03-31'
        }
      })
    );
  });
});
