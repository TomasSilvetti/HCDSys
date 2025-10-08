import os
import shutil
import hashlib
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from fastapi import UploadFile
from sqlalchemy.orm import Session

from ..db import models
from ..utils.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

class StorageService:
    """
    Servicio para gestionar el almacenamiento físico de documentos.
    """
    
    @staticmethod
    async def save_document(
        file: UploadFile, 
        document_id: int, 
        user_id: int,
        db: Session
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Guarda un archivo en el sistema de archivos y actualiza los metadatos en la base de datos.
        
        Args:
            file: Archivo a guardar
            document_id: ID del documento en la base de datos
            user_id: ID del usuario que está guardando el documento
            db: Sesión de base de datos
            
        Returns:
            Tuple con:
            - Éxito de la operación (bool)
            - Mensaje (str)
            - Metadatos del archivo (Dict)
        """
        try:
            # Crear directorio para el documento si no existe
            document_dir = os.path.join(settings.DOCUMENT_STORAGE_PATH, str(document_id))
            os.makedirs(document_dir, exist_ok=True)
            
            # Obtener extensión del archivo
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            # Definir ruta completa del archivo
            file_path = os.path.join(document_dir, f"{document_id}{file_extension}")
            
            # Leer contenido del archivo
            contents = await file.read()
            
            # Calcular hash del archivo para verificación de integridad
            file_hash = hashlib.sha256(contents).hexdigest()
            
            # Guardar archivo
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
            
            # Preparar metadatos
            metadata = {
                "path_archivo": file_path,
                "hash_archivo": file_hash,
                "tamano_archivo": len(contents),
                "extension_archivo": file_extension,
                "fecha_ultima_verificacion": datetime.utcnow(),
                "estado_integridad": True
            }
            
            # Registrar operación exitosa
            logger.info(f"Archivo guardado correctamente: {file_path}")
            
            return True, "Archivo guardado correctamente", metadata
            
        except Exception as e:
            # Registrar error
            logger.error(f"Error al guardar archivo: {str(e)}")
            
            # Registrar en la base de datos
            error_log = models.ErrorAlmacenamiento(
                documento_id=document_id,
                usuario_id=user_id,
                tipo_error="filesystem",
                mensaje_error=f"Error al guardar archivo: {str(e)}"
            )
            db.add(error_log)
            try:
                db.commit()
            except:
                db.rollback()
            
            return False, f"Error al guardar archivo: {str(e)}", {}
    
    @staticmethod
    def verify_document_integrity(
        document_id: int,
        db: Session
    ) -> Tuple[bool, str]:
        """
        Verifica la integridad de un documento comparando su hash almacenado con un nuevo cálculo.
        
        Args:
            document_id: ID del documento a verificar
            db: Sesión de base de datos
            
        Returns:
            Tuple con:
            - Resultado de la verificación (bool)
            - Mensaje (str)
        """
        try:
            # Obtener documento de la base de datos
            documento = db.query(models.Documento).filter(models.Documento.id == document_id).first()
            
            if not documento:
                return False, f"Documento con ID {document_id} no encontrado"
            
            # Verificar que existe el archivo
            if not os.path.exists(documento.path_archivo):
                return False, f"Archivo no encontrado en la ruta: {documento.path_archivo}"
            
            # Leer archivo y calcular hash
            with open(documento.path_archivo, "rb") as file:
                contents = file.read()
                current_hash = hashlib.sha256(contents).hexdigest()
            
            # Comparar hashes
            is_valid = current_hash == documento.hash_archivo
            
            # Actualizar información de verificación
            documento.fecha_ultima_verificacion = datetime.utcnow()
            documento.estado_integridad = is_valid
            
            db.commit()
            
            if is_valid:
                return True, "La verificación de integridad fue exitosa"
            else:
                # Registrar error de integridad
                error_log = models.ErrorAlmacenamiento(
                    documento_id=document_id,
                    usuario_id=documento.usuario_id,
                    tipo_error="integridad",
                    mensaje_error=f"Fallo en verificación de integridad. Hash esperado: {documento.hash_archivo}, Hash actual: {current_hash}"
                )
                db.add(error_log)
                db.commit()
                
                return False, "La verificación de integridad falló"
                
        except Exception as e:
            logger.error(f"Error al verificar integridad: {str(e)}")
            return False, f"Error al verificar integridad: {str(e)}"
    
    @staticmethod
    def delete_document(
        document_id: int,
        db: Session,
        physical_delete: bool = False
    ) -> Tuple[bool, str]:
        """
        Elimina un documento, marcándolo como inactivo en la base de datos 
        y opcionalmente eliminando el archivo físico.
        
        Args:
            document_id: ID del documento a eliminar
            db: Sesión de base de datos
            physical_delete: Si es True, elimina el archivo físico
            
        Returns:
            Tuple con:
            - Éxito de la operación (bool)
            - Mensaje (str)
        """
        try:
            # Obtener documento de la base de datos
            documento = db.query(models.Documento).filter(models.Documento.id == document_id).first()
            
            if not documento:
                return False, f"Documento con ID {document_id} no encontrado"
            
            # Marcar como inactivo en la base de datos
            documento.activo = False
            db.commit()
            
            # Si se solicita eliminación física
            if physical_delete and os.path.exists(documento.path_archivo):
                # Eliminar archivo
                os.remove(documento.path_archivo)
                
                # Eliminar directorio si está vacío
                document_dir = os.path.dirname(documento.path_archivo)
                if os.path.exists(document_dir) and not os.listdir(document_dir):
                    os.rmdir(document_dir)
            
            return True, "Documento eliminado correctamente"
            
        except Exception as e:
            logger.error(f"Error al eliminar documento: {str(e)}")
            db.rollback()
            return False, f"Error al eliminar documento: {str(e)}"
    
    @staticmethod
    def create_backup(document_id: int, db: Session) -> Tuple[bool, str, Optional[str]]:
        """
        Crea una copia de seguridad de un documento.
        
        Args:
            document_id: ID del documento a respaldar
            db: Sesión de base de datos
            
        Returns:
            Tuple con:
            - Éxito de la operación (bool)
            - Mensaje (str)
            - Ruta del archivo de respaldo (str o None)
        """
        try:
            # Obtener documento de la base de datos
            documento = db.query(models.Documento).filter(models.Documento.id == document_id).first()
            
            if not documento:
                return False, f"Documento con ID {document_id} no encontrado", None
            
            # Verificar que existe el archivo
            if not os.path.exists(documento.path_archivo):
                return False, f"Archivo no encontrado en la ruta: {documento.path_archivo}", None
            
            # Crear directorio de respaldos si no existe
            backup_dir = os.path.join(settings.DOCUMENT_STORAGE_PATH, "backups", str(document_id))
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generar nombre para el archivo de respaldo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{document_id}_{timestamp}{documento.extension_archivo}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Copiar archivo
            shutil.copy2(documento.path_archivo, backup_path)
            
            return True, "Respaldo creado correctamente", backup_path
            
        except Exception as e:
            logger.error(f"Error al crear respaldo: {str(e)}")
            return False, f"Error al crear respaldo: {str(e)}", None
    
    @staticmethod
    def restore_from_backup(
        document_id: int, 
        backup_path: str,
        user_id: int,
        db: Session
    ) -> Tuple[bool, str]:
        """
        Restaura un documento desde una copia de seguridad.
        
        Args:
            document_id: ID del documento a restaurar
            backup_path: Ruta del archivo de respaldo
            user_id: ID del usuario que realiza la restauración
            db: Sesión de base de datos
            
        Returns:
            Tuple con:
            - Éxito de la operación (bool)
            - Mensaje (str)
        """
        try:
            # Verificar que existe el archivo de respaldo
            if not os.path.exists(backup_path):
                return False, f"Archivo de respaldo no encontrado: {backup_path}"
            
            # Obtener documento de la base de datos
            documento = db.query(models.Documento).filter(models.Documento.id == document_id).first()
            
            if not documento:
                return False, f"Documento con ID {document_id} no encontrado"
            
            # Crear respaldo del archivo actual antes de restaurar
            current_backup = None
            if os.path.exists(documento.path_archivo):
                success, _, current_backup = StorageService.create_backup(document_id, db)
                if not success:
                    return False, "No se pudo crear respaldo del archivo actual antes de restaurar"
            
            # Copiar archivo de respaldo a la ubicación original
            shutil.copy2(backup_path, documento.path_archivo)
            
            # Recalcular hash y actualizar metadatos
            with open(documento.path_archivo, "rb") as file:
                contents = file.read()
                new_hash = hashlib.sha256(contents).hexdigest()
            
            documento.hash_archivo = new_hash
            documento.tamano_archivo = os.path.getsize(documento.path_archivo)
            documento.fecha_ultima_verificacion = datetime.utcnow()
            documento.estado_integridad = True
            
            # Registrar en historial
            historial = models.HistorialAcceso(
                usuario_id=user_id,
                documento_id=document_id,
                accion="restauracion",
                detalles=f"Documento restaurado desde respaldo: {backup_path}"
            )
            db.add(historial)
            db.commit()
            
            return True, "Documento restaurado correctamente"
            
        except Exception as e:
            logger.error(f"Error al restaurar documento: {str(e)}")
            db.rollback()
            
            # Registrar error
            error_log = models.ErrorAlmacenamiento(
                documento_id=document_id,
                usuario_id=user_id,
                tipo_error="restauracion",
                mensaje_error=f"Error al restaurar documento: {str(e)}"
            )
            db.add(error_log)
            try:
                db.commit()
            except:
                db.rollback()
                
            return False, f"Error al restaurar documento: {str(e)}"
