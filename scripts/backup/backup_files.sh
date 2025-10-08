#!/bin/bash

# Script para realizar copias de seguridad de archivos de documentos

# Configuración
BACKUP_DIR="/var/backups/hcdsys/files"
DOCS_DIR="/var/www/hcdsys/storage/documents"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30
S3_BUCKET="hcdsys-backups"
S3_PREFIX="files"
LOG_FILE="/var/log/hcdsys/backup.log"
MAX_BACKUPS=10

# Función para registrar mensajes
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Crear directorio de respaldos si no existe
mkdir -p $BACKUP_DIR
log_message "Iniciando respaldo de archivos de documentos"

# Verificar que el directorio de documentos existe
if [ ! -d "$DOCS_DIR" ]; then
    log_message "ERROR: El directorio de documentos no existe: $DOCS_DIR"
    exit 1
fi

# Realizar respaldo
BACKUP_FILE="$BACKUP_DIR/documents_$TIMESTAMP.tar.gz"
log_message "Creando archivo tar.gz de $DOCS_DIR"

tar -czf $BACKUP_FILE $DOCS_DIR 2>> $LOG_FILE

# Verificar si el respaldo se creó correctamente
if [ $? -eq 0 ] && [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    log_message "Respaldo creado con éxito: $BACKUP_FILE ($(du -h $BACKUP_FILE | cut -f1))"
    
    # Subir a S3 si está configurado
    if [ -n "$S3_BUCKET" ]; then
        log_message "Subiendo respaldo a S3: s3://$S3_BUCKET/$S3_PREFIX/"
        if command -v aws &> /dev/null; then
            aws s3 cp $BACKUP_FILE s3://$S3_BUCKET/$S3_PREFIX/
            if [ $? -eq 0 ]; then
                log_message "Subida a S3 completada con éxito"
            else
                log_message "Error al subir a S3"
            fi
        else
            log_message "AWS CLI no está instalado, omitiendo subida a S3"
        fi
    fi
else
    log_message "ERROR: Falló la creación del archivo de respaldo"
fi

# Eliminar respaldos antiguos basados en fecha
log_message "Eliminando respaldos antiguos (más de $RETENTION_DAYS días)"
find $BACKUP_DIR -type f -name "documents_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Limitar el número total de respaldos (mantener solo los más recientes)
BACKUP_COUNT=$(find $BACKUP_DIR -type f -name "documents_*.tar.gz" | wc -l)
if [ $BACKUP_COUNT -gt $MAX_BACKUPS ]; then
    log_message "Limitando a $MAX_BACKUPS respaldos (actual: $BACKUP_COUNT)"
    ls -t $BACKUP_DIR/documents_*.tar.gz | tail -n +$(($MAX_BACKUPS + 1)) | xargs rm -f
fi

log_message "Proceso de respaldo de archivos completado"
