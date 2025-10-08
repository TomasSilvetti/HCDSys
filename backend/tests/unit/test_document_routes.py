import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import status
from httpx import AsyncClient

from app.routes.documents import router
from app.db.models import Documento as Document, Usuario as User, Rol as Role
from tests.mocks.db import create_mock_document, create_mock_user
from tests.mocks.auth import get_mock_current_user

@pytest.mark.unit
@pytest.mark.asyncio
class TestDocumentRoutes:
    @pytest.fixture
    def mock_db(self):
        """Fixture para crear un mock de la sesión de base de datos"""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        return db
    
    @pytest.fixture
    def mock_storage(self):
        """Fixture para crear un mock del servicio de almacenamiento"""
        storage = AsyncMock()
        storage.save_file = AsyncMock(return_value="documents/test.pdf")
        storage.get_file = AsyncMock(return_value=b"test file content")
        return storage
    
    @patch("app.routes.documents.get_current_user")
    async def test_get_all_documents(self, mock_get_current_user, mock_db, async_client):
        """Prueba para obtener todos los documentos"""
        # Configurar el mock del usuario actual
        mock_user = create_mock_user(role_name="usuario")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos
        mock_documents = [
            create_mock_document(id=1, title="Documento 1"),
            create_mock_document(id=2, title="Documento 2")
        ]
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock()
        mock_result.scalars.return_value.all = AsyncMock(return_value=mock_documents)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Realizar la solicitud
        response = await app.get("/documents")
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2
        assert response.json()[0]["title"] == "Documento 1"
        assert response.json()[1]["title"] == "Documento 2"
    
    @patch("app.routes.documents.get_current_user")
    async def test_get_document_by_id(self, mock_get_current_user, mock_db, async_client):
        """Prueba para obtener un documento por ID"""
        # Configurar el mock del usuario actual
        mock_user = create_mock_user(role_name="usuario")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos
        mock_document = create_mock_document(id=1, title="Documento 1")
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=mock_document)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Realizar la solicitud
        response = await app.get("/documents/1")
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == 1
        assert response.json()["title"] == "Documento 1"
    
    @patch("app.routes.documents.get_current_user")
    async def test_create_document(self, mock_get_current_user, mock_db, mock_storage, async_client):
        """Prueba para crear un nuevo documento"""
        # Configurar el mock del usuario actual
        mock_user = create_mock_user(id=1, role_name="gestor")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos
        mock_db.add = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir las dependencias
        app.app.dependency_overrides = {
            get_db: lambda: mock_db,
            get_storage_service: lambda: mock_storage
        }
        
        # Datos para crear el documento
        document_data = {
            "title": "Nuevo Documento",
            "description": "Descripción del nuevo documento",
            "file_type": "pdf"
        }
        
        # Realizar la solicitud
        response = await app.post("/documents", json=document_data)
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["title"] == "Nuevo Documento"
        assert response.json()["description"] == "Descripción del nuevo documento"
        
        # Verificar que se llamó a la base de datos
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
    
    @patch("app.routes.documents.get_current_user")
    async def test_update_document(self, mock_get_current_user, mock_db, async_client):
        """Prueba para actualizar un documento existente"""
        # Configurar el mock del usuario actual
        mock_user = create_mock_user(id=1, role_name="gestor")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos
        mock_document = create_mock_document(id=1, title="Documento Original", created_by=1)
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=mock_document)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Datos para actualizar el documento
        update_data = {
            "title": "Documento Actualizado",
            "description": "Descripción actualizada"
        }
        
        # Realizar la solicitud
        response = await app.put("/documents/1", json=update_data)
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "Documento Actualizado"
        assert response.json()["description"] == "Descripción actualizada"
        
        # Verificar que se llamó a la base de datos
        assert mock_db.commit.called
    
    @patch("app.routes.documents.get_current_user")
    async def test_delete_document(self, mock_get_current_user, mock_db, mock_storage, async_client):
        """Prueba para eliminar un documento"""
        # Configurar el mock del usuario actual
        mock_user = create_mock_user(id=1, role_name="gestor")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos
        mock_document = create_mock_document(id=1, title="Documento a Eliminar", created_by=1)
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=mock_document)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir las dependencias
        app.app.dependency_overrides = {
            get_db: lambda: mock_db,
            get_storage_service: lambda: mock_storage
        }
        
        # Realizar la solicitud
        response = await app.delete("/documents/1")
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Documento eliminado correctamente"
        
        # Verificar que se llamó a la base de datos
        assert mock_db.delete.called
        assert mock_db.commit.called
        
        # Verificar que se eliminó el archivo
        assert mock_storage.delete_file.called
