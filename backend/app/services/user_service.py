"""
Servicio para la gestión de usuarios.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..db.models import Usuario, Rol
from ..schemas.user import UserCreate, UserUpdate


class UserService:
    """
    Servicio para operaciones relacionadas con usuarios.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def get_password_hash(self, password: str) -> str:
        """
        Genera un hash de la contraseña.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Hash de la contraseña
            
        Returns:
            True si coinciden, False en caso contrario
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_user_by_email(self, email: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        return self.db.query(Usuario).filter(Usuario.email == email).first()
    
    def get_user_by_dni(self, dni: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su DNI.
        
        Args:
            dni: DNI del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        return self.db.query(Usuario).filter(Usuario.dni == dni).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        return self.db.query(Usuario).filter(Usuario.id == user_id).first()
    
    def get_users(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Usuario]:
        """
        Obtiene una lista de usuarios.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a devolver
            active_only: Si True, solo devuelve usuarios activos
            
        Returns:
            Lista de usuarios
        """
        query = self.db.query(Usuario)
        
        if active_only:
            query = query.filter(Usuario.activo == True)
        
        return query.offset(skip).limit(limit).all()
    
    def create_user(self, user_data: UserCreate) -> Usuario:
        """
        Crea un nuevo usuario.
        
        Args:
            user_data: Datos del usuario a crear
            
        Returns:
            Usuario creado
            
        Raises:
            ValueError: Si el email o DNI ya existen
        """
        # Verificar si el email ya existe
        if self.get_user_by_email(user_data.email):
            raise ValueError(f"El email {user_data.email} ya está registrado")
        
        # Verificar si el DNI ya existe
        if self.get_user_by_dni(user_data.dni):
            raise ValueError(f"El DNI {user_data.dni} ya está registrado")
        
        # Hashear la contraseña
        password_hash = self.get_password_hash(user_data.password)
        
        # Crear el usuario
        db_user = Usuario(
            email=user_data.email,
            password_hash=password_hash,
            nombre=user_data.nombre,
            apellido=user_data.apellido,
            dni=user_data.dni,
            role_id=user_data.role_id,
            activo=True
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[Usuario]:
        """
        Actualiza un usuario existente.
        
        Args:
            user_id: ID del usuario a actualizar
            user_data: Datos a actualizar
            
        Returns:
            Usuario actualizado si existe, None en caso contrario
        """
        db_user = self.get_user_by_id(user_id)
        
        if not db_user:
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = user_data.dict(exclude_unset=True)
        
        # Si se actualiza la contraseña, hashearla
        if "password" in update_data:
            update_data["password_hash"] = self.get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def deactivate_user(self, user_id: int) -> Optional[Usuario]:
        """
        Desactiva un usuario.
        
        Args:
            user_id: ID del usuario a desactivar
            
        Returns:
            Usuario desactivado si existe, None en caso contrario
        """
        db_user = self.get_user_by_id(user_id)
        
        if not db_user:
            return None
        
        db_user.activo = False
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def activate_user(self, user_id: int) -> Optional[Usuario]:
        """
        Activa un usuario.
        
        Args:
            user_id: ID del usuario a activar
            
        Returns:
            Usuario activado si existe, None en caso contrario
        """
        db_user = self.get_user_by_id(user_id)
        
        if not db_user:
            return None
        
        db_user.activo = True
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def create_admin_user(
        self,
        email: str,
        password: str,
        nombre: str,
        apellido: str,
        dni: str
    ) -> Usuario:
        """
        Crea un usuario administrador.
        
        Args:
            email: Email del administrador
            password: Contraseña en texto plano
            nombre: Nombre del administrador
            apellido: Apellido del administrador
            dni: DNI del administrador
            
        Returns:
            Usuario administrador creado
            
        Raises:
            ValueError: Si el email o DNI ya existen, o si el rol de Administrador no existe
        """
        # Verificar si ya existe un usuario con ese email
        existing_user = self.get_user_by_email(email)
        if existing_user:
            print(f"El usuario {email} ya existe")
            return existing_user
        
        # Obtener el rol de Administrador
        admin_role = self.db.query(Rol).filter(Rol.nombre == "Administrador").first()
        if not admin_role:
            raise ValueError("El rol de Administrador no existe en la base de datos")
        
        # Crear el usuario administrador
        password_hash = self.get_password_hash(password)
        
        admin_user = Usuario(
            email=email,
            password_hash=password_hash,
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            role_id=admin_role.id,
            activo=True
        )
        
        self.db.add(admin_user)
        self.db.commit()
        self.db.refresh(admin_user)
        
        print(f"Usuario administrador {email} creado correctamente")
        return admin_user
    
    def authenticate_user(self, email: str, password: str) -> Optional[Usuario]:
        """
        Autentica un usuario con email y contraseña.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            Usuario si las credenciales son correctas y está activo, None en caso contrario
        """
        user = self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not user.activo:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user

