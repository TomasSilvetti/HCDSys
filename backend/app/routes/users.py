from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from ..db import models, schemas
from ..db.database import get_db
from ..utils.security import get_current_active_user, check_permission

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[schemas.Usuario])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de usuarios.
    Solo administradores pueden acceder a esta funcionalidad.
    """
    # Verificar si el usuario tiene permisos de administrador
    if not check_permission(current_user, "USER_VIEW_ALL", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver la lista de usuarios"
        )
    
    usuarios = db.query(models.Usuario).offset(skip).limit(limit).all()
    return usuarios

@router.get("/search", response_model=List[schemas.UsuarioBasico])
async def search_users(
    query: str = Query(..., min_length=2, description="Término de búsqueda (nombre, apellido o email)"),
    limit: int = Query(10, ge=1, le=50, description="Número máximo de resultados"),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Buscar usuarios por nombre, apellido o email.
    Retorna información básica para autocompletado.
    """
    # Verificar si el usuario tiene permisos para buscar usuarios
    if not check_permission(current_user, "USER_SEARCH", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para buscar usuarios"
        )
    
    # Buscar usuarios que coincidan con el término de búsqueda
    usuarios = db.query(models.Usuario).filter(
        models.Usuario.activo == True,
        or_(
            models.Usuario.nombre.ilike(f"%{query}%"),
            models.Usuario.apellido.ilike(f"%{query}%"),
            models.Usuario.email.ilike(f"%{query}%"),
            func.concat(models.Usuario.nombre, ' ', models.Usuario.apellido).ilike(f"%{query}%")
        )
    ).limit(limit).all()
    
    # Crear respuesta con información básica
    return [
        {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "email": usuario.email,
            "nombre_completo": f"{usuario.nombre} {usuario.apellido}"
        }
        for usuario in usuarios
    ]

@router.get("/{usuario_id}", response_model=schemas.Usuario)
async def get_user(
    usuario_id: int,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener información de un usuario específico.
    """
    # Verificar si el usuario tiene permisos para ver usuarios
    if current_user.id != usuario_id and not check_permission(current_user, "USER_VIEW", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este usuario"
        )
    
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario