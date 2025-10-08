import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.utils.security import get_password_hash

@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthRoutes:
    async def test_login_success(self, async_client: AsyncClient, test_users: dict):
        """Prueba de inicio de sesión exitoso"""
        response = await async_client.post(
            "/auth/login",
            json={
                "email": "usuario@example.com",
                "password": "userpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "usuario@example.com"
    
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Prueba de inicio de sesión con credenciales inválidas"""
        response = await async_client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "credenciales" in data["detail"].lower()
    
    async def test_register_user(self, async_client: AsyncClient, db_session: AsyncSession, test_roles: dict):
        """Prueba de registro de usuario"""
        response = await async_client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "newuserpassword",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        
        # Verificar que el usuario fue creado en la base de datos
        user_query = await db_session.get(User, data["id"])
        assert user_query is not None
        assert user_query.email == "newuser@example.com"
        
    async def test_register_existing_email(self, async_client: AsyncClient, test_users: dict):
        """Prueba de registro con un email ya existente"""
        response = await async_client.post(
            "/auth/register",
            json={
                "email": "usuario@example.com",  # Email ya existente
                "password": "newpassword",
                "full_name": "Duplicate User"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "ya existe" in data["detail"].lower()
