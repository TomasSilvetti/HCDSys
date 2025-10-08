// Mock de datos para pruebas

// Usuarios de prueba
export const mockUsers = [
  {
    id: '1',
    email: 'admin@example.com',
    fullName: 'Admin User',
    role: {
      id: '1',
      name: 'admin',
      permissions: ['create:document', 'read:document', 'update:document', 'delete:document', 'manage:users']
    }
  },
  {
    id: '2',
    email: 'gestor@example.com',
    fullName: 'Gestor User',
    role: {
      id: '2',
      name: 'gestor',
      permissions: ['create:document', 'read:document', 'update:document', 'delete:document']
    }
  },
  {
    id: '3',
    email: 'usuario@example.com',
    fullName: 'Regular User',
    role: {
      id: '3',
      name: 'usuario',
      permissions: ['read:document']
    }
  }
];

// Documentos de prueba
export const mockDocuments = [
  {
    id: '1',
    title: 'Informe Anual 2025',
    description: 'Informe anual de actividades y resultados',
    fileType: 'pdf',
    createdAt: '2025-01-15T10:30:00Z',
    updatedAt: '2025-01-15T10:30:00Z',
    createdBy: {
      id: '1',
      fullName: 'Admin User'
    },
    tags: ['informe', 'anual', '2025'],
    versions: [
      {
        id: '1',
        versionNumber: 1,
        createdAt: '2025-01-15T10:30:00Z',
        createdBy: {
          id: '1',
          fullName: 'Admin User'
        }
      }
    ]
  },
  {
    id: '2',
    title: 'Manual de Procedimientos',
    description: 'Manual de procedimientos internos',
    fileType: 'docx',
    createdAt: '2025-02-20T14:45:00Z',
    updatedAt: '2025-03-10T09:15:00Z',
    createdBy: {
      id: '2',
      fullName: 'Gestor User'
    },
    tags: ['manual', 'procedimientos', 'interno'],
    versions: [
      {
        id: '2',
        versionNumber: 1,
        createdAt: '2025-02-20T14:45:00Z',
        createdBy: {
          id: '2',
          fullName: 'Gestor User'
        }
      },
      {
        id: '3',
        versionNumber: 2,
        createdAt: '2025-03-10T09:15:00Z',
        createdBy: {
          id: '2',
          fullName: 'Gestor User'
        }
      }
    ]
  },
  {
    id: '3',
    title: 'Plan Estratégico 2025-2030',
    description: 'Plan estratégico para los próximos 5 años',
    fileType: 'pptx',
    createdAt: '2025-04-05T11:20:00Z',
    updatedAt: '2025-04-05T11:20:00Z',
    createdBy: {
      id: '1',
      fullName: 'Admin User'
    },
    tags: ['plan', 'estrategia', '2025', '2030'],
    versions: [
      {
        id: '4',
        versionNumber: 1,
        createdAt: '2025-04-05T11:20:00Z',
        createdBy: {
          id: '1',
          fullName: 'Admin User'
        }
      }
    ]
  }
];

// Roles de prueba
export const mockRoles = [
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
];

// Permisos de prueba
export const mockPermissions = [
  { id: '1', name: 'create:document', description: 'Crear documentos' },
  { id: '2', name: 'read:document', description: 'Leer documentos' },
  { id: '3', name: 'update:document', description: 'Actualizar documentos' },
  { id: '4', name: 'delete:document', description: 'Eliminar documentos' },
  { id: '5', name: 'manage:users', description: 'Gestionar usuarios' }
];

// Resultados de búsqueda de prueba
export const mockSearchResults = {
  results: [
    {
      id: '1',
      title: 'Informe Anual 2025',
      description: 'Informe anual de actividades y resultados',
      fileType: 'pdf',
      createdAt: '2025-01-15T10:30:00Z',
      createdBy: {
        id: '1',
        fullName: 'Admin User'
      },
      tags: ['informe', 'anual', '2025']
    },
    {
      id: '3',
      title: 'Plan Estratégico 2025-2030',
      description: 'Plan estratégico para los próximos 5 años',
      fileType: 'pptx',
      createdAt: '2025-04-05T11:20:00Z',
      createdBy: {
        id: '1',
        fullName: 'Admin User'
      },
      tags: ['plan', 'estrategia', '2025', '2030']
    }
  ],
  total: 2,
  page: 1,
  limit: 10
};
