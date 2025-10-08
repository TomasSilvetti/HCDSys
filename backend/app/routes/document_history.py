from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..db import models, schemas
from ..db.database import get_db
from ..utils.security import get_current_active_user, check_permission

router = APIRouter(prefix="/documents", tags=["document_history"])

@router.get("/{documento_id}/history", response_model=List[schemas.HistorialAcceso])
async def get_document_history(
    documento_id: int,
    page: int = Query(1, description="Número de página", ge=1),
    page_size: int = Query(20, description="Tamaño de página", ge=1, le=100),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de acceso y modificaciones de un documento.
    Requiere permiso para ver el documento o ser el creador del mismo.
    """
    # Verificar si el documento existe
    documento = db.query(models.Documento).filter(
        models.Documento.id == documento_id
    ).first()
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos
    is_owner = documento.usuario_id == current_user.id
    has_view_permission = check_permission(current_user, "DOCUMENT_VIEW_ALL", db)
    has_history_permission = check_permission(current_user, "DOCUMENT_HISTORY_VIEW", db)
    
    if not (is_owner or has_view_permission or has_history_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver el historial de este documento"
        )
    
    # Calcular offset para paginación
    skip = (page - 1) * page_size
    
    # Obtener historial paginado
    historial = db.query(models.HistorialAcceso).filter(
        models.HistorialAcceso.documento_id == documento_id
    ).order_by(
        desc(models.HistorialAcceso.fecha)
    ).offset(skip).limit(page_size).all()
    
    # Registrar esta consulta en el historial
    new_historial = models.HistorialAcceso(
        usuario_id=current_user.id,
        documento_id=documento_id,
        accion="consulta_historial",
        detalles=f"Consulta de historial de documento"
    )
    db.add(new_historial)
    db.commit()
    
    return historial

@router.get("/errors", response_model=List[schemas.ErrorAlmacenamiento])
async def get_storage_errors(
    documento_id: Optional[int] = None,
    resuelto: Optional[bool] = None,
    page: int = Query(1, description="Número de página", ge=1),
    page_size: int = Query(20, description="Tamaño de página", ge=1, le=100),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene los errores de almacenamiento registrados.
    Requiere permiso de administrador o técnico.
    """
    # Verificar permisos
    has_admin_permission = check_permission(current_user, "ADMIN_SYSTEM_CONFIG", db)
    has_tech_permission = check_permission(current_user, "TECH_STORAGE_MANAGE", db)
    
    if not (has_admin_permission or has_tech_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver los errores de almacenamiento"
        )
    
    # Construir consulta base
    query = db.query(models.ErrorAlmacenamiento)
    
    # Aplicar filtros si se proporcionan
    if documento_id is not None:
        query = query.filter(models.ErrorAlmacenamiento.documento_id == documento_id)
    
    if resuelto is not None:
        query = query.filter(models.ErrorAlmacenamiento.resuelto == resuelto)
    
    # Calcular offset para paginación
    skip = (page - 1) * page_size
    
    # Obtener errores paginados
    errores = query.order_by(
        desc(models.ErrorAlmacenamiento.fecha)
    ).offset(skip).limit(page_size).all()
    
    return errores

@router.put("/errors/{error_id}/resolve", response_model=schemas.ErrorAlmacenamiento)
async def resolve_storage_error(
    error_id: int,
    acciones_tomadas: str,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Marca un error de almacenamiento como resuelto.
    Requiere permiso de administrador o técnico.
    """
    # Verificar permisos
    has_admin_permission = check_permission(current_user, "ADMIN_SYSTEM_CONFIG", db)
    has_tech_permission = check_permission(current_user, "TECH_STORAGE_MANAGE", db)
    
    if not (has_admin_permission or has_tech_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para resolver errores de almacenamiento"
        )
    
    # Obtener error
    error = db.query(models.ErrorAlmacenamiento).filter(
        models.ErrorAlmacenamiento.id == error_id
    ).first()
    
    if not error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error no encontrado"
        )
    
    # Actualizar estado
    error.resuelto = True
    error.acciones_tomadas = acciones_tomadas
    
    db.commit()
    db.refresh(error)
    
    return error
