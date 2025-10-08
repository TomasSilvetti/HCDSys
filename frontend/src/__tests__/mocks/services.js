// Mocks para servicios API

// Mock para el servicio de autenticación
export const authServiceMock = {
  login: jest.fn().mockResolvedValue({
    token: 'fake-token',
    user: {
      id: '1',
      email: 'test@example.com',
      fullName: 'Test User',
      role: {
        id: '1',
        name: 'usuario',
        permissions: ['read:document']
      }
    }
  }),
  register: jest.fn().mockResolvedValue({
    id: '1',
    email: 'test@example.com',
    fullName: 'Test User'
  }),
  logout: jest.fn(),
  getCurrentUser: jest.fn().mockResolvedValue({
    id: '1',
    email: 'test@example.com',
    fullName: 'Test User',
    role: {
      id: '1',
      name: 'usuario',
      permissions: ['read:document']
    }
  })
};

// Mock para el servicio de documentos
export const documentServiceMock = {
  getAllDocuments: jest.fn().mockResolvedValue([
    {
      id: '1',
      title: 'Documento 1',
      description: 'Descripción del documento 1',
      fileType: 'pdf',
      createdAt: '2025-10-01T12:00:00Z',
      createdBy: {
        id: '1',
        fullName: 'Test User'
      }
    },
    {
      id: '2',
      title: 'Documento 2',
      description: 'Descripción del documento 2',
      fileType: 'docx',
      createdAt: '2025-10-02T14:30:00Z',
      createdBy: {
        id: '2',
        fullName: 'Another User'
      }
    }
  ]),
  getDocumentById: jest.fn().mockResolvedValue({
    id: '1',
    title: 'Documento 1',
    description: 'Descripción del documento 1',
    fileType: 'pdf',
    content: 'Contenido del documento',
    createdAt: '2025-10-01T12:00:00Z',
    updatedAt: '2025-10-01T12:00:00Z',
    createdBy: {
      id: '1',
      fullName: 'Test User'
    },
    versions: [
      {
        id: '1',
        versionNumber: 1,
        createdAt: '2025-10-01T12:00:00Z',
        createdBy: {
          id: '1',
          fullName: 'Test User'
        }
      }
    ]
  }),
  createDocument: jest.fn().mockResolvedValue({
    id: '3',
    title: 'Nuevo Documento',
    description: 'Descripción del nuevo documento',
    fileType: 'pdf',
    createdAt: '2025-10-03T09:15:00Z'
  }),
  updateDocument: jest.fn().mockResolvedValue({
    id: '1',
    title: 'Documento Actualizado',
    description: 'Descripción actualizada',
    fileType: 'pdf',
    updatedAt: '2025-10-03T10:20:00Z'
  }),
  deleteDocument: jest.fn().mockResolvedValue({ success: true }),
  searchDocuments: jest.fn().mockResolvedValue({
    results: [
      {
        id: '1',
        title: 'Documento 1',
        description: 'Descripción del documento 1',
        fileType: 'pdf',
        createdAt: '2025-10-01T12:00:00Z'
      }
    ],
    total: 1,
    page: 1,
    limit: 10
  })
};

// Mock para el servicio de usuarios
export const userServiceMock = {
  getAllUsers: jest.fn().mockResolvedValue([
    {
      id: '1',
      email: 'user1@example.com',
      fullName: 'User One',
      role: {
        id: '1',
        name: 'usuario'
      }
    },
    {
      id: '2',
      email: 'admin@example.com',
      fullName: 'Admin User',
      role: {
        id: '2',
        name: 'admin'
      }
    }
  ]),
  getUserById: jest.fn().mockResolvedValue({
    id: '1',
    email: 'user1@example.com',
    fullName: 'User One',
    role: {
      id: '1',
      name: 'usuario'
    },
    createdAt: '2025-09-15T10:00:00Z'
  }),
  updateUserRole: jest.fn().mockResolvedValue({
    id: '1',
    email: 'user1@example.com',
    role: {
      id: '2',
      name: 'gestor'
    }
  })
};

// Mock para el servicio de roles y permisos
export const roleServiceMock = {
  getAllRoles: jest.fn().mockResolvedValue([
    {
      id: '1',
      name: 'admin',
      description: 'Administrador del sistema',
      permissions: ['create:document', 'read:document', 'update:document', 'delete:document', 'manage:users']
    },
    {
      id: '2',
      name: 'gestor',
      description: 'Gestor de documentos',
      permissions: ['create:document', 'read:document', 'update:document', 'delete:document']
    },
    {
      id: '3',
      name: 'usuario',
      description: 'Usuario regular',
      permissions: ['read:document']
    }
  ]),
  getRoleById: jest.fn().mockResolvedValue({
    id: '1',
    name: 'admin',
    description: 'Administrador del sistema',
    permissions: ['create:document', 'read:document', 'update:document', 'delete:document', 'manage:users']
  })
};
