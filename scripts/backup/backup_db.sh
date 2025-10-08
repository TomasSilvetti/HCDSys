#!/bin/bash

# Script para realizar copias de seguridad de la base de datos PostgreSQL

# Configuración
BACKUP_DIR="/var/backups/hcdsys/db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTAINER_NAME="hcdsys-db"
DB_NAME="hcdsys_prod"
DB_USER="hcdsys_user"
RETENTION_DAYS=30
S3_BUCKET="hcdsys-backups"
S3_PREFIX="db"
LOG_FILE="/var/log/hcdsys/backup.log"

# Función para registrar mensajes
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Crear directorio de respaldos si no existe
mkdir -p $BACKUP_DIR
log_message "Iniciando respaldo de base de datos"

# Realizar respaldo
log_message "Ejecutando pg_dump en el contenedor $CONTAINER_NAME"
if docker exec $CONTAINER_NAME pg_dump -U $DB_USER -d $DB_NAME -F c -f /tmp/backup_$TIMESTAMP.dump; then
    log_message "pg_dump completado con éxito"
    
    # Copiar el archivo de respaldo del contenedor
    log_message "Copiando archivo de respaldo desde el contenedor"
    docker cp $CONTAINER_NAME:/tmp/backup_$TIMESTAMP.dump $BACKUP_DIR/
    docker exec $CONTAINER_NAME rm /tmp/backup_$TIMESTAMP.dump
    
    # Comprimir respaldo
    log_message "Comprimiendo archivo de respaldo"
    gzip $BACKUP_DIR/backup_$TIMESTAMP.dump
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.dump.gz"
    
    # Verificar integridad del archivo
    if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
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
        log_message "ERROR: El archivo de respaldo no existe o está vacío"
    fi
else
    log_message "ERROR: Falló la ejecución de pg_dump"
fi

# Eliminar respaldos antiguos
log_message "Eliminando respaldos antiguos (más de $RETENTION_DAYS días)"
find $BACKUP_DIR -type f -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete

log_message "Proceso de respaldo completado"
