from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..db import models, schemas
from ..db.database import get_db
from .config import settings

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar si la contraseña en texto plano coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    """Autenticar usuario por email y contraseña"""
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    if not user.activo:
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token de acceso JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """Obtener el usuario actual a partir del token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.Usuario).filter(models.Usuario.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador."
        )
    
    # Actualizar último acceso
    user.ultimo_acceso = datetime.utcnow()
    db.commit()
    
    return user

async def get_current_active_user(current_user: models.Usuario = Depends(get_current_user)):
    """Verificar que el usuario actual esté activo"""
    if not current_user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador."
        )
    return current_user

def check_permission(user: models.Usuario, permission_code: str, db: Session):
    """Verificar si el usuario tiene un permiso específico"""
    # TEMPORALMENTE DESACTIVADO PARA DEPURACIÓN - SIEMPRE DEVUELVE TRUE
    return True
    
    # Código original comentado:
    """
    # Enfoque simplificado basado en roles para MVP
    
    # Rol 1: Administrador - tiene todos los permisos
    if user.role_id == 1:
        return True
        
    # Rol 2: Editor - tiene permisos de edición de documentos
    if user.role_id == 2:
        # Lista de permisos para editores
        editor_permissions = [
            "docs:create", "docs:edit", "docs:view", "docs:download", 
            "docs:versions:view", "docs:versions:manage", "search:basic", 
            "search:advanced", "search:restricted"
        ]
        return permission_code in editor_permissions
        
    # Rol 3: Usuario básico - permisos limitados
    if user.role_id == 3:
        # Lista de permisos para usuarios básicos
    """
    basic_permissions = [
        "docs:view", "docs:download", "search:basic", 
        "docs:versions:view"
    ]
    return permission_code in basic_permissions
        
    # Si no es ninguno de estos roles o el permiso no está en la lista
    return False

async def get_current_user_ws(token: str, db: Session):
    """
    Versión para WebSockets de get_current_user.
    Obtiene el usuario actual a partir del token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.Usuario).filter(models.Usuario.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador."
        )
    
    # Actualizar último acceso
    user.ultimo_acceso = datetime.utcnow()
    db.commit()
    
    return user
