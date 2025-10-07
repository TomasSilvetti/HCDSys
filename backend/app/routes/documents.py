import os
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ..db import models, schemas
from ..db.database import get_db
from ..utils.security import get_current_active_user, check_permission
from ..utils.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/", response_model=List[schemas.Documento])
async def search_documents(
    termino: Optional[str] = Query(None, description="Término de búsqueda (título o número de expediente)"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    categoria_id: Optional[int] = Query(None, description="ID de categoría"),
    tipo_documento_id: Optional[int] = Query(None, description="ID de tipo de documento"),
    skip: int = Query(0, description="Número de resultados a omitir"),
    limit: int = Query(10, description="Número máximo de resultados"),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Buscar documentos con filtros opcionales.
    Los usuarios solo pueden ver documentos a los que tienen acceso según su rol.
    """
    # Iniciar la consulta base
    query = db.query(models.Documento).filter(models.Documento.activo == True)
    
    # Aplicar filtros si se proporcionan
    if termino:
        query = query.filter(
            or_(
                models.Documento.titulo.ilike(f"%{termino}%"),
                models.Documento.numero_expediente.ilike(f"%{termino}%"),
                models.Documento.descripcion.ilike(f"%{termino}%")
            )
        )
    
    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, "%Y-%m-%d")
            query = query.filter(models.Documento.fecha_creacion >= fecha_desde_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha_desde inválido. Use YYYY-MM-DD"
            )
    
    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d")
            query = query.filter(models.Documento.fecha_creacion <= fecha_hasta_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha_hasta inválido. Use YYYY-MM-DD"
            )
    
    if categoria_id:
        query = query.filter(models.Documento.categoria_id == categoria_id)
    
    if tipo_documento_id:
        query = query.filter(models.Documento.tipo_documento_id == tipo_documento_id)
    
    # Aplicar paginación
    documentos = query.offset(skip).limit(limit).all()
    
    # Registrar la búsqueda en el historial
    for doc in documentos:
        historial = models.HistorialAcceso(
            usuario_id=current_user.id,
            documento_id=doc.id,
            accion="busqueda",
            detalles=f"Búsqueda: {termino if termino else 'todos'}"
        )
        db.add(historial)
    
    db.commit()
    
    return documentos

@router.get("/{documento_id}", response_model=schemas.Documento)
async def get_document(
    documento_id: int,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un documento por su ID.
    """
    documento = db.query(models.Documento).filter(
        models.Documento.id == documento_id,
        models.Documento.activo == True
    ).first()
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Registrar la visualización en el historial
    historial = models.HistorialAcceso(
        usuario_id=current_user.id,
        documento_id=documento.id,
        accion="visualizacion",
        detalles="Visualización de detalle de documento"
    )
    db.add(historial)
    db.commit()
    
    return documento

@router.post("/", response_model=schemas.Documento)
async def create_document(
    titulo: str = Form(...),
    numero_expediente: str = Form(...),
    descripcion: Optional[str] = Form(None),
    categoria_id: Optional[int] = Form(None),
    tipo_documento_id: int = Form(...),
    archivo: UploadFile = File(...),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo documento.
    Solo usuarios con permiso de gestión de documentos pueden crear documentos.
    """
    # Verificar permiso
    if not check_permission(current_user, "DOCUMENT_CREATE", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear documentos"
        )
    
    # Verificar si ya existe un documento con el mismo título
    existing_doc = db.query(models.Documento).filter(
        models.Documento.titulo == titulo,
        models.Documento.activo == True
    ).first()
    
    if existing_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un documento con ese título"
        )
    
    # Verificar tipo de documento
    tipo_documento = db.query(models.TipoDocumento).filter(
        models.TipoDocumento.id == tipo_documento_id
    ).first()
    
    if not tipo_documento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de documento no válido"
        )
    
    # Verificar extensión del archivo
    file_extension = os.path.splitext(archivo.filename)[1].lower()
    allowed_extensions = tipo_documento.extensiones_permitidas.split(",")
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Extensiones permitidas: {tipo_documento.extensiones_permitidas}"
        )
    
    # Verificar tamaño del archivo
    file_size = 0
    contents = await archivo.read()
    file_size = len(contents)
    await archivo.seek(0)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo excede el tamaño máximo permitido ({settings.MAX_UPLOAD_SIZE / 1024 / 1024} MB)"
        )
    
    # Crear el documento en la base de datos
    new_document = models.Documento(
        titulo=titulo,
        numero_expediente=numero_expediente,
        descripcion=descripcion,
        categoria_id=categoria_id,
        tipo_documento_id=tipo_documento_id,
        usuario_id=current_user.id,
        path_archivo="",  # Se actualizará después de guardar el archivo
        activo=True
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    # Crear directorio de almacenamiento si no existe
    document_dir = os.path.join(settings.DOCUMENT_STORAGE_PATH, str(new_document.id))
    os.makedirs(document_dir, exist_ok=True)
    
    # Guardar el archivo
    file_path = os.path.join(document_dir, f"{new_document.id}{file_extension}")
    with open(file_path, "wb") as buffer:
        buffer.write(contents)
    
    # Actualizar la ruta del archivo en la base de datos
    new_document.path_archivo = file_path
    db.commit()
    db.refresh(new_document)
    
    # Registrar la acción en el historial
    historial = models.HistorialAcceso(
        usuario_id=current_user.id,
        documento_id=new_document.id,
        accion="creacion",
        detalles="Creación de documento"
    )
    db.add(historial)
    db.commit()
    
    return new_document

@router.put("/{documento_id}", response_model=schemas.Documento)
async def update_document(
    documento_id: int,
    documento_update: schemas.DocumentoUpdate,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un documento existente.
    Solo el creador del documento o usuarios con permisos de administrador pueden editar documentos.
    """
    # Verificar si el documento existe
    documento = db.query(models.Documento).filter(
        models.Documento.id == documento_id,
        models.Documento.activo == True
    ).first()
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos
    is_owner = documento.usuario_id == current_user.id
    has_permission = check_permission(current_user, "DOCUMENT_EDIT", db)
    
    if not (is_owner or has_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para editar este documento"
        )
    
    # Verificar si el nuevo título ya existe (si se está actualizando)
    if documento_update.titulo and documento_update.titulo != documento.titulo:
        existing_doc = db.query(models.Documento).filter(
            models.Documento.titulo == documento_update.titulo,
            models.Documento.id != documento_id,
            models.Documento.activo == True
        ).first()
        
        if existing_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un documento con ese título"
            )
    
    # Actualizar campos
    if documento_update.titulo:
        documento.titulo = documento_update.titulo
    if documento_update.numero_expediente:
        documento.numero_expediente = documento_update.numero_expediente
    if documento_update.descripcion is not None:
        documento.descripcion = documento_update.descripcion
    if documento_update.categoria_id is not None:
        documento.categoria_id = documento_update.categoria_id
    if documento_update.tipo_documento_id:
        documento.tipo_documento_id = documento_update.tipo_documento_id
    if documento_update.activo is not None:
        documento.activo = documento_update.activo
    
    # Actualizar fecha de modificación
    documento.fecha_modificacion = datetime.utcnow()
    
    db.commit()
    db.refresh(documento)
    
    # Registrar la acción en el historial
    historial = models.HistorialAcceso(
        usuario_id=current_user.id,
        documento_id=documento.id,
        accion="edicion",
        detalles="Edición de documento"
    )
    db.add(historial)
    db.commit()
    
    return documento
