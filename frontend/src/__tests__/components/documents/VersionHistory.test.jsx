import { render, screen, fireEvent } from '@testing-library/react';
import VersionHistory from '../../../components/documents/VersionHistory';
import { mockDocuments } from '../../mocks/data';

describe('VersionHistory Component', () => {
  const mockOnVersionSelect = jest.fn();
  const mockOnDownload = jest.fn();
  
  // Usar el documento con múltiples versiones de los mocks
  const documentWithVersions = mockDocuments[1];
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders version history correctly', () => {
    render(
      <VersionHistory 
        versions={documentWithVersions.versions} 
        onVersionSelect={mockOnVersionSelect}
        onDownload={mockOnDownload}
      />
    );
    
    // Verificar que se muestra el título
    expect(screen.getByText(/historial de versiones/i)).toBeInTheDocument();
    
    // Verificar que se muestran las versiones
    expect(screen.getByText(/versión 1/i)).toBeInTheDocument();
    expect(screen.getByText(/versión 2/i)).toBeInTheDocument();
    
    // Verificar que se muestran las fechas
    expect(screen.getAllByText(/20 feb 2025/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/10 mar 2025/i)[0]).toBeInTheDocument();
  });
  
  test('calls onVersionSelect when a version is clicked', () => {
    render(
      <VersionHistory 
        versions={documentWithVersions.versions} 
        onVersionSelect={mockOnVersionSelect}
        onDownload={mockOnDownload}
      />
    );
    
    // Hacer clic en la primera versión
    const versionItem = screen.getByText(/versión 1/i);
    fireEvent.click(versionItem);
    
    // Verificar que se llamó la función con la versión correcta
    expect(mockOnVersionSelect).toHaveBeenCalledWith(documentWithVersions.versions[0]);
  });
  
  test('calls onDownload when download button is clicked', () => {
    render(
      <VersionHistory 
        versions={documentWithVersions.versions} 
        onVersionSelect={mockOnVersionSelect}
        onDownload={mockOnDownload}
      />
    );
    
    // Hacer clic en el botón de descarga de la primera versión
    const downloadButtons = screen.getAllByRole('button', { name: /descargar/i });
    fireEvent.click(downloadButtons[0]);
    
    // Verificar que se llamó la función con la versión correcta
    expect(mockOnDownload).toHaveBeenCalledWith(documentWithVersions.versions[0]);
  });
  
  test('highlights current version', () => {
    render(
      <VersionHistory 
        versions={documentWithVersions.versions} 
        currentVersion={documentWithVersions.versions[1]}
        onVersionSelect={mockOnVersionSelect}
        onDownload={mockOnDownload}
      />
    );
    
    // Verificar que la versión actual está resaltada
    const currentVersionElement = screen.getByText(/versión 2/i).closest('li');
    expect(currentVersionElement).toHaveClass('bg-blue-50'); // Asumiendo que usas esta clase para resaltar
  });
  
  test('renders empty state when no versions are available', () => {
    render(
      <VersionHistory 
        versions={[]} 
        onVersionSelect={mockOnVersionSelect}
        onDownload={mockOnDownload}
      />
    );
    
    // Verificar que se muestra el mensaje de que no hay versiones
    expect(screen.getByText(/no hay versiones disponibles/i)).toBeInTheDocument();
  });
});
