import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Usuario as User, Rol as Role, Permiso as Permission
from app.utils.security import get_password_hash

@pytest.mark.integration
@pytest.mark.asyncio
class TestUsersRolesFlow:
    async def test_user_role_management(self, async_client: AsyncClient, db_session: AsyncSession):
        """Prueba el flujo de gestión de roles de usuarios"""
        # 1. Crear un usuario administrador para las pruebas
        admin_user = User(
            email="admin_test@example.com",
            hashed_password=get_password_hash("adminpass"),
            full_name="Admin Test",
            role_name="admin"
        )
        db_session.add(admin_user)
        
        # 2. Crear un usuario regular para modificar
        regular_user = User(
            email="regular_user@example.com",
            hashed_password=get_password_hash("userpass"),
            full_name="Regular User",
            role_name="usuario"
        )
        db_session.add(regular_user)
        
        await db_session.commit()
        await db_session.refresh(admin_user)
        await db_session.refresh(regular_user)
        
        # 3. Iniciar sesión como administrador
        login_data = {
            "email": "admin_test@example.com",
            "password": "adminpass"
        }
        
        login_response = await async_client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 4. Obtener todos los usuarios
        response = await async_client.get("/users", headers=headers)
        
        # Verificar respuesta
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 2
        
        # 5. Obtener todos los roles
        response = await async_client.get("/roles", headers=headers)
        
        # Verificar respuesta
        assert response.status_code == 200
        roles = response.json()
        assert isinstance(roles, list)
        
        # Encontrar el rol de gestor
        gestor_role = next((role for role in roles if role["name"] == "gestor"), None)
        assert gestor_role is not None
        
        # 6. Cambiar el rol del usuario regular a gestor
        update_data = {
            "role_id": gestor_role["id"]
        }
        
        response = await async_client.put(
            f"/users/{regular_user.id}/role",
            headers=headers,
            json=update_data
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["role"]["name"] == "gestor"
        
        # 7. Verificar que el cambio se aplicó en la base de datos
        await db_session.refresh(regular_user)
        assert regular_user.role_name == "gestor"
        
        # 8. Verificar que el usuario actualizado tiene los permisos correctos
        response = await async_client.get(f"/users/{regular_user.id}/permissions", headers=headers)
        
        # Verificar respuesta
        assert response.status_code == 200
        permissions = response.json()
        
        # Verificar que tiene permisos de gestor
        permission_names = [p["name"] for p in permissions]
        assert "create:document" in permission_names
        assert "update:document" in permission_names
        assert "delete:document" in permission_names
    
    async def test_role_permission_management(self, async_client: AsyncClient, db_session: AsyncSession):
        """Prueba el flujo de gestión de permisos para roles"""
        # 1. Crear un usuario administrador para las pruebas
        admin_user = User(
            email="admin_perm@example.com",
            hashed_password=get_password_hash("adminpass"),
            full_name="Admin Permissions",
            role_name="admin"
        )
        db_session.add(admin_user)
        await db_session.commit()
        await db_session.refresh(admin_user)
        
        # 2. Iniciar sesión como administrador
        login_data = {
            "email": "admin_perm@example.com",
            "password": "adminpass"
        }
        
        login_response = await async_client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Obtener todos los roles
        response = await async_client.get("/roles", headers=headers)
        roles = response.json()
        
        # Encontrar el rol de usuario
        usuario_role = next((role for role in roles if role["name"] == "usuario"), None)
        assert usuario_role is not None
        
        # 4. Obtener todos los permisos
        response = await async_client.get("/permissions", headers=headers)
        permissions = response.json()
        
        # Encontrar el permiso de crear documentos
        create_doc_permission = next((perm for perm in permissions if perm["name"] == "create:document"), None)
        assert create_doc_permission is not None
        
        # 5. Asignar el permiso de crear documentos al rol de usuario
        response = await async_client.post(
            f"/roles/{usuario_role['id']}/permissions/{create_doc_permission['id']}",
            headers=headers
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        
        # 6. Verificar que el permiso fue asignado
        response = await async_client.get(f"/roles/{usuario_role['id']}/permissions", headers=headers)
        role_permissions = response.json()
        
        permission_names = [p["name"] for p in role_permissions]
        assert "create:document" in permission_names
        
        # 7. Eliminar el permiso
        response = await async_client.delete(
            f"/roles/{usuario_role['id']}/permissions/{create_doc_permission['id']}",
            headers=headers
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        
        # 8. Verificar que el permiso fue eliminado
        response = await async_client.get(f"/roles/{usuario_role['id']}/permissions", headers=headers)
        role_permissions = response.json()
        
        permission_names = [p["name"] for p in role_permissions]
        assert "create:document" not in permission_names
    
    async def test_permission_based_access(self, async_client: AsyncClient, db_session: AsyncSession):
        """Prueba el control de acceso basado en permisos"""
        # 1. Crear usuarios con diferentes roles
        admin_user = User(
            email="admin_access@example.com",
            hashed_password=get_password_hash("adminpass"),
            full_name="Admin Access",
            role_name="admin"
        )
        db_session.add(admin_user)
        
        regular_user = User(
            email="regular_access@example.com",
            hashed_password=get_password_hash("userpass"),
            full_name="Regular Access",
            role_name="usuario"
        )
        db_session.add(regular_user)
        
        await db_session.commit()
        await db_session.refresh(admin_user)
        await db_session.refresh(regular_user)
        
        # 2. Iniciar sesión como usuario regular
        login_data = {
            "email": "regular_access@example.com",
            "password": "userpass"
        }
        
        login_response = await async_client.post("/auth/login", json=login_data)
        user_token = login_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # 3. Intentar acceder a un endpoint administrativo
        response = await async_client.get("/users", headers=user_headers)
        
        # Verificar que se deniega el acceso
        assert response.status_code == 403
        
        # 4. Iniciar sesión como administrador
        login_data = {
            "email": "admin_access@example.com",
            "password": "adminpass"
        }
        
        login_response = await async_client.post("/auth/login", json=login_data)
        admin_token = login_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 5. Acceder al mismo endpoint como administrador
        response = await async_client.get("/users", headers=admin_headers)
        
        # Verificar que se permite el acceso
        assert response.status_code == 200
