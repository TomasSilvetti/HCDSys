// Mock para api.js
const API_URL = 'http://localhost:8000/api';

// Mock de axios
const mockAxios = {
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
  patch: jest.fn(() => Promise.resolve({ data: {} })),
  interceptors: {
    request: { use: jest.fn(), eject: jest.fn() },
    response: { use: jest.fn(), eject: jest.fn() }
  },
  defaults: {
    baseURL: API_URL,
    headers: {
      common: {}
    }
  }
};

// Exportar el mock de axios como default y como create
mockAxios.create = jest.fn(() => mockAxios);
export default mockAxios;

// Función para manejar errores de API
function handleApiError(error) {
  let errorMessage = 'Ha ocurrido un error. Por favor, inténtelo de nuevo.';
  
  if (error.response) {
    const data = error.response.data;
    errorMessage = data.detail || data.message || errorMessage;
  } else if (error.request) {
    errorMessage = 'No se pudo conectar con el servidor. Verifique su conexión.';
  }
  
  return new Error(errorMessage);
}

// Función para parsear token JWT
function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error al parsear JWT:', error);
    return {};
  }
}

// Mock de servicios
export const authService = {
  login: jest.fn(() => Promise.resolve({ access_token: 'mock-token', user: { id: 1, email: 'test@example.com', role: { name: 'usuario' } } })),
  register: jest.fn(() => Promise.resolve({ id: 1, email: 'test@example.com' })),
  logout: jest.fn(),
  isAuthenticated: jest.fn(() => true),
  getCurrentUser: jest.fn(() => ({ id: 1, email: 'test@example.com', role: { name: 'usuario' } })),
  checkAuth: jest.fn(() => Promise.resolve({ user: { id: 1, email: 'test@example.com', role: { name: 'usuario' } } })),
  getUserProfile: jest.fn(() => Promise.resolve({ id: 1, email: 'test@example.com', role: { name: 'usuario' } }))
};

export const documentService = {
  getDocuments: jest.fn(() => Promise.resolve([])),
  getDocument: jest.fn(() => Promise.resolve({})),
  createDocument: jest.fn(() => Promise.resolve({})),
  updateDocument: jest.fn(() => Promise.resolve({})),
  deleteDocument: jest.fn(() => Promise.resolve({})),
  searchDocuments: jest.fn(() => Promise.resolve({ results: [], total: 0 })),
  getDocumentVersions: jest.fn(() => Promise.resolve([])),
  createDocumentVersion: jest.fn(() => Promise.resolve({})),
  restoreDocumentVersion: jest.fn(() => Promise.resolve({})),
  compareDocumentVersions: jest.fn(() => Promise.resolve({ diff: [] }))
};

export const userService = {
  getUsers: jest.fn(() => Promise.resolve([])),
  getUser: jest.fn(() => Promise.resolve({})),
  updateUser: jest.fn(() => Promise.resolve({})),
  deleteUser: jest.fn(() => Promise.resolve({})),
  updateUserRole: jest.fn(() => Promise.resolve({}))
};

export const roleService = {
  getRoles: jest.fn(() => Promise.resolve([])),
  getRole: jest.fn(() => Promise.resolve({})),
  createRole: jest.fn(() => Promise.resolve({})),
  updateRole: jest.fn(() => Promise.resolve({})),
  deleteRole: jest.fn(() => Promise.resolve({})),
  getRolePermissions: jest.fn(() => Promise.resolve([])),
  addRolePermission: jest.fn(() => Promise.resolve({})),
  removeRolePermission: jest.fn(() => Promise.resolve({}))
};

export const permissionService = {
  getPermissions: jest.fn(() => Promise.resolve([])),
  getPermission: jest.fn(() => Promise.resolve({})),
  createPermission: jest.fn(() => Promise.resolve({})),
  updatePermission: jest.fn(() => Promise.resolve({})),
  deletePermission: jest.fn(() => Promise.resolve({}))
};

export const documentTypeService = {
  getDocumentTypes: jest.fn(() => Promise.resolve([])),
  getDocumentType: jest.fn(() => Promise.resolve({})),
  createDocumentType: jest.fn(() => Promise.resolve({})),
  updateDocumentType: jest.fn(() => Promise.resolve({})),
  deleteDocumentType: jest.fn(() => Promise.resolve({}))
};

export const auditService = {
  getAuditLogs: jest.fn(() => Promise.resolve([])),
  getAuditLog: jest.fn(() => Promise.resolve({})),
  createAuditLog: jest.fn(() => Promise.resolve({}))
};

export const storageService = {
  uploadFile: jest.fn(() => Promise.resolve({ path: 'mock-path.pdf' })),
  downloadFile: jest.fn(() => Promise.resolve({ data: new Blob(['mock-file-content']) }))
};

export const searchService = {
  search: jest.fn(() => Promise.resolve({ results: [], total: 0 })),
  advancedSearch: jest.fn(() => Promise.resolve({ results: [], total: 0 }))
};