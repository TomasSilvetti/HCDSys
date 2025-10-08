"""
Mocks para la base de datos y modelos
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Usuario as User, Rol as Role, Permiso as Permission, Documento as Document, VersionDocumento as DocumentVersion, HistorialAcceso as DocumentHistory

# Mock para la sesión de base de datos
class MockDBSession:
    def __init__(self):
        self.add = AsyncMock()
        self.add_all = AsyncMock()
        self.commit = AsyncMock()
        self.refresh = AsyncMock()
        self.delete = AsyncMock()
        self.execute = AsyncMock()
        self.close = AsyncMock()
        self.rollback = AsyncMock()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

# Función para crear un mock de AsyncSession
def create_mock_session() -> AsyncSession:
    session = AsyncMock(spec=AsyncSession)
    session.add = AsyncMock()
    session.add_all = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.execute = AsyncMock()
    session.close = AsyncMock()
    session.rollback = AsyncMock()
    return session

# Datos mock para pruebas
class MockData:
    @staticmethod
    def get_mock_users() -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "email": "admin@example.com",
                "hashed_password": "hashed_adminpassword",
                "full_name": "Admin User",
                "role_id": 1,
                "is_active": True,
                "created_at": datetime.now() - timedelta(days=30)
            },
            {
                "id": 2,
                "email": "gestor@example.com",
                "hashed_password": "hashed_gestorpassword",
                "full_name": "Gestor User",
                "role_id": 2,
                "is_active": True,
                "created_at": datetime.now() - timedelta(days=20)
            },
            {
                "id": 3,
                "email": "usuario@example.com",
                "hashed_password": "hashed_userpassword",
                "full_name": "Regular User",
                "role_id": 3,
                "is_active": True,
                "created_at": datetime.now() - timedelta(days=10)
            }
        ]
    
    @staticmethod
    def get_mock_roles() -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "name": "admin",
                "description": "Administrador del sistema"
            },
            {
                "id": 2,
                "name": "gestor",
                "description": "Gestor de documentos"
            },
            {
                "id": 3,
                "name": "usuario",
                "description": "Usuario regular"
            }
        ]
    
    @staticmethod
    def get_mock_permissions() -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "name": "create:document",
                "description": "Crear documentos"
            },
            {
                "id": 2,
                "name": "read:document",
                "description": "Leer documentos"
            },
            {
                "id": 3,
                "name": "update:document",
                "description": "Actualizar documentos"
            },
            {
                "id": 4,
                "name": "delete:document",
                "description": "Eliminar documentos"
            },
            {
                "id": 5,
                "name": "manage:users",
                "description": "Gestionar usuarios"
            }
        ]
    
    @staticmethod
    def get_mock_documents() -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "title": "Informe Anual 2025",
                "description": "Informe anual de actividades y resultados",
                "file_path": "documents/informe_anual_2025.pdf",
                "file_type": "pdf",
                "created_by": 1,
                "created_at": datetime.now() - timedelta(days=15),
                "updated_at": datetime.now() - timedelta(days=15)
            },
            {
                "id": 2,
                "title": "Manual de Procedimientos",
                "description": "Manual de procedimientos internos",
                "file_path": "documents/manual_procedimientos.docx",
                "file_type": "docx",
                "created_by": 2,
                "created_at": datetime.now() - timedelta(days=10),
                "updated_at": datetime.now() - timedelta(days=5)
            }
        ]

    @staticmethod
    def get_mock_document_versions() -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "document_id": 1,
                "version_number": 1,
                "file_path": "documents/versions/informe_anual_2025_v1.pdf",
                "created_by": 1,
                "created_at": datetime.now() - timedelta(days=15)
            },
            {
                "id": 2,
                "document_id": 2,
                "version_number": 1,
                "file_path": "documents/versions/manual_procedimientos_v1.docx",
                "created_by": 2,
                "created_at": datetime.now() - timedelta(days=10)
            },
            {
                "id": 3,
                "document_id": 2,
                "version_number": 2,
                "file_path": "documents/versions/manual_procedimientos_v2.docx",
                "created_by": 2,
                "created_at": datetime.now() - timedelta(days=5)
            }
        ]

# Funciones para crear objetos mock
def create_mock_user(
    id: int = 1,
    email: str = "test@example.com",
    hashed_password: str = "hashed_password",
    full_name: str = "Test User",
    role_id: int = 3,
    is_active: bool = True
) -> User:
    user = MagicMock(spec=User)
    user.id = id
    user.email = email
    user.hashed_password = hashed_password
    user.full_name = full_name
    user.role_id = role_id
    user.is_active = is_active
    user.created_at = datetime.now()
    return user

def create_mock_role(
    id: int = 1,
    name: str = "usuario",
    description: str = "Usuario regular"
) -> Role:
    role = MagicMock(spec=Role)
    role.id = id
    role.name = name
    role.description = description
    return role

def create_mock_document(
    id: int = 1,
    title: str = "Test Document",
    description: str = "Test Description",
    file_path: str = "documents/test.pdf",
    file_type: str = "pdf",
    created_by: int = 1
) -> Document:
    document = MagicMock(spec=Document)
    document.id = id
    document.title = title
    document.description = description
    document.file_path = file_path
    document.file_type = file_type
    document.created_by = created_by
    document.created_at = datetime.now()
    document.updated_at = datetime.now()
    return document
