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
    registros_acceso = relationship("RegistroAcceso", back_populates="usuario")

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
    hash_archivo = Column(String, nullable=True)  # Hash para verificación de integridad
    tamano_archivo = Column(Integer, nullable=True)  # Tamaño en bytes
    extension_archivo = Column(String, nullable=True)  # Extensión del archivo
    fecha_ultima_verificacion = Column(DateTime, nullable=True)  # Fecha de última verificación de integridad
    estado_integridad = Column(Boolean, nullable=True)  # True si la última verificación fue exitosa
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

class RegistroAcceso(Base):
    __tablename__ = "registro_acceso"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)  # Puede ser nulo en intentos fallidos
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    endpoint = Column(String, nullable=False)
    metodo = Column(String, nullable=False)  # GET, POST, PUT, DELETE, etc.
    fecha = Column(DateTime, default=datetime.utcnow)
    exitoso = Column(Boolean, default=True)
    codigo_respuesta = Column(Integer, nullable=False)  # 200, 401, 403, etc.
    mensaje_error = Column(String, nullable=True)  # Detalle del error si falla
    tiempo_respuesta = Column(Float, nullable=True)  # Tiempo de respuesta en ms
    
    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id], back_populates="registros_acceso")

class IntentosLogin(Base):
    __tablename__ = "intentos_login"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    exitoso = Column(Boolean, default=False)
    motivo_fallo = Column(String, nullable=True)  # "credenciales_invalidas", "usuario_inactivo", etc.
    
class BloqueoIP(Base):
    __tablename__ = "bloqueo_ip"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, nullable=False, index=True, unique=True)
    motivo = Column(String, nullable=False)  # "intentos_fallidos", "actividad_sospechosa", etc.
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=False)  # Cuando expira el bloqueo
    activo = Column(Boolean, default=True)

class ErrorAlmacenamiento(Base):
    __tablename__ = "errores_almacenamiento"
    
    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, ForeignKey("documentos.id"), nullable=True)  # Puede ser nulo si el error ocurre antes de crear el registro
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_error = Column(String, nullable=False)  # "db", "filesystem", "integridad", etc.
    mensaje_error = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    resuelto = Column(Boolean, default=False)
    acciones_tomadas = Column(Text, nullable=True)  # Acciones de rollback realizadas
    
    # Relaciones
    documento = relationship("Documento", foreign_keys=[documento_id])
    usuario = relationship("Usuario", foreign_keys=[usuario_id])