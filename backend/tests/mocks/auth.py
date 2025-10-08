"""
Mocks para autenticación y seguridad
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import MagicMock

from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.utils.config import settings
from app.db.models import Usuario as User

# Token de prueba
MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwicm9sZSI6InVzdWFyaW8iLCJleHAiOjE3MjUwODg0MDB9.THIS_IS_A_MOCK_TOKEN"

# Mock para el usuario actual
def get_mock_current_user(
    user_id: int = 1,
    email: str = "test@example.com",
    role_name: str = "usuario"
) -> User:
    """Devuelve un usuario mock para pruebas"""
    mock_user = MagicMock(spec=User)
    mock_user.id = user_id
    mock_user.email = email
    mock_user.full_name = "Test User"
    mock_user.is_active = True
    
    # Configurar el rol del usuario
    mock_role = MagicMock()
    mock_role.id = 1 if role_name == "usuario" else (2 if role_name == "gestor" else 3)
    mock_role.name = role_name
    
    # Configurar permisos basados en el rol
    if role_name == "admin":
        mock_role.permissions = ["create:document", "read:document", "update:document", "delete:document", "manage:users"]
    elif role_name == "gestor":
        mock_role.permissions = ["create:document", "read:document", "update:document", "delete:document"]
    else:  # usuario
        mock_role.permissions = ["read:document"]
    
    mock_user.role = mock_role
    return mock_user

# Mock para el token de acceso
def create_mock_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token de acceso mock para pruebas"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    
    # Para pruebas, simplemente devolvemos un token mock en lugar de codificar uno real
    return MOCK_TOKEN

# Mock para la dependencia de usuario actual
def get_mock_current_user_dependency(role_name: str = "usuario"):
    """Crea una dependencia mock para el usuario actual"""
    async def _get_current_user():
        return get_mock_current_user(role_name=role_name)
    return _get_current_user

# Mock para verificar permisos
def mock_has_permission(permission: str, user_role: str) -> bool:
    """Verifica si un rol tiene un permiso específico"""
    if user_role == "admin":
        return True
    
    if user_role == "gestor":
        return permission in ["create:document", "read:document", "update:document", "delete:document"]
    
    if user_role == "usuario":
        return permission == "read:document"
    
    return False
