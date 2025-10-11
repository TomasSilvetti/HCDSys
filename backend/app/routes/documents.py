import os
import shutil
import hashlib
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func

# Configurar logging
logger = logging.getLogger("app.documents")

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

@router.get("/diagnostics/search", response_model=dict)
async def search_diagnostics(
    termino: Optional[str] = Query(None, description="Término de búsqueda para diagnóstico"),
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Ruta de diagnóstico para verificar la funcionalidad de búsqueda.
    Devuelve información detallada sobre el proceso de búsqueda sin ejecutar la consulta completa.
    """
    try:
        logger.info(f"Diagnóstico de búsqueda - Término: {termino}")
        
        # Verificar si el término contiene caracteres especiales
        special_chars = "%_[]^$.|?*+(){}\\"
        has_special_chars = any(c in termino for c in special_chars) if termino else False
        
        # Crear término escapado para demostración
        def escape_like(string):
            if not string:
                return string
            return string.replace('%', '\\%').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]')
        
        termino_escapado = escape_like(termino) if termino else None
        
        # Verificar permisos del usuario
        has_full_access = check_permission(current_user, "docs:view", db)
        has_restricted_access = check_permission(current_user, "search:restricted", db)
        
        # Información de diagnóstico
        diagnostico = {
            "termino_original": termino,
            "termino_escapado": termino_escapado,
            "tiene_caracteres_especiales": has_special_chars,
            "caracteres_especiales_detectados": [c for c in termino if c in special_chars] if termino else [],
            "permisos_usuario": {
                "acceso_completo": has_full_access,
                "acceso_restringido": has_restricted_access,
                "usuario_id": current_user.id,
                "usuario_email": current_user.email,
                "role_id": current_user.role_id
            },
            "configuracion_cors": {
                "origenes_permitidos": settings.CORS_ORIGINS
            },
            "estado": "ok",
            "mensaje": "Diagnóstico completado con éxito"
        }
        
        # Si se proporciona un término, buscar documentos que coincidan (solo conteo)
        if termino:
            try:
                # Crear consulta simplificada para verificar
                query = db.query(func.count(models.Documento.id)).filter(models.Documento.activo == True)
                
                # Aplicar filtro con término escapado
                try:
                    query = query.filter(
                        or_(
                            models.Documento.titulo.ilike(f"%{termino_escapado}%"),
                            models.Documento.numero_expediente.ilike(f"%{termino_escapado}%"),
                            models.Documento.descripcion.ilike(f"%{termino_escapado}%")
                        )
                    )
                    
                    # Ejecutar consulta
                    count = query.scalar()
                    
                    diagnostico["resultados"] = {
                        "conteo": count,
                        "consulta_exitosa": True
                    }
                except Exception as e:
                    logger.error(f"Error en consulta ILIKE de diagnóstico: {str(e)}", exc_info=True)
                    
                    # Intentar con una búsqueda más simple como fallback
                    try:
                        query = db.query(func.count(models.Documento.id)).filter(models.Documento.activo == True)
                        query = query.filter(
                            or_(
                                models.Documento.titulo.contains(termino),
                                models.Documento.numero_expediente.contains(termino),
                                models.Documento.descripcion.contains(termino)
                            )
                        )
                        
                        # Ejecutar consulta
                        count = query.scalar()
                        
                        diagnostico["resultados"] = {
                            "conteo": count,
                            "consulta_exitosa": True,
                            "metodo": "contains (fallback)",
                            "error_ilike": str(e),
                            "tipo_error_ilike": type(e).__name__
                        }
                    except Exception as e2:
                        logger.error(f"Error en consulta contains de diagnóstico: {str(e2)}", exc_info=True)
                        diagnostico["resultados"] = {
                            "conteo": None,
                            "consulta_exitosa": False,
                            "error_ilike": str(e),
                            "tipo_error_ilike": type(e).__name__,
                            "error_contains": str(e2),
                            "tipo_error_contains": type(e2).__name__
                        }
                        diagnostico["estado"] = "error"
                        diagnostico["mensaje"] = "Error al ejecutar consultas de diagnóstico"
                
            except Exception as e:
                logger.error(f"Error en diagnóstico al ejecutar consulta: {str(e)}", exc_info=True)
                diagnostico["resultados"] = {
                    "conteo": None,
                    "consulta_exitosa": False,
                    "error": str(e),
                    "tipo_error": type(e).__name__
                }
                diagnostico["estado"] = "error"
                diagnostico["mensaje"] = "Error al ejecutar consulta de diagnóstico"
        
        # Verificar si hay documentos en la base de datos
        try:
            total_docs = db.query(func.count(models.Documento.id)).scalar()
            diagnostico["total_documentos"] = total_docs
        except Exception as e:
            diagnostico["total_documentos"] = None
            diagnostico["error_conteo_total"] = str(e)
        
        return diagnostico
        
    except Exception as e:
        logger.error(f"Error general en diagnóstico: {str(e)}", exc_info=True)
        return {
            "estado": "error",
            "mensaje": f"Error en diagnóstico: {str(e)}",
            "tipo_error": type(e).__name__,
            "traceback": str(e.__traceback__)
        }

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
        
    logger.info(f"Búsqueda de documentos - Usuario: {current_user.email} - Criterios: termino={termino}, fecha_desde={fecha_desde}, fecha_hasta={fecha_hasta}, categoria_id={categoria_id}, tipo_documento_id={tipo_documento_id}, numero_expediente={numero_expediente}, usuario_id={usuario_id}")
    
    # Iniciar la consulta base - IMPORTANTE: Primero select_from y luego los filtros
    query = db.query(models.Documento).select_from(models.Documento)
    
    # Aplicar filtro base de documentos activos
    query = query.filter(models.Documento.activo == True)
    
    # Aplicar filtros si se proporcionan
    if termino:
        try:
            logger.info(f"Aplicando filtro de búsqueda con término: '{termino}'")
            # Escapar caracteres especiales en el término de búsqueda
            # Usamos una función más robusta para escapar caracteres especiales
            def escape_like(string):
                if not string:
                    return string
                return string.replace('%', '\\%').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]')
            
            termino_seguro = escape_like(termino)
            logger.debug(f"Término de búsqueda escapado: '{termino_seguro}'")
            
            # Usamos la función de texto completo para una búsqueda más robusta
            try:
                query = query.filter(
                    or_(
                        models.Documento.titulo.ilike(f"%{termino_seguro}%"),
                        models.Documento.numero_expediente.ilike(f"%{termino_seguro}%"),
                        models.Documento.descripcion.ilike(f"%{termino_seguro}%")
                    )
                )
            except Exception as e:
                logger.error(f"Error en la consulta ILIKE: {str(e)}", exc_info=True)
                # Intentar con una búsqueda más simple como fallback
                query = query.filter(
                    or_(
                        models.Documento.titulo.contains(termino),
                        models.Documento.numero_expediente.contains(termino),
                        models.Documento.descripcion.contains(termino)
                    )
                )
            logger.debug("Filtro de búsqueda aplicado correctamente")
        except Exception as e:
            logger.error(f"Error al aplicar filtro de término: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al procesar el término de búsqueda: {str(e)}"
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
    has_full_access = check_permission(current_user, "docs:view", db)
    
    # 2. Si no tiene acceso completo, filtrar según restricciones
    if not has_full_access:
        # Obtener documentos creados por el usuario
        user_docs = query.filter(models.Documento.usuario_id == current_user.id)
        
        # Obtener documentos públicos o con acceso según rol
        # Aquí asumimos que los documentos tienen un nivel de acceso basado en roles
        # Si no existe esta estructura, se puede implementar según los requisitos específicos
        
        # Verificar si el usuario tiene permiso de acceso a documentos restringidos
        has_restricted_access = check_permission(current_user, "search:restricted", db)
        
        if has_restricted_access:
            # El usuario puede ver documentos restringidos, pero no clasificados
            # Obtenemos primero los IDs de documentos clasificados
            classified_docs = db.query(models.TipoDocumento.id).filter(
                models.TipoDocumento.nombre.ilike("%clasificado%")
            ).all()
            
            classified_ids = [doc_id for (doc_id,) in classified_docs]
            logger.debug(f"Documentos clasificados encontrados: {classified_ids}")
            
            if classified_ids:
                query = query.filter(
                    or_(
                        models.Documento.usuario_id == current_user.id,  # Documentos propios
                        ~models.Documento.tipo_documento_id.in_(classified_ids)  # No clasificados
                    )
                )
            else:
                logger.debug("No se encontraron documentos clasificados, mostrando todos los documentos")
                query = query.filter(
                    or_(
                        models.Documento.usuario_id == current_user.id,  # Documentos propios
                        True  # Si no hay documentos clasificados, mostrar todos
                    )
                )
        else:
            # El usuario solo puede ver documentos públicos y propios
            # Obtenemos primero los IDs de documentos públicos
            public_docs = db.query(models.TipoDocumento.id).filter(
                models.TipoDocumento.nombre.ilike("%público%")
            ).all()
            
            public_ids = [doc_id for (doc_id,) in public_docs]
            logger.debug(f"Documentos públicos encontrados: {public_ids}")
            
            if public_ids:
                query = query.filter(
                    or_(
                        models.Documento.usuario_id == current_user.id,  # Documentos propios
                        models.Documento.tipo_documento_id.in_(public_ids)  # Documentos públicos
                    )
                )
            else:
                logger.debug("No se encontraron documentos públicos, mostrando solo documentos propios")
                query = query.filter(
                    models.Documento.usuario_id == current_user.id  # Solo documentos propios
                )
    
    # Optimizaciones para mejorar el rendimiento
    
    # 1. Aplicar eager loading para evitar problemas de N+1 queries
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
    count_query = db.query(func.count(models.Documento.id))
    
    # Aplicar los mismos filtros a la consulta de conteo
    if termino:
        try:
            logger.info(f"Aplicando filtro de término a consulta de conteo: '{termino}'")
            # Usar la misma función de escape definida anteriormente
            def escape_like(string):
                if not string:
                    return string
                return string.replace('%', '\\%').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]')
            
            termino_seguro = escape_like(termino)
            logger.debug(f"Término de conteo escapado: '{termino_seguro}'")
            
            try:
                count_query = count_query.filter(
                    or_(
                        models.Documento.titulo.ilike(f"%{termino_seguro}%"),
                        models.Documento.numero_expediente.ilike(f"%{termino_seguro}%"),
                        models.Documento.descripcion.ilike(f"%{termino_seguro}%")
                    )
                )
            except Exception as e:
                logger.error(f"Error en la consulta ILIKE de conteo: {str(e)}", exc_info=True)
                # Intentar con una búsqueda más simple como fallback
                count_query = count_query.filter(
                    or_(
                        models.Documento.titulo.contains(termino),
                        models.Documento.numero_expediente.contains(termino),
                        models.Documento.descripcion.contains(termino)
                    )
                )
            logger.debug("Filtro de término aplicado correctamente a consulta de conteo")
        except Exception as e:
            logger.error(f"Error al aplicar filtro de término en consulta de conteo: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al procesar el término de búsqueda en consulta de conteo: {str(e)}"
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
            ).all()
            
            classified_ids = [doc_id for (doc_id,) in classified_docs]
            
            if classified_ids:
                count_query = count_query.filter(
                    or_(
                        models.Documento.usuario_id == current_user.id,
                        ~models.Documento.tipo_documento_id.in_(classified_ids)
                    )
                )
            else:
                count_query = count_query.filter(
                    or_(
                        models.Documento.usuario_id == current_user.id,
                        True  # Si no hay documentos clasificados, mostrar todos
                    )
                )
        else:
            # Usamos una forma alternativa para el filtro que no depende de .has()
            public_docs = db.query(models.TipoDocumento.id).filter(
                models.TipoDocumento.nombre.ilike("%público%")
            ).all()
            
            public_ids = [doc_id for (doc_id,) in public_docs]
            
            if public_ids:
                count_query = count_query.filter(
                    or_(
                        models.Documento.usuario_id == current_user.id,
                        models.Documento.tipo_documento_id.in_(public_ids)
                    )
                )
            else:
                count_query = count_query.filter(
                    models.Documento.usuario_id == current_user.id  # Solo documentos propios
                )
    
    # Obtener el conteo total
    try:
        logger.debug("Ejecutando consulta de conteo...")
        # Registrar la consulta SQL para depuración
        query_str = str(count_query.statement.compile(compile_kwargs={"literal_binds": True}))
        logger.debug(f"SQL de consulta de conteo: {query_str}")
        
        total_items = count_query.scalar()
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
        logger.info(f"Búsqueda completada - Total de documentos encontrados: {total_items}, páginas: {total_pages}")
    except Exception as e:
        logger.error(f"Error al obtener el conteo total: {str(e)}", exc_info=True)
        # Registrar detalles adicionales del error
        logger.error(f"Tipo de error: {type(e).__name__}")
        logger.error(f"Parámetros de búsqueda: termino={termino}, categoria_id={categoria_id}, tipo_documento_id={tipo_documento_id}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la búsqueda: {str(e)}"
        )
    
    # Aplicar paginación
    try:
        logger.debug(f"Aplicando paginación: página {page}, tamaño {page_size}")
        skip = (page - 1) * page_size
        logger.debug(f"Saltando {skip} registros")
        
        # Registrar la consulta SQL para depuración
        query_str = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        logger.debug(f"SQL de consulta principal: {query_str}")
        
        documentos = query.offset(skip).limit(page_size).all()
        logger.debug(f"Documentos recuperados: {len(documentos)}")
        
        # Log de IDs de documentos recuperados para depuración
        doc_ids = [doc.id for doc in documentos]
        logger.debug(f"IDs de documentos recuperados: {doc_ids}")
    except Exception as e:
        logger.error(f"Error al recuperar documentos: {str(e)}", exc_info=True)
        # Registrar detalles adicionales del error
        logger.error(f"Tipo de error: {type(e).__name__}")
        logger.error(f"Parámetros de paginación: page={page}, page_size={page_size}, skip={skip if 'skip' in locals() else 'N/A'}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar documentos: {str(e)}"
        )
    
    # Registrar la búsqueda en el historial
    try:
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
            logger.error(f"Error al registrar la búsqueda en el historial: {str(e)}", exc_info=True)
            # Continuamos sin lanzar excepción para no interrumpir la respuesta al usuario
    except Exception as e:
        logger.error(f"Error al procesar el historial de búsqueda: {str(e)}", exc_info=True)
        # Continuamos sin lanzar excepción para no interrumpir la respuesta al usuario
    
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

@router.get("/{documento_id}/download")
async def download_document(
    documento_id: int,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Descargar un documento por su ID.
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
    has_permission = check_permission(current_user, "docs:download", db)
    
    if not (is_owner or has_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para descargar este documento"
        )
    
    # Verificar que el archivo existe
    if not os.path.exists(documento.path_archivo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    # Registrar la acción en el historial
    historial = models.HistorialAcceso(
        usuario_id=current_user.id,
        documento_id=documento_id,
        accion="descarga",
        detalles="Descarga del documento"
    )
    db.add(historial)
    db.commit()
    
    # Obtener nombre original del archivo
    filename = f"{documento.titulo}{documento.extension_archivo}"
    
    return FileResponse(
        path=documento.path_archivo,
        filename=filename,
        media_type="application/octet-stream"
    )

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
    has_permission = check_permission(current_user, "docs:view", db) or check_permission(current_user, "search:restricted", db)
    
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
    has_permission = check_permission(current_user, "docs:view", db) or check_permission(current_user, "search:restricted", db)
    
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
    has_permission = check_permission(current_user, "docs:download", db)
    
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

@router.post("/{documento_id}/versions", response_model=schemas.VersionDocumento)
async def create_document_version(
    documento_id: int,
    archivo: UploadFile = File(...),
    titulo: Optional[str] = Form(None),
    numero_expediente: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    categoria_id: Optional[int] = Form(None),
    tipo_documento_id: Optional[int] = Form(None),
    comentario: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crear una nueva versión de un documento existente.
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
    has_permission = check_permission(current_user, "docs:edit", db)
    
    if not (is_owner or has_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para editar este documento"
        )
    
    # Verificar tipo de documento si se proporciona
    if tipo_documento_id:
        tipo_documento = db.query(models.TipoDocumento).filter(
            models.TipoDocumento.id == tipo_documento_id
        ).first()
        
        if not tipo_documento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de documento no válido"
            )
    else:
        # Usar el tipo de documento actual
        tipo_documento_id = documento.tipo_documento_id
        tipo_documento = db.query(models.TipoDocumento).filter(
            models.TipoDocumento.id == tipo_documento_id
        ).first()
    
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
    
    version_id = None
    
    try:
        # Crear nueva versión del documento
        success, message, version_id = await StorageService.create_document_version(
            archivo,
            documento_id,
            current_user.id,
            db,
            comentario
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        # Actualizar metadatos del documento si se proporcionan
        if titulo or numero_expediente or descripcion or categoria_id:
            try:
                if titulo:
                    documento.titulo = titulo
                if numero_expediente:
                    documento.numero_expediente = numero_expediente
                if descripcion is not None:
                    documento.descripcion = descripcion
                if categoria_id is not None:
                    documento.categoria_id = categoria_id
                
                documento.fecha_modificacion = datetime.utcnow()
                db.commit()
            except Exception as metadata_error:
                logger.error(f"Error al actualizar metadatos: {str(metadata_error)}")
                # No lanzar excepción, la versión ya se creó correctamente
        
            # Obtener la versión creada con relaciones necesarias para el esquema de respuesta
            version = db.query(models.VersionDocumento).filter(
                models.VersionDocumento.id == version_id
            ).first()
            
            if not version:
                logger.error(f"Versión creada con ID {version_id} pero no se puede recuperar")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Versión creada pero no se puede recuperar: {message}"
                )
                
            # Crear una respuesta simplificada que cumpla con el esquema
            # Esto evita los errores de validación cuando version_siguiente es None
            response_version = {
                "id": version.id,
                "documento_id": version.documento_id,
                "numero_version": version.numero_version,
                "fecha_version": version.fecha_version,
                "comentario": version.comentario,
                "cambios": version.cambios,
                "path_archivo": version.path_archivo,
                "usuario_id": version.usuario_id,
                "usuario": version.usuario,
                "hash_archivo": version.hash_archivo,
                "tamano_archivo": version.tamano_archivo,
                "extension_archivo": version.extension_archivo,
                "es_actual": version.es_actual,
                "version_anterior_id": version.version_anterior_id,
                "version_anterior": None,
                "version_siguiente": None,
                "documento": documento
            }
            
            # Programar verificación de integridad en segundo plano
            if background_tasks:
                try:
                    from ..utils.tasks import verify_document_integrity
                    background_tasks.add_task(verify_document_integrity, db, documento_id)
                except Exception as bg_error:
                    logger.error(f"Error al programar tarea en segundo plano: {str(bg_error)}")
                    # No lanzar excepción, la versión ya se creó correctamente
            
            return response_version
        
    except HTTPException as http_ex:
        # Re-lanzar excepciones HTTP
        raise http_ex
        
    except Exception as e:
        logger.error(f"Error al crear versión: {str(e)}")
        
        # Si ya se creó la versión en la base de datos pero ocurrió un error posterior
        if version_id is not None:
            logger.warning(f"Se creó la versión con ID {version_id} pero ocurrió un error posterior")
            
            # Intentar recuperar la versión creada
            try:
                version = db.query(models.VersionDocumento).filter(
                    models.VersionDocumento.id == version_id
                ).first()
                
                if version:
                    # Registrar advertencia en el historial
                    try:
                        historial = models.HistorialAcceso(
                            usuario_id=current_user.id,
                            documento_id=documento_id,
                            accion="nueva_version_con_advertencia",
                            detalles=f"Nueva versión creada con advertencias: {str(e)}"
                        )
                        db.add(historial)
                        db.commit()
                    except:
                        db.rollback()
                    
                    # Crear respuesta simplificada que cumpla con el esquema
                    response_version = {
                        "id": version.id,
                        "documento_id": version.documento_id,
                        "numero_version": version.numero_version,
                        "fecha_version": version.fecha_version,
                        "comentario": version.comentario,
                        "cambios": version.cambios,
                        "path_archivo": version.path_archivo,
                        "usuario_id": version.usuario_id,
                        "usuario": version.usuario,
                        "hash_archivo": version.hash_archivo,
                        "tamano_archivo": version.tamano_archivo,
                        "extension_archivo": version.extension_archivo,
                        "es_actual": version.es_actual,
                        "version_anterior_id": version.version_anterior_id,
                        "version_anterior": None,
                        "version_siguiente": None,
                        "documento": documento
                    }
                    
                    # Devolver la versión creada a pesar del error
                    return response_version
            except Exception as recovery_error:
                logger.error(f"Error al recuperar versión creada: {str(recovery_error)}")
        
        # Si llegamos aquí, es un error completo
        try:
            db.rollback()
            
            # Registrar error
            error_log = models.ErrorAlmacenamiento(
                documento_id=documento_id,
                usuario_id=current_user.id,
                tipo_error="version",
                mensaje_error=f"Error al crear versión: {str(e)}"
            )
            db.add(error_log)
            db.commit()
        except Exception as log_error:
            logger.error(f"Error al registrar error: {str(log_error)}")
            try:
                db.rollback()
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear versión: {str(e)}"
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
    has_permission = check_permission(current_user, "docs:edit", db)
    
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
    has_permission = check_permission(current_user, "docs:view", db) or check_permission(current_user, "search:restricted", db)
    
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
    has_permission = check_permission(current_user, "docs:edit", db)
    
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
        detalles="Edición de metadatos del documento"
    )
    db.add(historial)
    db.commit()
    
    return documento
