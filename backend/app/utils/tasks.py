import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..db import models
from ..utils.storage import StorageService

# Configurar logging
logger = logging.getLogger(__name__)

async def verify_document_integrity(db: Session, document_id: int = None):
    """
    Tarea en segundo plano para verificar la integridad de los documentos.
    
    Args:
        db: Sesión de base de datos
        document_id: ID específico de documento a verificar. Si es None, verifica todos los documentos
                    que no han sido verificados en el último día.
    """
    try:
        if document_id:
            # Verificar documento específico
            success, message = StorageService.verify_document_integrity(document_id, db)
            logger.info(f"Verificación de documento {document_id}: {message}")
            return
        
        # Obtener documentos que no han sido verificados en el último día
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        documentos = db.query(models.Documento).filter(
            models.Documento.activo == True,
            models.Documento.fecha_ultima_verificacion < one_day_ago
        ).all()
        
        logger.info(f"Iniciando verificación de integridad de {len(documentos)} documentos")
        
        for documento in documentos:
            success, message = StorageService.verify_document_integrity(documento.id, db)
            if not success:
                logger.warning(f"Documento {documento.id}: {message}")
                
                # Crear respaldo automático si falla la verificación
                backup_success, backup_message, backup_path = StorageService.create_backup(documento.id, db)
                if backup_success:
                    logger.info(f"Respaldo creado para documento {documento.id}: {backup_path}")
                else:
                    logger.error(f"Error al crear respaldo para documento {documento.id}: {backup_message}")
        
        logger.info("Verificación de integridad completada")
        
    except Exception as e:
        logger.error(f"Error en verificación de integridad: {str(e)}")

async def cleanup_old_backups(db: Session, days_to_keep: int = 30):
    """
    Tarea en segundo plano para eliminar respaldos antiguos.
    
    Args:
        db: Sesión de base de datos
        days_to_keep: Número de días a mantener los respaldos
    """
    import os
    from pathlib import Path
    from ..utils.config import settings
    
    try:
        backup_dir = os.path.join(settings.DOCUMENT_STORAGE_PATH, "backups")
        if not os.path.exists(backup_dir):
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        count_deleted = 0
        
        # Recorrer todos los directorios de respaldo
        for document_dir in os.listdir(backup_dir):
            document_backup_path = os.path.join(backup_dir, document_dir)
            
            if not os.path.isdir(document_backup_path):
                continue
                
            # Recorrer archivos de respaldo
            for backup_file in os.listdir(document_backup_path):
                file_path = os.path.join(document_backup_path, backup_file)
                
                # Obtener fecha de modificación
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # Eliminar si es más antiguo que el límite
                if file_mtime < cutoff_date:
                    os.remove(file_path)
                    count_deleted += 1
            
            # Eliminar directorio si está vacío
            if not os.listdir(document_backup_path):
                os.rmdir(document_backup_path)
        
        logger.info(f"Limpieza de respaldos completada: {count_deleted} archivos eliminados")
        
    except Exception as e:
        logger.error(f"Error en limpieza de respaldos: {str(e)}")
