from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..db import models, schemas
from ..db.database import get_db
from ..utils.security import get_current_active_user, check_permission
from ..utils.middleware import require_permissions

router = APIRouter(prefix="/security", tags=["security"])

@router.get("/access-logs", response_model=List[schemas.RegistroAcceso])
async def get_access_logs(
    endpoint: Optional[str] = Query(None, description="Filtrar por endpoint"),
    user_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    exitoso: Optional[bool] = Query(None, description="Filtrar por accesos exitosos o fallidos"),
    desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    ip_address: Optional[str] = Query(None, description="Filtrar por dirección IP"),
    skip: int = Query(0, description="Número de registros a omitir"),
    limit: int = Query(100, description="Número máximo de registros a devolver"),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permissions(["admin:history:view"]))
):
    """
    Obtener registros de acceso al sistema.
    Requiere permiso de administrador para ver el historial del sistema.
    """
    # Construir consulta base
    query = db.query(models.RegistroAcceso)
    
    # Aplicar filtros
    if endpoint:
        query = query.filter(models.RegistroAcceso.endpoint.ilike(f"%{endpoint}%"))
    
    if user_id:
        query = query.filter(models.RegistroAcceso.usuario_id == user_id)
    
    if exitoso is not None:
        query = query.filter(models.RegistroAcceso.exitoso == exitoso)
    
    if desde:
        try:
            desde_dt = datetime.strptime(desde, "%Y-%m-%d")
            query = query.filter(models.RegistroAcceso.fecha >= desde_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha 'desde' inválido. Use YYYY-MM-DD"
            )
    
    if hasta:
        try:
            hasta_dt = datetime.strptime(hasta, "%Y-%m-%d")
            # Añadir un día para incluir todo el día final
            hasta_dt = hasta_dt + timedelta(days=1)
            query = query.filter(models.RegistroAcceso.fecha < hasta_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha 'hasta' inválido. Use YYYY-MM-DD"
            )
    
    if ip_address:
        query = query.filter(models.RegistroAcceso.ip_address == ip_address)
    
    # Ordenar por fecha descendente (más reciente primero)
    query = query.order_by(models.RegistroAcceso.fecha.desc())
    
    # Aplicar paginación
    registros = query.offset(skip).limit(limit).all()
    
    return registros

@router.get("/login-attempts", response_model=List[schemas.IntentosLogin])
async def get_login_attempts(
    email: Optional[str] = Query(None, description="Filtrar por email"),
    exitoso: Optional[bool] = Query(None, description="Filtrar por intentos exitosos o fallidos"),
    desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    ip_address: Optional[str] = Query(None, description="Filtrar por dirección IP"),
    skip: int = Query(0, description="Número de registros a omitir"),
    limit: int = Query(100, description="Número máximo de registros a devolver"),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permissions(["admin:history:view"]))
):
    """
    Obtener registros de intentos de inicio de sesión.
    Requiere permiso de administrador para ver el historial del sistema.
    """
    # Construir consulta base
    query = db.query(models.IntentosLogin)
    
    # Aplicar filtros
    if email:
        query = query.filter(models.IntentosLogin.email.ilike(f"%{email}%"))
    
    if exitoso is not None:
        query = query.filter(models.IntentosLogin.exitoso == exitoso)
    
    if desde:
        try:
            desde_dt = datetime.strptime(desde, "%Y-%m-%d")
            query = query.filter(models.IntentosLogin.fecha >= desde_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha 'desde' inválido. Use YYYY-MM-DD"
            )
    
    if hasta:
        try:
            hasta_dt = datetime.strptime(hasta, "%Y-%m-%d")
            # Añadir un día para incluir todo el día final
            hasta_dt = hasta_dt + timedelta(days=1)
            query = query.filter(models.IntentosLogin.fecha < hasta_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha 'hasta' inválido. Use YYYY-MM-DD"
            )
    
    if ip_address:
        query = query.filter(models.IntentosLogin.ip_address == ip_address)
    
    # Ordenar por fecha descendente (más reciente primero)
    query = query.order_by(models.IntentosLogin.fecha.desc())
    
    # Aplicar paginación
    intentos = query.offset(skip).limit(limit).all()
    
    return intentos

@router.get("/ip-blocks", response_model=List[schemas.BloqueoIP])
async def get_ip_blocks(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo o inactivo"),
    ip_address: Optional[str] = Query(None, description="Filtrar por dirección IP"),
    motivo: Optional[str] = Query(None, description="Filtrar por motivo de bloqueo"),
    skip: int = Query(0, description="Número de registros a omitir"),
    limit: int = Query(100, description="Número máximo de registros a devolver"),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permissions(["admin:history:view"]))
):
    """
    Obtener registros de bloqueos de IP.
    Requiere permiso de administrador para ver el historial del sistema.
    """
    # Construir consulta base
    query = db.query(models.BloqueoIP)
    
    # Aplicar filtros
    if activo is not None:
        query = query.filter(models.BloqueoIP.activo == activo)
    
    if ip_address:
        query = query.filter(models.BloqueoIP.ip_address == ip_address)
    
    if motivo:
        query = query.filter(models.BloqueoIP.motivo == motivo)
    
    # Ordenar por fecha de inicio descendente (más reciente primero)
    query = query.order_by(models.BloqueoIP.fecha_inicio.desc())
    
    # Aplicar paginación
    bloqueos = query.offset(skip).limit(limit).all()
    
    return bloqueos

@router.post("/ip-blocks/{ip_address}/unblock", response_model=schemas.BloqueoIP)
async def unblock_ip(
    ip_address: str,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permissions(["admin:system:config"]))
):
    """
    Desbloquear una IP previamente bloqueada.
    Requiere permiso de administrador para configurar el sistema.
    """
    # Buscar bloqueo activo para esta IP
    bloqueo = db.query(models.BloqueoIP).filter(
        models.BloqueoIP.ip_address == ip_address,
        models.BloqueoIP.activo == True
    ).first()
    
    if not bloqueo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay bloqueo activo para la IP {ip_address}"
        )
    
    # Desactivar bloqueo
    bloqueo.activo = False
    db.commit()
    db.refresh(bloqueo)
    
    return bloqueo
