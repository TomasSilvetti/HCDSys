import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Usuario as User
from app.utils.security import verify_password

@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthFlow:
    async def test_register_login_flow(self, async_client: AsyncClient, db_session: AsyncSession):
        """Prueba el flujo completo de registro y login de un usuario"""
        # 1. Registrar un nuevo usuario
        register_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New Test User"
        }
        
        register_response = await async_client.post("/api/auth/register", json=register_data)
        
        # Verificar respuesta de registro
        assert register_response.status_code == 201
        register_data = register_response.json()
        assert register_data["email"] == "newuser@example.com"
        assert register_data["full_name"] == "New Test User"
        assert "id" in register_data
        
        # Verificar que el usuario se creó en la base de datos
        user_id = register_data["id"]
        db_user = await db_session.get(User, user_id)
        assert db_user is not None
        assert db_user.email == "newuser@example.com"
        assert db_user.full_name == "New Test User"
        assert verify_password("securepassword123", db_user.hashed_password)
        
        # 2. Iniciar sesión con el usuario registrado
        login_data = {
            "email": "newuser@example.com",
            "password": "securepassword123"
        }
        
        login_response = await async_client.post("/api/auth/login", json=login_data)
        
        # Verificar respuesta de login
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        assert login_data["token_type"] == "bearer"
        assert login_data["user"]["email"] == "newuser@example.com"
        
        # 3. Obtener perfil del usuario con el token
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        profile_response = await async_client.get("/auth/me", headers=headers)
        
        # Verificar respuesta de perfil
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["email"] == "newuser@example.com"
        assert profile_data["full_name"] == "New Test User"
    
    async def test_invalid_login_attempts(self, async_client: AsyncClient):
        """Prueba intentos de inicio de sesión inválidos"""
        # 1. Intento con email inexistente
        login_data = {
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
        
        response = await async_client.post("/api/auth/login", json=login_data)
        
        # Verificar respuesta de error
        assert response.status_code == 401
        assert "detail" in response.json()
        
        # 2. Intento con contraseña incorrecta para un usuario existente
        # Primero registramos un usuario
        register_data = {
            "email": "testuser@example.com",
            "password": "correctpassword",
            "full_name": "Test User"
        }
        
        await async_client.post("/api/auth/register", json=register_data)
        
        # Luego intentamos login con contraseña incorrecta
        login_data = {
            "email": "testuser@example.com",
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/api/auth/login", json=login_data)
        
        # Verificar respuesta de error
        assert response.status_code == 401
        assert "detail" in response.json()
    
    async def test_token_validation(self, async_client: AsyncClient):
        """Prueba la validación de tokens de acceso"""
        # 1. Registrar y hacer login con un usuario
        register_data = {
            "email": "tokentest@example.com",
            "password": "tokenpassword",
            "full_name": "Token Test User"
        }
        
        await async_client.post("/api/auth/register", json=register_data)
        
        login_data = {
            "email": "tokentest@example.com",
            "password": "tokenpassword"
        }
        
        login_response = await async_client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # 2. Acceder a un endpoint protegido con token válido
        valid_headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get("/api/auth/me", headers=valid_headers)
        
        # Verificar acceso exitoso
        assert response.status_code == 200
        
        # 3. Acceder con token inválido
        invalid_headers = {"Authorization": "Bearer invalidtoken12345"}
        response = await async_client.get("/api/auth/me", headers=invalid_headers)
        
        # Verificar acceso denegado
        assert response.status_code == 401
        
        # 4. Acceder sin token
        response = await async_client.get("/api/auth/me")
        
        # Verificar acceso denegado
        assert response.status_code == 401
