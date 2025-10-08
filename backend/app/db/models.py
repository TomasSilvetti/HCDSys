from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Table
from sqlalchemy.orm import relationship

from .database import Base

# Tabla de relación entre roles y permisos
rol_permiso = Table(
    'rol_permiso',
    Base.metadata,
    Column('rol_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('permisos.id'), primary_key=True)
)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    dni = Column(String, unique=True, index=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    ultimo_acceso = Column(DateTime, nullable=True)

    # Relaciones
    role = relationship("Rol", back_populates="usuarios")
    documentos = relationship("Documento", back_populates="usuario")
    versiones = relationship("VersionDocumento", back_populates="usuario")
    historial = relationship("HistorialAcceso", back_populates="usuario")

class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="role")
    permisos = relationship("Permiso", secondary=rol_permiso, back_populates="roles")

class CategoriaPermiso(Base):
    __tablename__ = "categorias_permiso"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    codigo = Column(String, unique=True, nullable=False)
    
    # Relaciones
    permisos = relationship("Permiso", back_populates="categoria")

class Permiso(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    codigo = Column(String, unique=True, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias_permiso.id"), nullable=False)
    es_critico = Column(Boolean, default=False)

    # Relaciones
    roles = relationship("Rol", secondary=rol_permiso, back_populates="permisos")
    categoria = relationship("CategoriaPermiso", back_populates="permisos")

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)

    # Relaciones
    documentos = relationship("Documento", back_populates="categoria")

class TipoDocumento(Base):
    __tablename__ = "tipos_documento"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    extensiones_permitidas = Column(String, nullable=False)

    # Relaciones
    documentos = relationship("Documento", back_populates="tipo_documento")

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False, index=True)
    numero_expediente = Column(String, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    tipo_documento_id = Column(Integer, ForeignKey("tipos_documento.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    path_archivo = Column(String, nullable=False)
    activo = Column(Boolean, default=True)

    # Relaciones
    categoria = relationship("Categoria", back_populates="documentos")
    tipo_documento = relationship("TipoDocumento", back_populates="documentos")
    usuario = relationship("Usuario", back_populates="documentos")
    versiones = relationship("VersionDocumento", back_populates="documento")
    historial = relationship("HistorialAcceso", back_populates="documento")

class VersionDocumento(Base):
    __tablename__ = "versiones_documento"

    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, ForeignKey("documentos.id"), nullable=False)
    numero_version = Column(Integer, nullable=False)
    fecha_version = Column(DateTime, default=datetime.utcnow)
    comentario = Column(Text, nullable=True)
    path_archivo = Column(String, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Relaciones
    documento = relationship("Documento", back_populates="versiones")
    usuario = relationship("Usuario", back_populates="versiones")

class HistorialAcceso(Base):
    __tablename__ = "historial_acceso"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    documento_id = Column(Integer, ForeignKey("documentos.id"), nullable=False)
    accion = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    detalles = Column(Text, nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="historial")
    documento = relationship("Documento", back_populates="historial")

class HistorialRol(Base):
    __tablename__ = "historial_rol"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    rol_anterior_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    rol_nuevo_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    modificado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_cambio = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    rol_anterior = relationship("Rol", foreign_keys=[rol_anterior_id])
    rol_nuevo = relationship("Rol", foreign_keys=[rol_nuevo_id])
    modificado_por = relationship("Usuario", foreign_keys=[modificado_por_id])

class HistorialPermiso(Base):
    __tablename__ = "historial_permiso"
    
    id = Column(Integer, primary_key=True, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permiso_id = Column(Integer, ForeignKey("permisos.id"), nullable=False)
    accion = Column(String, nullable=False)  # "asignado" o "removido"
    modificado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_cambio = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    rol = relationship("Rol", foreign_keys=[rol_id])
    permiso = relationship("Permiso", foreign_keys=[permiso_id])
    modificado_por = relationship("Usuario", foreign_keys=[modificado_por_id])