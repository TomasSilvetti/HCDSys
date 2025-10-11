import os
import shutil
import hashlib
import logging
import difflib
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List
from fastapi import UploadFile
from sqlalchemy.orm import Session

from ..db import models
from ..utils.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

class StorageService:
    """
    Servicio para gestionar el almacenamiento físico de documentos y sus versiones.
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
    async def create_document_version(
        file: UploadFile,
        document_id: int,
        user_id: int,
        db: Session,
        comentario: Optional[str] = None,
        cambios: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Crea una nueva versión de un documento existente.
        
        Args:
            file: Archivo de la nueva versión
            document_id: ID del documento
            user_id: ID del usuario que crea la versión
            comentario: Comentario opcional sobre la versión
            cambios: Descripción opcional de los cambios realizados
            db: Sesión de base de datos
            
        Returns:
            Tuple con:
            - Éxito de la operación (bool)
            - Mensaje (str)
            - ID de la versión creada (int o None)
        """
        nueva_version_id = None
        version_file_path = None
        
        try:
            # Verificar que el documento existe
            documento = db.query(models.Documento).filter(
                models.Documento.id == document_id,
                models.Documento.activo == True
            ).first()
            
            if not documento:
                return False, f"Documento con ID {document_id} no encontrado", None
            
            # Obtener la última versión del documento
            ultima_version = db.query(models.VersionDocumento).filter(
                models.VersionDocumento.documento_id == document_id,
                models.VersionDocumento.es_actual == True
            ).first()
            
            # Si no hay versión actual, buscar la versión con número más alto
            if not ultima_version:
                ultima_version = db.query(models.VersionDocumento).filter(
                    models.VersionDocumento.documento_id == document_id
                ).order_by(models.VersionDocumento.numero_version.desc()).first()
            
            # Determinar el número de la nueva versión
            nuevo_numero_version = 1
            version_anterior_id = None
            
            if ultima_version:
                nuevo_numero_version = ultima_version.numero_version + 1
                version_anterior_id = ultima_version.id
            
            # Crear directorio para versiones si no existe
            versions_dir = os.path.join(settings.DOCUMENT_STORAGE_PATH, str(document_id), "versions")
            os.makedirs(versions_dir, exist_ok=True)
            
            # Obtener extensión del archivo
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            # Definir ruta completa del archivo de la versión
            version_file_path = os.path.join(versions_dir, f"{document_id}_v{nuevo_numero_version}{file_extension}")
            
            # Leer contenido del archivo
            contents = await file.read()
            
            # Calcular hash del archivo
            file_hash = hashlib.sha256(contents).hexdigest()
            
            # Guardar archivo de la versión
            with open(version_file_path, "wb") as buffer:
                buffer.write(contents)
            
            # Usar transacciones separadas para cada operación principal
            # Transacción 1: Actualizar la versión anterior
            if ultima_version:
                try:
                    # Actualizar la versión anterior para que no sea la actual
                    ultima_version.es_actual = False
                    db.add(ultima_version)
                    db.commit()
                except Exception as e:
                    logger.error(f"Error al actualizar versión anterior: {str(e)}")
                    # Continuar con el proceso, no es crítico
            
            # Transacción 2: Crear nueva versión
            try:
                # Crear registro de la nueva versión
                nueva_version = models.VersionDocumento(
                    documento_id=document_id,
                    numero_version=nuevo_numero_version,
                    fecha_version=datetime.utcnow(),
                    comentario=comentario,
                    cambios=cambios,
                    path_archivo=version_file_path,
                    usuario_id=user_id,
                    version_anterior_id=version_anterior_id,
                    hash_archivo=file_hash,
                    tamano_archivo=len(contents),
                    extension_archivo=file_extension,
                    es_actual=True,
                    titulo_archivo=file.filename
                )
                
                db.add(nueva_version)
                db.commit()
                db.refresh(nueva_version)
                nueva_version_id = nueva_version.id
                
                logger.info(f"Nueva versión creada con ID: {nueva_version_id}")
            except Exception as e:
                logger.error(f"Error al crear registro de nueva versión: {str(e)}")
                if os.path.exists(version_file_path):
                    try:
                        os.remove(version_file_path)
                    except:
                        pass
                raise
            
            # Transacción 3: Actualizar documento principal
            try:
                # Actualizar el documento principal con la información de la nueva versión
                documento.path_archivo = version_file_path
                documento.hash_archivo = file_hash
                documento.tamano_archivo = len(contents)
                documento.extension_archivo = file_extension
                documento.fecha_modificacion = datetime.utcnow()
                documento.fecha_ultima_verificacion = datetime.utcnow()
                documento.estado_integridad = True
                
                db.add(documento)
                db.commit()
            except Exception as e:
                logger.error(f"Error al actualizar documento principal: {str(e)}")
                # No lanzar excepción, la versión ya se creó correctamente
            
            # Transacción 4: Registrar historial (no crítico)
            try:
                # Registrar la acción en el historial
                historial = models.HistorialAcceso(
                    usuario_id=user_id,
                    documento_id=document_id,
                    accion="nueva_version",
                    detalles=f"Nueva versión {nuevo_numero_version} creada"
                )
                db.add(historial)
                db.commit()
            except Exception as e:
                logger.error(f"Error al registrar historial: {str(e)}")
                # No lanzar excepción, la versión ya se creó correctamente
            
            return True, f"Versión {nuevo_numero_version} creada correctamente", nueva_version_id
            
        except Exception as e:
            logger.error(f"Error al crear versión: {str(e)}")
            
            # Si ya se creó la versión en la base de datos pero ocurrió un error posterior
            if nueva_version_id is not None:
                logger.warning(f"Se creó la versión con ID {nueva_version_id} pero ocurrió un error posterior")
                return True, f"Versión creada con advertencias: {str(e)}", nueva_version_id
            
            # Si el archivo se guardó pero no se creó el registro en la base de datos
            if version_file_path and os.path.exists(version_file_path):
                try:
                    os.remove(version_file_path)
                    logger.info(f"Archivo temporal eliminado: {version_file_path}")
                except Exception as cleanup_error:
                    logger.error(f"Error al limpiar archivo temporal: {str(cleanup_error)}")
            
            # Registrar error
            try:
                db.rollback()
                error_log = models.ErrorAlmacenamiento(
                    documento_id=document_id,
                    usuario_id=user_id,
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
            
            return False, f"Error al crear versión: {str(e)}", None
    
    @staticmethod
    def restore_version(
        document_id: int,
        version_id: int,
        user_id: int,
        db: Session,
        comentario: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Restaura una versión específica de un documento, creando una nueva versión.
        
        Args:
            document_id: ID del documento
            version_id: ID de la versión a restaurar
            user_id: ID del usuario que realiza la restauración
            comentario: Comentario opcional sobre la restauración
            db: Sesión de base de datos
            
        Returns:
            Tuple con:
            - Éxito de la operación (bool)
            - Mensaje (str)
            - ID de la nueva versión creada (int o None)
        """
        try:
            # Verificar que el documento existe
            documento = db.query(models.Documento).filter(
                models.Documento.id == document_id,
                models.Documento.activo == True
            ).first()
            
            if not documento:
                return False, f"Documento con ID {document_id} no encontrado", None
            
            # Verificar que la versión existe y pertenece al documento
            version = db.query(models.VersionDocumento).filter(
                models.VersionDocumento.id == version_id,
                models.VersionDocumento.documento_id == document_id
            ).first()
            
            if not version:
                return False, f"Versión con ID {version_id} no encontrada para el documento {document_id}", None
            
            # Verificar que el archivo de la versión existe
            if not os.path.exists(version.path_archivo):
                return False, f"Archivo de la versión no encontrado: {version.path_archivo}", None
            
            # Obtener la última versión del documento
            ultima_version = db.query(models.VersionDocumento).filter(
                models.VersionDocumento.documento_id == document_id,
                models.VersionDocumento.es_actual == True
            ).first()
            
            # Si no hay versión actual, buscar la versión con número más alto
            if not ultima_version:
                ultima_version = db.query(models.VersionDocumento).filter(
                    models.VersionDocumento.documento_id == document_id
                ).order_by(models.VersionDocumento.numero_version.desc()).first()
            
            # Determinar el número de la nueva versión
            nuevo_numero_version = 1
            version_anterior_id = None
            
            if ultima_version:
                nuevo_numero_version = ultima_version.numero_version + 1
                version_anterior_id = ultima_version.id
                
                # Actualizar la versión anterior para que no sea la actual
                ultima_version.es_actual = False
                db.add(ultima_version)
            
            # Crear directorio para versiones si no existe
            versions_dir = os.path.join(settings.DOCUMENT_STORAGE_PATH, str(document_id), "versions")
            os.makedirs(versions_dir, exist_ok=True)
            
            # Definir ruta completa del archivo de la nueva versión
            version_file_path = os.path.join(versions_dir, f"{document_id}_v{nuevo_numero_version}{version.extension_archivo}")
            
            # Copiar archivo de la versión a restaurar
            shutil.copy2(version.path_archivo, version_file_path)
            
            # Calcular hash del archivo
            with open(version_file_path, "rb") as file:
                contents = file.read()
                file_hash = hashlib.sha256(contents).hexdigest()
            
            # Crear registro de la nueva versión
            nueva_version = models.VersionDocumento(
                documento_id=document_id,
                numero_version=nuevo_numero_version,
                fecha_version=datetime.utcnow(),
                comentario=comentario or f"Restauración de la versión {version.numero_version}",
                cambios=f"Restauración de la versión {version.numero_version}",
                path_archivo=version_file_path,
                usuario_id=user_id,
                version_anterior_id=version_anterior_id,
                hash_archivo=file_hash,
                tamano_archivo=os.path.getsize(version_file_path),
                extension_archivo=version.extension_archivo,
                es_actual=True,
                titulo_archivo=version.titulo_archivo
            )
            
            db.add(nueva_version)
            db.commit()
            db.refresh(nueva_version)
            
            # Actualizar el documento principal con la información de la nueva versión
            documento.path_archivo = version_file_path
            documento.hash_archivo = file_hash
            documento.tamano_archivo = os.path.getsize(version_file_path)
            documento.extension_archivo = version.extension_archivo
            documento.fecha_modificacion = datetime.utcnow()
            documento.fecha_ultima_verificacion = datetime.utcnow()
            documento.estado_integridad = True
            
            db.add(documento)
            db.commit()
            
            # Registrar la acción en el historial
            historial = models.HistorialAcceso(
                usuario_id=user_id,
                documento_id=document_id,
                accion="restauracion_version",
                detalles=f"Restauración de la versión {version.numero_version} como nueva versión {nuevo_numero_version}"
            )
            db.add(historial)
            db.commit()
            
            return True, f"Versión {version.numero_version} restaurada como versión {nuevo_numero_version}", nueva_version.id
            
        except Exception as e:
            logger.error(f"Error al restaurar versión: {str(e)}")
            db.rollback()
            
            # Registrar error
            error_log = models.ErrorAlmacenamiento(
                documento_id=document_id,
                usuario_id=user_id,
                tipo_error="restauracion_version",
                mensaje_error=f"Error al restaurar versión: {str(e)}"
            )
            db.add(error_log)
            try:
                db.commit()
            except:
                db.rollback()
            
            return False, f"Error al restaurar versión: {str(e)}", None
    
    @staticmethod
    def compare_versions(
        document_id: int,
        version_id1: int,
        version_id2: int,
        db: Session
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Compara dos versiones de un documento.
        
        Args:
            document_id: ID del documento
            version_id1: ID de la primera versión a comparar
            version_id2: ID de la segunda versión a comparar
            db: Sesión de base de datos
            
        Returns:
            Tuple con:
            - Éxito de la operación (bool)
            - Mensaje (str)
            - Diccionario con los resultados de la comparación (Dict o None)
        """
        try:
            # Verificar que el documento existe
            documento = db.query(models.Documento).filter(
                models.Documento.id == document_id,
                models.Documento.activo == True
            ).first()
            
            if not documento:
                return False, f"Documento con ID {document_id} no encontrado", None
            
            # Verificar que las versiones existen y pertenecen al documento
            version1 = db.query(models.VersionDocumento).filter(
                models.VersionDocumento.id == version_id1,
                models.VersionDocumento.documento_id == document_id
            ).first()
            
            version2 = db.query(models.VersionDocumento).filter(
                models.VersionDocumento.id == version_id2,
                models.VersionDocumento.documento_id == document_id
            ).first()
            
            if not version1:
                return False, f"Versión con ID {version_id1} no encontrada para el documento {document_id}", None
                
            if not version2:
                return False, f"Versión con ID {version_id2} no encontrada para el documento {document_id}", None
            
            # Verificar que los archivos de las versiones existen
            if not os.path.exists(version1.path_archivo):
                return False, f"Archivo de la versión {version_id1} no encontrado: {version1.path_archivo}", None
                
            if not os.path.exists(version2.path_archivo):
                return False, f"Archivo de la versión {version_id2} no encontrado: {version2.path_archivo}", None
            
            # Leer contenido de los archivos
            try:
                with open(version1.path_archivo, "r", encoding="utf-8") as file1:
                    content1 = file1.readlines()
                    
                with open(version2.path_archivo, "r", encoding="utf-8") as file2:
                    content2 = file2.readlines()
            except UnicodeDecodeError:
                # Si no se pueden leer como texto, comparar solo metadatos
                return True, "Los archivos son binarios, solo se pueden comparar metadatos", {
                    "version1": {
                        "numero": version1.numero_version,
                        "fecha": version1.fecha_version.isoformat(),
                        "usuario": f"{version1.usuario.nombre} {version1.usuario.apellido}",
                        "tamano": version1.tamano_archivo,
                        "comentario": version1.comentario,
                        "cambios": version1.cambios
                    },
                    "version2": {
                        "numero": version2.numero_version,
                        "fecha": version2.fecha_version.isoformat(),
                        "usuario": f"{version2.usuario.nombre} {version2.usuario.apellido}",
                        "tamano": version2.tamano_archivo,
                        "comentario": version2.comentario,
                        "cambios": version2.cambios
                    },
                    "diff": None,
                    "is_binary": True
                }
            
            # Generar diff
            diff = list(difflib.unified_diff(
                content1, 
                content2, 
                fromfile=f"v{version1.numero_version}", 
                tofile=f"v{version2.numero_version}",
                lineterm=""
            ))
            
            # Contar cambios
            added_lines = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
            removed_lines = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
            
            # Preparar resultado
            result = {
                "version1": {
                    "numero": version1.numero_version,
                    "fecha": version1.fecha_version.isoformat(),
                    "usuario": f"{version1.usuario.nombre} {version1.usuario.apellido}",
                    "tamano": version1.tamano_archivo,
                    "comentario": version1.comentario,
                    "cambios": version1.cambios
                },
                "version2": {
                    "numero": version2.numero_version,
                    "fecha": version2.fecha_version.isoformat(),
                    "usuario": f"{version2.usuario.nombre} {version2.usuario.apellido}",
                    "tamano": version2.tamano_archivo,
                    "comentario": version2.comentario,
                    "cambios": version2.cambios
                },
                "diff": diff,
                "added_lines": added_lines,
                "removed_lines": removed_lines,
                "is_binary": False
            }
            
            return True, "Comparación realizada correctamente", result
            
        except Exception as e:
            logger.error(f"Error al comparar versiones: {str(e)}")
            return False, f"Error al comparar versiones: {str(e)}", None
    
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
