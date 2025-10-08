import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import status
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.routes.auth import router
from app.db.models import Usuario as User, Rol as Role
from app.utils.security import create_access_token, get_password_hash
from tests.mocks.db import create_mock_user, create_mock_role

@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthRoutes:
    @pytest.fixture
    def mock_db(self):
        """Fixture para crear un mock de la sesión de base de datos"""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        return db
    
    async def test_login_success(self, mock_db, async_client):
        """Prueba de inicio de sesión exitoso"""
        # Configurar el mock de la base de datos
        mock_user = create_mock_user(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            role_name="usuario"
        )
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=mock_user)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Datos de inicio de sesión
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        # Realizar la solicitud
        response = await app.post("/auth/login", json=login_data)
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
        assert response.json()["user"]["email"] == "test@example.com"
    
    async def test_login_invalid_credentials(self, mock_db, async_client):
        """Prueba de inicio de sesión con credenciales inválidas"""
        # Configurar el mock de la base de datos
        mock_user = create_mock_user(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            role_name="usuario"
        )
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=mock_user)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Datos de inicio de sesión incorrectos
        login_data = {
            "email": "test@example.com",
            "password": "wrong_password"
        }
        
        # Realizar la solicitud
        response = await app.post("/auth/login", json=login_data)
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()
        assert "credenciales" in response.json()["detail"].lower()
    
    async def test_login_user_not_found(self, mock_db, async_client):
        """Prueba de inicio de sesión con usuario no existente"""
        # Configurar el mock de la base de datos para devolver None (usuario no encontrado)
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Datos de inicio de sesión
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        # Realizar la solicitud
        response = await app.post("/auth/login", json=login_data)
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()
        assert "credenciales" in response.json()["detail"].lower()
    
    async def test_register_user(self, mock_db, async_client):
        """Prueba de registro de usuario"""
        # Configurar el mock para verificar que el email no existe
        mock_result_email_check = AsyncMock()
        mock_result_email_check.scalar_one_or_none = AsyncMock(return_value=None)
        
        # Configurar el mock para obtener el rol de usuario
        mock_role = create_mock_role(id=3, name="usuario")
        mock_result_role = AsyncMock()
        mock_result_role.scalar_one_or_none = AsyncMock(return_value=mock_role)
        
        # Configurar el mock de la base de datos para devolver diferentes resultados según la consulta
        def mock_execute_side_effect(query, *args, **kwargs):
            # Verificar el tipo de consulta para determinar qué resultado devolver
            if "SELECT" in str(query) and "users" in str(query) and "email" in str(query):
                return mock_result_email_check
            elif "SELECT" in str(query) and "roles" in str(query) and "name" in str(query):
                return mock_result_role
            return AsyncMock()
        
        mock_db.execute.side_effect = mock_execute_side_effect
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Datos de registro
        register_data = {
            "email": "new_user@example.com",
            "password": "password123",
            "full_name": "New User"
        }
        
        # Realizar la solicitud
        response = await app.post("/auth/register", json=register_data)
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == "new_user@example.com"
        assert response.json()["full_name"] == "New User"
        
        # Verificar que se llamó a la base de datos
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
    
    async def test_register_existing_email(self, mock_db, async_client):
        """Prueba de registro con un email ya existente"""
        # Configurar el mock para verificar que el email ya existe
        mock_user = create_mock_user(email="existing@example.com")
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=mock_user)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Datos de registro
        register_data = {
            "email": "existing@example.com",
            "password": "password123",
            "full_name": "Existing User"
        }
        
        # Realizar la solicitud
        response = await app.post("/auth/register", json=register_data)
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()
        assert "ya existe" in response.json()["detail"].lower()
