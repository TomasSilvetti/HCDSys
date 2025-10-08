import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import status
from httpx import AsyncClient

from app.routes.users import router as users_router
from app.routes.roles import router as roles_router
from app.db.models import Usuario as User, Rol as Role, Permiso as Permission
from tests.mocks.db import create_mock_user, create_mock_role
from tests.mocks.auth import get_mock_current_user

@pytest.mark.unit
@pytest.mark.asyncio
class TestUsersRolesRoutes:
    @pytest.fixture
    def mock_db(self):
        """Fixture para crear un mock de la sesión de base de datos"""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        return db
    
    @patch("app.routes.users.get_current_user")
    async def test_get_all_users(self, mock_get_current_user, mock_db, async_client):
        """Prueba para obtener todos los usuarios"""
        # Configurar el mock del usuario actual (admin)
        mock_user = get_mock_current_user(role_name="admin")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos
        mock_users = [
            create_mock_user(id=1, email="admin@example.com", role_name="admin"),
            create_mock_user(id=2, email="gestor@example.com", role_name="gestor"),
            create_mock_user(id=3, email="usuario@example.com", role_name="usuario")
        ]
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock()
        mock_result.scalars.return_value.all = AsyncMock(return_value=mock_users)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Realizar la solicitud
        response = await app.get("/users")
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3
        assert response.json()[0]["email"] == "admin@example.com"
        assert response.json()[1]["email"] == "gestor@example.com"
        assert response.json()[2]["email"] == "usuario@example.com"
    
    @patch("app.routes.users.get_current_user")
    async def test_get_user_by_id(self, mock_get_current_user, mock_db, async_client):
        """Prueba para obtener un usuario por ID"""
        # Configurar el mock del usuario actual (admin)
        mock_user = get_mock_current_user(role_name="admin")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos
        mock_user_result = create_mock_user(id=1, email="test@example.com", role_name="usuario")
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=mock_user_result)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Realizar la solicitud
        response = await app.get("/users/1")
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == 1
        assert response.json()["email"] == "test@example.com"
    
    @patch("app.routes.users.get_current_user")
    async def test_update_user_role(self, mock_get_current_user, mock_db, async_client):
        """Prueba para actualizar el rol de un usuario"""
        # Configurar el mock del usuario actual (admin)
        mock_user = get_mock_current_user(role_name="admin")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos para el usuario
        mock_user_to_update = create_mock_user(id=2, email="user@example.com", role_name="usuario")
        
        # Configurar el mock de la base de datos para el rol
        mock_role = create_mock_role(id=2, name="gestor")
        
        # Configurar los resultados de las consultas
        def mock_execute_side_effect(query, *args, **kwargs):
            # Verificar el tipo de consulta para determinar qué resultado devolver
            if "SELECT" in str(query) and "users" in str(query) and "id" in str(query):
                mock_result_user = AsyncMock()
                mock_result_user.scalar_one_or_none = AsyncMock(return_value=mock_user_to_update)
                return mock_result_user
            elif "SELECT" in str(query) and "roles" in str(query) and "id" in str(query):
                mock_result_role = AsyncMock()
                mock_result_role.scalar_one_or_none = AsyncMock(return_value=mock_role)
                return mock_result_role
            return AsyncMock()
        
        mock_db.execute.side_effect = mock_execute_side_effect
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Datos para actualizar el rol
        update_data = {
            "role_id": 2
        }
        
        # Realizar la solicitud
        response = await app.put("/users/2/role", json=update_data)
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "user@example.com"
        assert response.json()["role"]["id"] == 2
        assert response.json()["role"]["name"] == "gestor"
        
        # Verificar que se llamó a la base de datos
        assert mock_db.commit.called
    
    @patch("app.routes.roles.get_current_user")
    async def test_get_all_roles(self, mock_get_current_user, mock_db, async_client):
        """Prueba para obtener todos los roles"""
        # Configurar el mock del usuario actual (admin)
        mock_user = get_mock_current_user(role_name="admin")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos
        mock_roles = [
            create_mock_role(id=1, name="admin"),
            create_mock_role(id=2, name="gestor"),
            create_mock_role(id=3, name="usuario")
        ]
        mock_result = AsyncMock()
        mock_result.scalars = AsyncMock()
        mock_result.scalars.return_value.all = AsyncMock(return_value=mock_roles)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Realizar la solicitud
        response = await app.get("/roles")
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3
        assert response.json()[0]["name"] == "admin"
        assert response.json()[1]["name"] == "gestor"
        assert response.json()[2]["name"] == "usuario"
    
    @patch("app.routes.roles.get_current_user")
    async def test_get_role_by_id(self, mock_get_current_user, mock_db, async_client):
        """Prueba para obtener un rol por ID"""
        # Configurar el mock del usuario actual (admin)
        mock_user = get_mock_current_user(role_name="admin")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos
        mock_role = create_mock_role(id=1, name="admin")
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=mock_role)
        mock_db.execute.return_value = mock_result
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Realizar la solicitud
        response = await app.get("/roles/1")
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == 1
        assert response.json()["name"] == "admin"
    
    @patch("app.routes.roles.get_current_user")
    async def test_create_role(self, mock_get_current_user, mock_db, async_client):
        """Prueba para crear un nuevo rol"""
        # Configurar el mock del usuario actual (admin)
        mock_user = get_mock_current_user(role_name="admin")
        mock_get_current_user.return_value = mock_user
        
        # Configurar el mock de la base de datos
        mock_db.add = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Configurar el endpoint
        app = AsyncClient(app=async_client.app)
        
        # Sobreescribir la dependencia de la base de datos
        app.app.dependency_overrides = {
            get_db: lambda: mock_db
        }
        
        # Datos para crear el rol
        role_data = {
            "name": "nuevo_rol",
            "description": "Descripción del nuevo rol"
        }
        
        # Realizar la solicitud
        response = await app.post("/roles", json=role_data)
        
        # Verificar la respuesta
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "nuevo_rol"
        assert response.json()["description"] == "Descripción del nuevo rol"
        
        # Verificar que se llamó a la base de datos
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
