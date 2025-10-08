#!/bin/bash

# Script para restaurar una copia de seguridad de archivos de documentos

# Configuración
BACKUP_DIR="/var/backups/hcdsys/files"
DOCS_DIR="/var/www/hcdsys/storage/documents"
TEMP_RESTORE_DIR="/tmp/hcdsys_restore"
LOG_FILE="/var/log/hcdsys/backup.log"

# Función para registrar mensajes
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Verificar que se proporcionó un archivo de respaldo
if [ -z "$1" ]; then
    echo "Uso: $0 <archivo_de_respaldo.tar.gz> [--force]"
    echo "Respaldos disponibles:"
    ls -lh $BACKUP_DIR/documents_*.tar.gz 2>/dev/null || echo "No hay respaldos disponibles en $BACKUP_DIR"
    exit 1
fi

BACKUP_FILE="$1"
FORCE_RESTORE=0

# Verificar si se especificó la opción --force
if [ "$2" == "--force" ]; then
    FORCE_RESTORE=1
fi

# Verificar si es una ruta absoluta o relativa
if [[ "$BACKUP_FILE" != /* ]]; then
    # Es una ruta relativa, buscar en el directorio de respaldos
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
fi

# Verificar que el archivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    log_message "ERROR: El archivo de respaldo no existe: $BACKUP_FILE"
    exit 1
fi

log_message "Iniciando restauración de archivos desde: $BACKUP_FILE"

# Verificar que el directorio de documentos existe
if [ ! -d "$DOCS_DIR" ]; then
    log_message "ERROR: El directorio de destino no existe: $DOCS_DIR"
    exit 1
fi

# Verificar si el directorio de documentos está vacío
if [ "$(ls -A $DOCS_DIR)" ] && [ $FORCE_RESTORE -eq 0 ]; then
    log_message "ADVERTENCIA: El directorio de documentos no está vacío"
    read -p "¿Desea continuar y sobrescribir los archivos existentes? (s/N): " CONFIRM
    if [[ "$CONFIRM" != "s" && "$CONFIRM" != "S" ]]; then
        log_message "Restauración cancelada por el usuario"
        exit 0
    fi
fi

# Crear directorio temporal para la restauración
log_message "Creando directorio temporal para la restauración"
rm -rf $TEMP_RESTORE_DIR
mkdir -p $TEMP_RESTORE_DIR

# Extraer el archivo de respaldo al directorio temporal
log_message "Extrayendo archivo de respaldo"
tar -xzf $BACKUP_FILE -C $TEMP_RESTORE_DIR

# Encontrar el directorio de documentos dentro del respaldo
SOURCE_DIR=$(find $TEMP_RESTORE_DIR -type d -path "*storage/documents" | head -n 1)

if [ -z "$SOURCE_DIR" ]; then
    log_message "ERROR: No se pudo encontrar el directorio de documentos en el respaldo"
    rm -rf $TEMP_RESTORE_DIR
    exit 1
fi

log_message "Directorio fuente encontrado: $SOURCE_DIR"

# Realizar la restauración
log_message "Restaurando archivos a $DOCS_DIR"
rsync -av --delete $SOURCE_DIR/ $DOCS_DIR/

# Verificar el resultado
if [ $? -eq 0 ]; then
    log_message "Restauración completada con éxito"
else
    log_message "ERROR: Falló la restauración de archivos"
fi

# Limpiar directorio temporal
log_message "Limpiando directorio temporal"
rm -rf $TEMP_RESTORE_DIR

log_message "Proceso de restauración de archivos completado"
