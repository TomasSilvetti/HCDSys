from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import models, schemas
from ..db.database import get_db
from ..utils.security import get_current_active_user, check_permission, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.Usuario)
async def read_users_me(current_user: models.Usuario = Depends(get_current_active_user)):
    """
    Obtener información del usuario actual.
    """
    return current_user

@router.get("/", response_model=List[schemas.Usuario])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de usuarios.
    Solo administradores pueden ver la lista completa de usuarios.
    """
    # Verificar permiso
    if not check_permission(current_user, "USER_LIST", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver la lista de usuarios"
        )
    
    users = db.query(models.Usuario).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=schemas.Usuario)
async def get_user(
    user_id: int,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener información de un usuario específico.
    Solo administradores o el propio usuario pueden ver esta información.
    """
    # Permitir al usuario ver su propia información
    if user_id == current_user.id:
        return current_user
    
    # Verificar permiso para ver información de otros usuarios
    if not check_permission(current_user, "USER_VIEW", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver información de otros usuarios"
        )
    
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user

@router.put("/{user_id}", response_model=schemas.Usuario)
async def update_user(
    user_id: int,
    user_update: schemas.UsuarioUpdate,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar información de un usuario.
    Solo administradores o el propio usuario pueden actualizar esta información.
    """
    # Verificar si el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar permisos
    is_self = user_id == current_user.id
    is_admin = check_permission(current_user, "USER_EDIT", db)
    
    if not (is_self or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para editar este usuario"
        )
    
    # Restricciones para usuarios no administradores
    if not is_admin:
        # Un usuario normal solo puede modificar su nombre y apellido
        if user_update.role_id is not None or user_update.activo is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para modificar rol o estado"
            )
    
    # Verificar si el nuevo email ya existe (si se está actualizando)
    if user_update.email and user_update.email != user.email:
        existing_user = db.query(models.Usuario).filter(
            models.Usuario.email == user_update.email,
            models.Usuario.id != user_id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
    
    # Actualizar campos
    if user_update.nombre:
        user.nombre = user_update.nombre
    if user_update.apellido:
        user.apellido = user_update.apellido
    if user_update.email:
        user.email = user_update.email
    
    # Solo administradores pueden actualizar estos campos
    if is_admin:
        if user_update.role_id is not None:
            # Verificar que el rol existe
            role = db.query(models.Rol).filter(models.Rol.id == user_update.role_id).first()
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rol no válido"
                )
            user.role_id = user_update.role_id
        
        if user_update.activo is not None:
            user.activo = user_update.activo
    
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/roles", response_model=List[schemas.Rol])
async def get_roles(
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de roles disponibles.
    Solo administradores pueden ver la lista de roles.
    """
    # Verificar permiso
    if not check_permission(current_user, "ROLE_LIST", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver la lista de roles"
        )
    
    roles = db.query(models.Rol).all()
    return roles
