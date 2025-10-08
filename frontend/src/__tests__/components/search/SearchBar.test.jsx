import { render, screen, fireEvent } from '@testing-library/react';
import SearchBar from '../../../components/search/SearchBar';

describe('SearchBar Component', () => {
  const mockOnSearch = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders search input and button', () => {
    render(<SearchBar onSearch={mockOnSearch} />);
    
    expect(screen.getByPlaceholderText(/buscar documentos/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /buscar/i })).toBeInTheDocument();
  });
  
  test('calls onSearch when form is submitted', () => {
    render(<SearchBar onSearch={mockOnSearch} />);
    
    const searchInput = screen.getByPlaceholderText(/buscar documentos/i);
    const searchButton = screen.getByRole('button', { name: /buscar/i });
    
    // Escribir en el campo de búsqueda
    fireEvent.change(searchInput, { target: { value: 'documento importante' } });
    
    // Enviar el formulario
    fireEvent.click(searchButton);
    
    expect(mockOnSearch).toHaveBeenCalledWith('documento importante');
  });
  
  test('calls onSearch when Enter key is pressed', () => {
    render(<SearchBar onSearch={mockOnSearch} />);
    
    const searchInput = screen.getByPlaceholderText(/buscar documentos/i);
    
    // Escribir en el campo de búsqueda
    fireEvent.change(searchInput, { target: { value: 'informe anual' } });
    
    // Presionar Enter
    fireEvent.keyPress(searchInput, { key: 'Enter', code: 13, charCode: 13 });
    
    expect(mockOnSearch).toHaveBeenCalledWith('informe anual');
  });
  
  test('does not call onSearch when form is submitted with empty query', () => {
    render(<SearchBar onSearch={mockOnSearch} />);
    
    const searchButton = screen.getByRole('button', { name: /buscar/i });
    
    // Enviar el formulario sin escribir nada
    fireEvent.click(searchButton);
    
    expect(mockOnSearch).not.toHaveBeenCalled();
  });
  
  test('renders with initial query value', () => {
    render(<SearchBar onSearch={mockOnSearch} initialQuery="documento inicial" />);
    
    const searchInput = screen.getByPlaceholderText(/buscar documentos/i);
    expect(searchInput.value).toBe('documento inicial');
  });
});
