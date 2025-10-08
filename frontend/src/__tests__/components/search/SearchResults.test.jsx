import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import SearchResults from '../../../components/search/SearchResults';

// Mock de datos
const mockResults = [
  {
    id: '1',
    titulo: 'Informe Anual 2025',
    descripcion: 'Informe anual de actividades y resultados',
    tipo_documento: { nombre: 'pdf' },
    fecha_modificacion: '2025-01-15T10:30:00Z',
    numero_expediente: 'EXP-2025-001'
  },
  {
    id: '2',
    titulo: 'Plan Estratégico 2025-2030',
    descripcion: 'Plan estratégico para los próximos 5 años',
    tipo_documento: { nombre: 'pptx' },
    fecha_modificacion: '2025-04-05T11:20:00Z',
    numero_expediente: 'EXP-2025-003'
  }
];

// Mock de react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

describe('SearchResults Component', () => {
  test('renders loading state', () => {
    render(
      <BrowserRouter>
        <SearchResults 
          results={[]} 
          isLoading={true} 
          page={1} 
          totalPages={1} 
          totalItems={0}
          onPageChange={jest.fn()}
          onSort={jest.fn()}
        />
      </BrowserRouter>
    );
    
    // Verificar que se muestra el spinner de carga
    const loadingElement = screen.getByRole('status', { hidden: true });
    expect(loadingElement).toBeInTheDocument();
  });
  
  test('renders empty results message with query', () => {
    render(
      <BrowserRouter>
        <SearchResults 
          results={[]} 
          isLoading={false} 
          query="test"
          page={1} 
          totalPages={1} 
          totalItems={0}
          onPageChange={jest.fn()}
          onSort={jest.fn()}
        />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/No se encontraron resultados para "test"/i)).toBeInTheDocument();
  });
  
  test('renders empty results message without query', () => {
    render(
      <BrowserRouter>
        <SearchResults 
          results={[]} 
          isLoading={false} 
          page={1} 
          totalPages={1} 
          totalItems={0}
          onPageChange={jest.fn()}
          onSort={jest.fn()}
        />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/Ingrese un término de búsqueda para encontrar documentos/i)).toBeInTheDocument();
  });
  
  test('renders search results correctly', () => {
    render(
      <BrowserRouter>
        <SearchResults 
          results={mockResults} 
          isLoading={false} 
          page={1} 
          totalPages={1} 
          totalItems={2}
          onPageChange={jest.fn()}
          onSort={jest.fn()}
        />
      </BrowserRouter>
    );
    
    // Verificar que se muestran los títulos
    expect(screen.getByText('Informe Anual 2025')).toBeInTheDocument();
    expect(screen.getByText('Plan Estratégico 2025-2030')).toBeInTheDocument();
    
    // Verificar que se muestran los números de expediente
    expect(screen.getByText('EXP-2025-001')).toBeInTheDocument();
    expect(screen.getByText('EXP-2025-003')).toBeInTheDocument();
    
    // Verificar que se muestran los tipos de documento
    expect(screen.getByText('pdf')).toBeInTheDocument();
    expect(screen.getByText('pptx')).toBeInTheDocument();
  });
  
  test('calls navigate when a result is clicked', () => {
    const navigateMock = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockImplementation(() => navigateMock);
    
    render(
      <BrowserRouter>
        <SearchResults 
          results={mockResults} 
          isLoading={false} 
          page={1} 
          totalPages={1} 
          totalItems={2}
          onPageChange={jest.fn()}
          onSort={jest.fn()}
        />
      </BrowserRouter>
    );
    
    // Hacer clic en el botón "Ver detalles" del primer resultado
    const viewButtons = screen.getAllByText('Ver detalles');
    fireEvent.click(viewButtons[0]);
    
    // Verificar que se llamó a navigate con la ruta correcta
    expect(navigateMock).toHaveBeenCalledWith('/documentos/1');
  });
  
  test('renders pagination when total pages is greater than 1', () => {
    render(
      <BrowserRouter>
        <SearchResults 
          results={mockResults} 
          isLoading={false} 
          page={1}
          totalPages={3}
          totalItems={6}
          onPageChange={jest.fn()}
          onSort={jest.fn()}
        />
      </BrowserRouter>
    );
    
    // Verificar que se muestra la paginación
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('Siguiente')).toBeInTheDocument();
  });
  
  test('calls onSort when sort button is clicked', () => {
    const onSortMock = jest.fn();
    
    render(
      <BrowserRouter>
        <SearchResults 
          results={mockResults} 
          isLoading={false} 
          page={1} 
          totalPages={1} 
          totalItems={2}
          onPageChange={jest.fn()}
          onSort={onSortMock}
        />
      </BrowserRouter>
    );
    
    // Hacer clic en el botón de ordenar por título
    fireEvent.click(screen.getByText('Título'));
    
    // Verificar que se llamó a onSort con los parámetros correctos
    expect(onSortMock).toHaveBeenCalledWith('titulo', 'asc');
  });
});