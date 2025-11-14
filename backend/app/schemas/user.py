"""
Schemas Pydantic para usuarios.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
import re


class UserBase(BaseModel):
    """Schema base para usuario."""
    email: EmailStr
    nombre: str
    apellido: str
    dni: str
    
    @validator('dni')
    def validate_dni(cls, v):
        if not re.match(r'^\d{7,8}$', v):
            raise ValueError('DNI debe tener entre 7 y 8 dígitos')
        return v


class UserCreate(UserBase):
    """Schema para crear un usuario."""
    password: str
    role_id: int
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe tener al menos una letra mayúscula')
        return v


class UserUpdate(BaseModel):
    """Schema para actualizar un usuario."""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    activo: Optional[bool] = None
    role_id: Optional[int] = None
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('La contraseña debe tener al menos 8 caracteres')
            if not any(c.isupper() for c in v):
                raise ValueError('La contraseña debe tener al menos una letra mayúscula')
        return v


class UserInDB(UserBase):
    """Schema para usuario en base de datos."""
    id: int
    activo: bool
    role_id: int
    fecha_registro: datetime
    ultimo_acceso: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserBasic(BaseModel):
    """Schema básico de usuario (sin información sensible)."""
    id: int
    nombre: str
    apellido: str
    email: EmailStr

    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema completo de usuario."""
    pass

