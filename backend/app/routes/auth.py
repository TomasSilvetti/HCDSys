from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..db import models, schemas
from ..db.database import get_db
from ..utils.security import authenticate_user, create_access_token, get_password_hash
from ..utils.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint para autenticar usuario y generar token JWT.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
