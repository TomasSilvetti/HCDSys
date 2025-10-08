from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..db import models, schemas
from ..db.database import get_db
from ..utils.security import authenticate_user, create_access_token, get_password_hash
from ..utils.config import settings
from ..utils.middleware import check_and_block_ip

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint para autenticar usuario y generar token JWT.
    Registra intentos de acceso y bloquea IPs con demasiados intentos fallidos.
    """
    # Obtener IP y user-agent del cliente
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Verificar si la IP está bloqueada
    is_blocked, block_minutes = check_and_block_ip(form_data.username, client_host, db)
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Demasiados intentos fallidos. IP bloqueada por {block_minutes} minutos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Intentar autenticar
    user = authenticate_user(db, form_data.username, form_data.password)
    
    # Registrar intento de login
    intento_login = models.IntentosLogin(
        email=form_data.username,
        ip_address=client_host,
        user_agent=user_agent,
        exitoso=(user is not False and user is not None)
    )
    
    if not user:
        # Autenticación fallida - credenciales incorrectas
        intento_login.motivo_fallo = "credenciales_invalidas"
        db.add(intento_login)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user is None:
        # Autenticación fallida - usuario inactivo
        intento_login.motivo_fallo = "usuario_inactivo"
        db.add(intento_login)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Autenticación exitosa
    db.add(intento_login)
    db.commit()
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role_id": user.role_id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.Usuario)
async def register_user(
    user_data: schemas.UsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Endpoint para registrar un nuevo usuario.
    Por defecto, los nuevos usuarios se crean con el rol de Usuario de Consulta.
    """
    # Verificar si el email ya existe
    db_user = db.query(models.Usuario).filter(models.Usuario.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar si el DNI ya existe
    db_dni = db.query(models.Usuario).filter(models.Usuario.dni == user_data.dni).first()
    if db_dni:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El DNI ya está registrado"
        )
    
    # Obtener el rol de Usuario de Consulta (rol_id=3)
    # Asumimos que este rol existe en la base de datos
    role_id = 3  # Usuario de Consulta
    
    # Crear el nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = models.Usuario(
        email=user_data.email,
        nombre=user_data.nombre,
        apellido=user_data.apellido,
        dni=user_data.dni,
        password_hash=hashed_password,
        role_id=role_id,
        activo=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
