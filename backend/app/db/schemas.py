from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re

# Esquemas de Usuario
class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str
    apellido: str
    dni: str
    
    @validator('dni')
    def validate_dni(cls, v):
        if not re.match(r'^\d{7,8}$', v):
            raise ValueError('DNI debe tener entre 7 y 8 dígitos')
        return v

class UsuarioCreate(UsuarioBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe tener al menos una letra mayúscula')
        return v

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None
    role_id: Optional[int] = None

class UsuarioInDB(UsuarioBase):
    id: int
    activo: bool
    role_id: int
    fecha_registro: datetime
    ultimo_acceso: Optional[datetime] = None

    class Config:
        orm_mode = True

class Usuario(UsuarioInDB):
    pass

# Esquemas de Autenticación
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role_id: Optional[int] = None

class LoginData(BaseModel):
    email: EmailStr
    password: str

# Esquemas de Rol
class RolBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class RolCreate(RolBase):
    pass

class RolUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class RolInDB(RolBase):
    id: int

    class Config:
        orm_mode = True

class Rol(RolInDB):
    pass

# Esquemas de Permiso
class PermisoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    codigo: str

class PermisoCreate(PermisoBase):
    pass

class PermisoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class PermisoInDB(PermisoBase):
    id: int

    class Config:
        orm_mode = True

class Permiso(PermisoInDB):
    pass

# Esquemas de Categoría
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class CategoriaInDB(CategoriaBase):
    id: int

    class Config:
        orm_mode = True

class Categoria(CategoriaInDB):
    pass

# Esquemas de Tipo de Documento
class TipoDocumentoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    extensiones_permitidas: str

class TipoDocumentoCreate(TipoDocumentoBase):
    pass

class TipoDocumentoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    extensiones_permitidas: Optional[str] = None

class TipoDocumentoInDB(TipoDocumentoBase):
    id: int

    class Config:
        orm_mode = True

class TipoDocumento(TipoDocumentoInDB):
    pass

# Esquemas de Documento
class DocumentoBase(BaseModel):
    titulo: str
    numero_expediente: str
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    tipo_documento_id: int

class DocumentoCreate(DocumentoBase):
    pass

class DocumentoUpdate(BaseModel):
    titulo: Optional[str] = None
    numero_expediente: Optional[str] = None
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    tipo_documento_id: Optional[int] = None
    activo: Optional[bool] = None

class DocumentoInDB(DocumentoBase):
    id: int
    fecha_creacion: datetime
    fecha_modificacion: datetime
    usuario_id: int
    path_archivo: str
    activo: bool

    class Config:
        orm_mode = True

class Documento(DocumentoInDB):
    categoria: Optional[Categoria] = None
    tipo_documento: TipoDocumento
    usuario: Usuario

# Esquemas de Versión de Documento
class VersionDocumentoBase(BaseModel):
    documento_id: int
    numero_version: int
    comentario: Optional[str] = None

class VersionDocumentoCreate(VersionDocumentoBase):
    pass

class VersionDocumentoInDB(VersionDocumentoBase):
    id: int
    fecha_version: datetime
    path_archivo: str
    usuario_id: int

    class Config:
        orm_mode = True

class VersionDocumento(VersionDocumentoInDB):
    documento: Documento
    usuario: Usuario

# Esquemas de Historial de Acceso
class HistorialAccesoBase(BaseModel):
    documento_id: int
    accion: str
    detalles: Optional[str] = None

class HistorialAccesoCreate(HistorialAccesoBase):
    pass

class HistorialAccesoInDB(HistorialAccesoBase):
    id: int
    usuario_id: int
    fecha: datetime

    class Config:
        orm_mode = True

class HistorialAcceso(HistorialAccesoInDB):
    documento: Documento
    usuario: Usuario

# Esquema de búsqueda de documentos
class DocumentoSearchParams(BaseModel):
    termino: str
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    tipo_documento_id: Optional[int] = None
    categoria_id: Optional[int] = None
    numero_expediente: Optional[str] = None
    usuario_id: Optional[int] = None
