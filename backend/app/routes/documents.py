import os
import shutil
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func

from ..db import models, schemas
from ..db.database import get_db
from ..utils.security import get_current_active_user, check_permission
from ..utils.config import settings
from ..utils.storage import StorageService

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/categories", response_model=List[schemas.Categoria])
async def get_document_categories(
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las categorías de documentos disponibles.
    """
    categorias = db.query(models.Categoria).all()
    return categorias

@router.get("/types", response_model=List[schemas.TipoDocumento])
async def get_document_types(
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los tipos de documentos disponibles.
    """
    tipos = db.query(models.TipoDocumento).all()
    return tipos

@router.get("/", response_model=schemas.PaginatedResponse)
async def search_documents(
    termino: Optional[str] = Query(None, description="Término de búsqueda (título o número de expediente)"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    categoria_id: Optional[int] = Query(None, description="ID de categoría"),
    tipo_documento_id: Optional[int] = Query(None, description="ID de tipo de documento"),
    numero_expediente: Optional[str] = Query(None, description="Número de expediente exacto"),
    usuario_id: Optional[int] = Query(None, description="ID del usuario que cargó el documento"),
    sort_by: str = Query("fecha_modificacion", description="Campo para ordenar los resultados"),
    sort_order: str = Query("desc", description="Orden de los resultados (asc, desc)"),
    page: int = Query(1, description="Número de página", ge=1),
    page_size: int = Query(10, description="Tamaño de página", ge=1, le=100),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Buscar documentos con filtros opcionales y paginación.
    Los usuarios solo pueden ver documentos a los que tienen acceso según su rol.
    
    - **termino**: Busca en título, número de expediente y descripción
    - **fecha_desde/fecha_hasta**: Filtra por rango de fechas (formato YYYY-MM-DD)
    - **categoria_id/tipo_documento_id**: Filtra por categoría o tipo de documento
    - **numero_expediente**: Filtra por número de expediente exacto
    - **usuario_id**: Filtra por usuario que cargó el documento
    - **sort_by/sort_order**: Controla el ordenamiento de los resultados
    - **page/page_size**: Controla la paginación de resultados
    """
    # Validación de parámetros
    if not termino and not fecha_desde and not fecha_hasta and not categoria_id and not tipo_documento_id and not numero_expediente and not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un criterio de búsqueda"
        )
    
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
        
    # Filtro exacto por número de expediente
    if numero_expediente:
        query = query.filter(models.Documento.numero_expediente == numero_expediente)
        
    # Filtro por usuario que cargó el documento
    if usuario_id:
        query = query.filter(models.Documento.usuario_id == usuario_id)
    
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
        # Verificar que la categoría existe
        categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Categoría con ID {categoria_id} no encontrada"
            )
        query = query.filter(models.Documento.categoria_id == categoria_id)
    
    if tipo_documento_id:
        # Verificar que el tipo de documento existe
        tipo_documento = db.query(models.TipoDocumento).filter(models.TipoDocumento.id == tipo_documento_id).first()
        if not tipo_documento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de documento con ID {tipo_documento_id} no encontrado"
            )
        query = query.filter(models.Documento.tipo_documento_id == tipo_documento_id)
    
    # Filtrar por permisos de acceso
    # 1. Verificar si el usuario tiene permiso de acceso a todos los documentos
    has_full_access = check_permission(current_user, "DOCUMENT_VIEW_ALL", db)
    
    # 2. Si no tiene acceso completo, filtrar según restricciones
    if not has_full_access:
        # Obtener documentos creados por el usuario
        user_docs = query.filter(models.Documento.usuario_id == current_user.id)
        
        # Obtener documentos públicos o con acceso según rol
        # Aquí asumimos que los documentos tienen un nivel de acceso basado en roles
        # Si no existe esta estructura, se puede implementar según los requisitos específicos
        
        # Verificar si el usuario tiene permiso de acceso a documentos restringidos
        has_restricted_access = check_permission(current_user, "DOCUMENT_VIEW_RESTRICTED", db)
        
        if has_restricted_access:
            # El usuario puede ver documentos restringidos, pero no clasificados
            # Usamos una forma alternativa para el filtro que no depende de .has()
            classified_docs = db.query(models.TipoDocumento.id).filter(
                models.TipoDocumento.nombre.ilike("%clasificado%")
            ).subquery()
            
            query = query.filter(
                or_(
                    models.Documento.usuario_id == current_user.id,  # Documentos propios
                    ~models.Documento.tipo_documento_id.in_(classified_docs)  # No clasificados
                )
            )
        else:
            # El usuario solo puede ver documentos públicos y propios
            # Usamos una forma alternativa para el filtro que no depende de .has()
            public_docs = db.query(models.TipoDocumento.id).filter(
                models.TipoDocumento.nombre.ilike("%público%")
            ).subquery()
            
            query = query.filter(
                or_(
                    models.Documento.usuario_id == current_user.id,  # Documentos propios
                    models.Documento.tipo_documento_id.in_(public_docs)  # Documentos públicos
                )
            )
    
    # Optimizaciones para mejorar el rendimiento
    
    # 1. Usar select_from para hacer joins explícitos y mejorar el rendimiento
    query = query.select_from(models.Documento)
    
    # 2. Aplicar eager loading para evitar problemas de N+1 queries
    query = query.options(
        joinedload(models.Documento.categoria),
        joinedload(models.Documento.tipo_documento),
        joinedload(models.Documento.usuario)
    )
    
    # 3. Ordenar según los parámetros proporcionados
    sort_column = None
    
    # Determinar la columna de ordenamiento
    if sort_by == "titulo":
        sort_column = models.Documento.titulo
    elif sort_by == "numero_expediente":
        sort_column = models.Documento.numero_expediente
    elif sort_by == "fecha_creacion":
        sort_column = models.Documento.fecha_creacion
    elif sort_by == "categoria_id":
        sort_column = models.Documento.categoria_id
    elif sort_by == "tipo_documento_id":
        sort_column = models.Documento.tipo_documento_id
    else:
        # Por defecto, ordenar por fecha de modificación
        sort_column = models.Documento.fecha_modificacion
    
    # Aplicar el orden
    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Calcular total de resultados para la paginación
    # Usar una consulta separada y optimizada solo para contar
    count_query = db.query(func.count(models.Documento.id)).select_from(models.Documento)
    
    # Aplicar los mismos filtros a la consulta de conteo
    if termino:
        count_query = count_query.filter(
            or_(
                models.Documento.titulo.ilike(f"%{termino}%"),
                models.Documento.numero_expediente.ilike(f"%{termino}%"),
                models.Documento.descripcion.ilike(f"%{termino}%")
            )
        )
        
    # Filtro exacto por número de expediente
    if numero_expediente:
        count_query = count_query.filter(models.Documento.numero_expediente == numero_expediente)
        
    # Filtro por usuario que cargó el documento
    if usuario_id:
        count_query = count_query.filter(models.Documento.usuario_id == usuario_id)
    
    if fecha_desde and 'fecha_desde_dt' in locals():
        count_query = count_query.filter(models.Documento.fecha_creacion >= fecha_desde_dt)
    
    if fecha_hasta and 'fecha_hasta_dt' in locals():
        count_query = count_query.filter(models.Documento.fecha_creacion <= fecha_hasta_dt)
    
    if categoria_id:
        count_query = count_query.filter(models.Documento.categoria_id == categoria_id)
    
    if tipo_documento_id:
        count_query = count_query.filter(models.Documento.tipo_documento_id == tipo_documento_id)
    
    # Aplicar filtros de permisos a la consulta de conteo
    if not has_full_access:
        if has_restricted_access:
            # Usamos una forma alternativa para el filtro que no depende de .has()
            classified_docs = db.query(models.TipoDocumento.id).filter(
                models.TipoDocumento.nombre.ilike("%clasificado%")
            ).subquery()
            
            count_query = count_query.filter(
                or_(
                    models.Documento.usuario_id == current_user.id,
                    ~models.Documento.tipo_documento_id.in_(classified_docs)
                )
            )
        else:
            # Usamos una forma alternativa para el filtro que no depende de .has()
            public_docs = db.query(models.TipoDocumento.id).filter(
                models.TipoDocumento.nombre.ilike("%público%")
            ).subquery()
            
            count_query = count_query.filter(
                or_(
                    models.Documento.usuario_id == current_user.id,
                    models.Documento.tipo_documento_id.in_(public_docs)
                )
            )
    
    # Obtener el conteo total
    total_items = count_query.scalar()
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
    
    # Aplicar paginación
    skip = (page - 1) * page_size
    documentos = query.offset(skip).limit(page_size).all()
    
    # Registrar la búsqueda en el historial
    for doc in documentos:
        historial = models.HistorialAcceso(
            usuario_id=current_user.id,
            documento_id=doc.id,
            accion="busqueda",
            detalles=f"Búsqueda: {termino if termino else 'filtrada'}, página {page}"
        )
        db.add(historial)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar la búsqueda: {str(e)}"
        )
    
    # Construir respuesta paginada
    return {
        "total": total_items,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": documentos
    }

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
    background_tasks: BackgroundTasks = None,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo documento.
    Solo usuarios con permiso de gestión de documentos pueden crear documentos.
    Implementa verificación de integridad y sistema de rollback en caso de errores.
    """
    # Verificar permiso
    if not check_permission(current_user, "docs:create", db):
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
    
    # Calcular hash del archivo para verificación de integridad
    file_hash = hashlib.sha256(contents).hexdigest()
    
    # Crear el documento en la base de datos
    new_document = models.Documento(
        titulo=titulo,
        numero_expediente=numero_expediente,
        descripcion=descripcion,
        categoria_id=categoria_id,
        tipo_documento_id=tipo_documento_id,
        usuario_id=current_user.id,
        path_archivo="",  # Se actualizará después de guardar el archivo
        hash_archivo=file_hash,
        tamano_archivo=file_size,
        extension_archivo=file_extension,
        fecha_ultima_verificacion=datetime.utcnow(),
        estado_integridad=True,
        activo=True
    )
    
    try:
        # Iniciar transacción
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        
        # Usar el servicio de almacenamiento para guardar el archivo
        success, message, metadata = await StorageService.save_document(
            archivo, new_document.id, current_user.id, db
        )
        
        if not success:
            # Si falla el guardado, hacer rollback y lanzar excepción
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar el archivo: {message}"
            )
        
        # Actualizar metadatos del documento
        for key, value in metadata.items():
            setattr(new_document, key, value)
        
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
        
        # Programar verificación de integridad en segundo plano
        if background_tasks:
            from ..utils.tasks import verify_document_integrity
            background_tasks.add_task(verify_document_integrity, db, new_document.id)
        
        return new_document
        
    except HTTPException as http_ex:
        # Re-lanzar excepciones HTTP
        raise http_ex
        
    except Exception as e:
        # Hacer rollback en caso de error
        db.rollback()
        
        # Registrar el error
        error_log = models.ErrorAlmacenamiento(
            documento_id=None,  # No tenemos ID porque falló antes de commit
            usuario_id=current_user.id,
            tipo_error="db",
            mensaje_error=f"Error al crear documento: {str(e)}"
        )
        
        try:
            db.add(error_log)
            db.commit()
        except:
            db.rollback()
        
        # Eliminar archivos parcialmente guardados si existen
        try:
            document_dir = os.path.join(settings.DOCUMENT_STORAGE_PATH, str(new_document.id))
            if os.path.exists(document_dir):
                shutil.rmtree(document_dir)
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear documento: {str(e)}"
        )

# Endpoints para gestión de versiones de documentos
@router.get("/{documento_id}/versions", response_model=List[schemas.VersionDocumentoSimple])
async def get_document_versions(
    documento_id: int,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las versiones de un documento.
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
    
    # Verificar permisos para ver el documento
    is_owner = documento.usuario_id == current_user.id
    has_permission = check_permission(current_user, "DOCUMENT_VIEW_ALL", db) or check_permission(current_user, "DOCUMENT_VIEW_RESTRICTED", db)
    
    if not (is_owner or has_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este documento"
        )
    
    # Obtener todas las versiones del documento
    versiones = db.query(models.VersionDocumento).filter(
        models.VersionDocumento.documento_id == documento_id
    ).order_by(models.VersionDocumento.numero_version.desc()).all()
    
    # Registrar la acción en el historial
    historial = models.HistorialAcceso(
        usuario_id=current_user.id,
        documento_id=documento_id,
        accion="consulta_versiones",
        detalles="Consulta de historial de versiones"
    )
    db.add(historial)
    db.commit()
    
    return versiones

@router.get("/{documento_id}/versions/{version_id}", response_model=schemas.VersionDocumento)
async def get_document_version(
    documento_id: int,
    version_id: int,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener una versión específica de un documento.
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
    
    # Verificar permisos para ver el documento
    is_owner = documento.usuario_id == current_user.id
    has_permission = check_permission(current_user, "DOCUMENT_VIEW_ALL", db) or check_permission(current_user, "DOCUMENT_VIEW_RESTRICTED", db)
    
    if not (is_owner or has_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este documento"
        )
    
    # Obtener la versión específica
    version = db.query(models.VersionDocumento).filter(
        models.VersionDocumento.documento_id == documento_id,
        models.VersionDocumento.id == version_id
    ).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Versión no encontrada"
        )
    
    # Registrar la acción en el historial
    historial = models.HistorialAcceso(
        usuario_id=current_user.id,
        documento_id=documento_id,
        accion="consulta_version",
        detalles=f"Consulta de la versión {version.numero_version}"
    )
    db.add(historial)
    db.commit()
    
    return version

@router.get("/{documento_id}/versions/{version_id}/download")
async def download_document_version(
    documento_id: int,
    version_id: int,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Descargar una versión específica de un documento.
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
    
    # Verificar permisos para descargar el documento
    is_owner = documento.usuario_id == current_user.id
    has_permission = check_permission(current_user, "DOCUMENT_DOWNLOAD", db)
    
    if not (is_owner or has_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para descargar este documento"
        )
    
    # Obtener la versión específica
    version = db.query(models.VersionDocumento).filter(
        models.VersionDocumento.documento_id == documento_id,
        models.VersionDocumento.id == version_id
    ).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Versión no encontrada"
        )
    
    # Verificar que el archivo existe
    if not os.path.exists(version.path_archivo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    # Registrar la acción en el historial
    historial = models.HistorialAcceso(
        usuario_id=current_user.id,
        documento_id=documento_id,
        accion="descarga_version",
        detalles=f"Descarga de la versión {version.numero_version}"
    )
    db.add(historial)
    db.commit()
    
    # Obtener nombre original del archivo
    filename = f"{documento.titulo}_v{version.numero_version}{version.extension_archivo}"
    
    return FileResponse(
        path=version.path_archivo,
        filename=filename,
        media_type="application/octet-stream"
    )

@router.post("/{documento_id}/versions/{version_id}/restore", response_model=schemas.Documento)
async def restore_document_version(
    documento_id: int,
    version_id: int,
    comentario: Optional[str] = Form(None),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Restaurar una versión específica de un documento, creando una nueva versión.
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
    
    # Verificar permisos para editar el documento
    is_owner = documento.usuario_id == current_user.id
    has_permission = check_permission(current_user, "DOCUMENT_EDIT", db)
    
    if not (is_owner or has_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para editar este documento"
        )
    
    # Restaurar la versión
    success, message, version_id = StorageService.restore_version(
        document_id=documento_id,
        version_id=version_id,
        user_id=current_user.id,
        db=db,
        comentario=comentario
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    # Obtener el documento actualizado
    db.refresh(documento)
    
    return documento

@router.post("/{documento_id}/versions/compare")
async def compare_document_versions(
    documento_id: int,
    version_id1: int,
    version_id2: int,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Comparar dos versiones de un documento.
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
    
    # Verificar permisos para ver el documento
    is_owner = documento.usuario_id == current_user.id
    has_permission = check_permission(current_user, "DOCUMENT_VIEW_ALL", db) or check_permission(current_user, "DOCUMENT_VIEW_RESTRICTED", db)
    
    if not (is_owner or has_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este documento"
        )
    
    # Comparar versiones
    success, message, result = StorageService.compare_versions(
        document_id=documento_id,
        version_id1=version_id1,
        version_id2=version_id2,
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    # Registrar la acción en el historial
    historial = models.HistorialAcceso(
        usuario_id=current_user.id,
        documento_id=documento_id,
        accion="comparacion_versiones",
        detalles=f"Comparación de las versiones {version_id1} y {version_id2}"
    )
    db.add(historial)
    db.commit()
    
    return result

@router.put("/{documento_id}", response_model=schemas.Documento)
async def update_document(
    documento_id: int,
    documento_update: schemas.DocumentoUpdate,
    file: Optional[UploadFile] = None,
    comentario: Optional[str] = Form(None),
    cambios: Optional[str] = Form(None),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un documento existente.
    Solo el creador del documento o usuarios con permisos de administrador pueden editar documentos.
    Si se proporciona un archivo, se crea una nueva versión del documento.
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
    
    # Si se proporciona un archivo, crear una nueva versión
    if file:
        # Verificar tipo de documento
        tipo_documento = db.query(models.TipoDocumento).filter(
            models.TipoDocumento.id == documento.tipo_documento_id
        ).first()
        
        if not tipo_documento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de documento no válido"
            )
        
        # Verificar extensión del archivo
        file_extension = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = tipo_documento.extensiones_permitidas.split(",")
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extensión de archivo no permitida. Extensiones permitidas: {tipo_documento.extensiones_permitidas}"
            )
        
        # Crear nueva versión
        success, message, version_id = await StorageService.create_document_version(
            file=file,
            document_id=documento_id,
            user_id=current_user.id,
            db=db,
            comentario=comentario,
            cambios=cambios
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
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
    
    # Actualizar fecha de modificación si no se actualizó con una nueva versión
    if not file:
        documento.fecha_modificacion = datetime.utcnow()
    
    db.commit()
    db.refresh(documento)
    
    # Registrar la acción en el historial si no se registró al crear la versión
    if not file:
        historial = models.HistorialAcceso(
            usuario_id=current_user.id,
            documento_id=documento.id,
            accion="edicion",
            detalles="Edición de metadatos del documento"
        )
        db.add(historial)
        db.commit()
    
    return documento
