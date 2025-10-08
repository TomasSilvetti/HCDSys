from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload

from .websockets import notify_permission_change

from ..db import models, schemas
from ..db.database import get_db
from ..utils.security import get_current_active_user, check_permission

router = APIRouter(prefix="/permissions", tags=["permissions"])

# Obtener todas las categorías de permisos
@router.get("/categories", response_model=List[schemas.CategoriaPermiso])
async def get_permission_categories(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener todas las categorías de permisos disponibles.
    Requiere permisos de administrador.
    """
    # Verificar permisos
    if not check_permission(current_user, "admin:permissions:manage", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver categorías de permisos"
        )
    
    categories = db.query(models.CategoriaPermiso).all()
    return categories

# Obtener todos los permisos
@router.get("/", response_model=List[schemas.Permiso])
async def get_permissions(
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener todos los permisos disponibles.
    Se puede filtrar por categoría.
    Requiere permisos de administrador.
    """
    # Verificar permisos
    if not check_permission(current_user, "admin:permissions:manage", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver permisos"
        )
    
    # Consulta base con eager loading para la categoría
    query = db.query(models.Permiso).options(joinedload(models.Permiso.categoria))
    
    # Filtrar por categoría si se especifica
    if categoria_id:
        query = query.filter(models.Permiso.categoria_id == categoria_id)
    
    permisos = query.all()
    return permisos

# Obtener permisos de un rol específico
@router.get("/roles/{role_id}", response_model=List[schemas.Permiso])
async def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener todos los permisos asignados a un rol específico.
    Requiere permisos de administrador.
    """
    # Verificar permisos
    if not check_permission(current_user, "admin:permissions:manage", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver permisos de roles"
        )
    
    # Verificar que el rol existe
    role = db.query(models.Rol).filter(models.Rol.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Obtener permisos del rol con eager loading para la categoría
    permisos = db.query(models.Permiso)\
        .join(models.rol_permiso, models.Permiso.id == models.rol_permiso.c.permiso_id)\
        .filter(models.rol_permiso.c.rol_id == role_id)\
        .options(joinedload(models.Permiso.categoria))\
        .all()
    
    return permisos

# Asignar permiso a un rol
@router.post("/roles/assign", status_code=status.HTTP_200_OK)
async def assign_permission_to_role(
    permission_data: schemas.AsignarPermisoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Asignar un permiso a un rol.
    Requiere permisos de administrador.
    """
    # Verificar permisos
    if not check_permission(current_user, "admin:permissions:manage", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para asignar permisos a roles"
        )
    
    # Verificar que el rol existe
    role = db.query(models.Rol).filter(models.Rol.id == permission_data.rol_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Verificar que el permiso existe
    permission = db.query(models.Permiso).filter(models.Permiso.id == permission_data.permiso_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permiso no encontrado"
        )
    
    # Verificar si el permiso ya está asignado al rol
    existing_assignment = db.query(models.rol_permiso).filter(
        models.rol_permiso.c.rol_id == permission_data.rol_id,
        models.rol_permiso.c.permiso_id == permission_data.permiso_id
    ).first()
    
    if existing_assignment:
        return {"message": "El permiso ya está asignado al rol"}
    
    # Verificar si el permiso es crítico
    if permission.es_critico:
        # Solo el rol de administrador puede tener permisos críticos
        if role.id != 1:  # Asumiendo que 1 es el ID del rol de administrador
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Los permisos críticos solo pueden ser asignados al rol de administrador"
            )
    
    # Asignar permiso al rol
    role.permisos.append(permission)
    
    # Registrar en historial
    historial = models.HistorialPermiso(
        rol_id=permission_data.rol_id,
        permiso_id=permission_data.permiso_id,
        accion="asignado",
        modificado_por_id=current_user.id
    )
    db.add(historial)
    
    db.commit()
    
    # Tarea en segundo plano para notificar a usuarios afectados
    background_tasks.add_task(notify_permission_change, permission_data.rol_id, permission_data.permiso_id, "asignado", db)
    
    return {"message": "Permiso asignado correctamente al rol"}

# Remover permiso de un rol
@router.post("/roles/remove", status_code=status.HTTP_200_OK)
async def remove_permission_from_role(
    permission_data: schemas.AsignarPermisoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Remover un permiso de un rol.
    Requiere permisos de administrador.
    """
    # Verificar permisos
    if not check_permission(current_user, "admin:permissions:manage", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para remover permisos de roles"
        )
    
    # Verificar que el rol existe
    role = db.query(models.Rol).filter(models.Rol.id == permission_data.rol_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Verificar que el permiso existe
    permission = db.query(models.Permiso).filter(models.Permiso.id == permission_data.permiso_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permiso no encontrado"
        )
    
    # Verificar si el permiso está asignado al rol
    existing_assignment = db.query(models.rol_permiso).filter(
        models.rol_permiso.c.rol_id == permission_data.rol_id,
        models.rol_permiso.c.permiso_id == permission_data.permiso_id
    ).first()
    
    if not existing_assignment:
        return {"message": "El permiso no está asignado al rol"}
    
    # Verificar si el permiso es crítico
    if permission.es_critico:
        # No permitir remover permisos críticos del rol de administrador
        if role.id == 1:  # Asumiendo que 1 es el ID del rol de administrador
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se pueden remover permisos críticos del rol de administrador"
            )
    
    # Remover permiso del rol
    role.permisos.remove(permission)
    
    # Registrar en historial
    historial = models.HistorialPermiso(
        rol_id=permission_data.rol_id,
        permiso_id=permission_data.permiso_id,
        accion="removido",
        modificado_por_id=current_user.id
    )
    db.add(historial)
    
    db.commit()
    
    # Tarea en segundo plano para notificar a usuarios afectados
    background_tasks.add_task(notify_permission_change, permission_data.rol_id, permission_data.permiso_id, "removido", db)
    
    return {"message": "Permiso removido correctamente del rol"}

# Obtener historial de cambios de permisos de un rol
@router.get("/roles/{role_id}/history", response_model=List[schemas.HistorialPermiso])
async def get_role_permission_history(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener historial de cambios de permisos de un rol específico.
    Requiere permisos de administrador.
    """
    # Verificar permisos
    if not check_permission(current_user, "admin:permissions:manage", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver historial de permisos"
        )
    
    # Verificar que el rol existe
    role = db.query(models.Rol).filter(models.Rol.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Obtener historial
    historial = db.query(models.HistorialPermiso).filter(
        models.HistorialPermiso.rol_id == role_id
    ).order_by(models.HistorialPermiso.fecha_cambio.desc()).all()
    
    return historial

# Eliminamos esta función ya que ahora se usa la de websockets.py
