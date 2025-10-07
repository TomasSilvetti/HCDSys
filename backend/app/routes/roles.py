from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import models, schemas
from ..db.database import get_db
from ..utils.security import get_current_active_user, check_permission

router = APIRouter(prefix="/roles", tags=["roles"])

# Obtener todos los roles
@router.get("/", response_model=List[schemas.Rol])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener todos los roles disponibles en el sistema.
    Requiere permisos de administrador.
    """
    # Verificar permisos
    if not check_permission(current_user, "admin:roles:manage", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver roles"
        )
    
    roles = db.query(models.Rol).all()
    return roles

# Obtener un rol específico
@router.get("/{role_id}", response_model=schemas.Rol)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener información detallada de un rol específico.
    Requiere permisos de administrador.
    """
    # Verificar permisos
    if not check_permission(current_user, "admin:roles:manage", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver roles"
        )
    
    role = db.query(models.Rol).filter(models.Rol.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    return role

# Asignar rol a usuario
@router.put("/users/{user_id}", response_model=schemas.Usuario)
async def assign_role_to_user(
    user_id: int,
    role_data: schemas.RolUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Asignar un rol a un usuario.
    Requiere permisos de administrador.
    """
    # Verificar permisos
    if not check_permission(current_user, "admin:roles:manage", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para asignar roles"
        )
    
    # Verificar que el rol existe
    role = db.query(models.Rol).filter(models.Rol.id == role_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Verificar que el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Evitar que un administrador cambie su propio rol
    if user_id == current_user.id and current_user.role_id == 1:  # Rol de Administrador
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede cambiar su propio rol de administrador"
        )
    
    # Guardar el rol anterior para el historial
    rol_anterior_id = user.role_id
    
    # Asignar nuevo rol
    user.role_id = role_data.role_id
    
    # Registrar cambio en el historial
    historial = models.HistorialRol(
        usuario_id=user_id,
        rol_anterior_id=rol_anterior_id,
        rol_nuevo_id=role_data.role_id,
        modificado_por_id=current_user.id
    )
    db.add(historial)
    
    # Guardar cambios
    db.commit()
    db.refresh(user)
    
    return user

# Obtener historial de cambios de rol de un usuario
@router.get("/users/{user_id}/history", response_model=List[schemas.HistorialRol])
async def get_user_role_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener historial de cambios de rol de un usuario específico.
    Requiere permisos de administrador.
    """
    # Verificar permisos
    if not check_permission(current_user, "admin:roles:manage", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver historial de roles"
        )
    
    # Verificar que el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Obtener historial
    historial = db.query(models.HistorialRol).filter(
        models.HistorialRol.usuario_id == user_id
    ).order_by(models.HistorialRol.fecha_cambio.desc()).all()
    
    return historial
