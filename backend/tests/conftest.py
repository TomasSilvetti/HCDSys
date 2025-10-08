import os
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient
from typing import AsyncGenerator, Generator

# Importaciones de la aplicación
from app.main_test import app
from app.db.database import Base, get_db
from app.db.models import Usuario as User, Rol as Role, Permiso as Permission, Documento as Document
from app.utils.security import get_password_hash

# Configuración de la base de datos de prueba
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Crear motor de base de datos asíncrono para pruebas
engine = create_async_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Crear fábrica de sesiones para pruebas
TestingSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Sobreescribir la dependencia de la base de datos
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Fixtures para las pruebas
@pytest.fixture(scope="session")
def event_loop():
    """Crear un event loop para las pruebas asíncronas"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Crear tablas y proporcionar una sesión de base de datos para las pruebas"""
    # Crear todas las tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Proporcionar la sesión
    async with TestingSessionLocal() as session:
        yield session
    
    # Limpiar después de las pruebas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Proporcionar un cliente de prueba para la API"""
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Proporcionar un cliente asíncrono para pruebas asíncronas"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
async def test_roles(db_session: AsyncSession) -> dict:
    """Crear roles de prueba"""
    roles = {
        "admin": Role(name="admin", description="Administrador del sistema"),
        "gestor": Role(name="gestor", description="Gestor de documentos"),
        "usuario": Role(name="usuario", description="Usuario regular")
    }
    
    for role in roles.values():
        db_session.add(role)
    
    await db_session.commit()
    
    # Refrescar para obtener los IDs
    for role in roles.values():
        await db_session.refresh(role)
    
    return roles

@pytest.fixture(scope="function")
async def test_users(db_session: AsyncSession, test_roles: dict) -> dict:
    """Crear usuarios de prueba"""
    users = {
        "admin": User(
            email="admin@example.com",
            hashed_password=get_password_hash("adminpassword"),
            full_name="Admin User",
            role_id=test_roles["admin"].id
        ),
        "gestor": User(
            email="gestor@example.com",
            hashed_password=get_password_hash("gestorpassword"),
            full_name="Gestor User",
            role_id=test_roles["gestor"].id
        ),
        "usuario": User(
            email="usuario@example.com",
            hashed_password=get_password_hash("userpassword"),
            full_name="Regular User",
            role_id=test_roles["usuario"].id
        )
    }
    
    for user in users.values():
        db_session.add(user)
    
    await db_session.commit()
    
    # Refrescar para obtener los IDs
    for user in users.values():
        await db_session.refresh(user)
    
    return users

@pytest.fixture(scope="function")
async def test_permissions(db_session: AsyncSession) -> dict:
    """Crear permisos de prueba"""
    permissions = {
        "create_doc": Permission(name="create:document", description="Crear documentos"),
        "read_doc": Permission(name="read:document", description="Leer documentos"),
        "update_doc": Permission(name="update:document", description="Actualizar documentos"),
        "delete_doc": Permission(name="delete:document", description="Eliminar documentos"),
        "manage_users": Permission(name="manage:users", description="Gestionar usuarios")
    }
    
    for permission in permissions.values():
        db_session.add(permission)
    
    await db_session.commit()
    
    # Refrescar para obtener los IDs
    for permission in permissions.values():
        await db_session.refresh(permission)
    
    return permissions
