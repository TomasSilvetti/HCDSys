#!/bin/bash

# Script para restaurar una copia de seguridad de la base de datos PostgreSQL

# Configuración
BACKUP_DIR="/var/backups/hcdsys/db"
CONTAINER_NAME="hcdsys-db"
DB_NAME="hcdsys_prod"
DB_USER="hcdsys_user"
LOG_FILE="/var/log/hcdsys/backup.log"

# Función para registrar mensajes
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Verificar que se proporcionó un archivo de respaldo
if [ -z "$1" ]; then
    echo "Uso: $0 <archivo_de_respaldo.dump.gz>"
    echo "Respaldos disponibles:"
    ls -lh $BACKUP_DIR/*.dump.gz 2>/dev/null || echo "No hay respaldos disponibles en $BACKUP_DIR"
    exit 1
fi

BACKUP_FILE="$1"

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

log_message "Iniciando restauración de base de datos desde: $BACKUP_FILE"

# Descomprimir el archivo si es necesario
if [[ "$BACKUP_FILE" == *.gz ]]; then
    log_message "Descomprimiendo archivo de respaldo"
    TEMP_FILE="/tmp/backup_restore_$(date +%s).dump"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    BACKUP_FILE="$TEMP_FILE"
fi

# Copiar el archivo al contenedor
log_message "Copiando archivo de respaldo al contenedor"
docker cp "$BACKUP_FILE" $CONTAINER_NAME:/tmp/restore.dump

# Restaurar la base de datos
log_message "Restaurando base de datos $DB_NAME"
log_message "ADVERTENCIA: Esto eliminará todos los datos existentes en la base de datos"

# Pedir confirmación
read -p "¿Está seguro de que desea continuar? (s/N): " CONFIRM
if [[ "$CONFIRM" != "s" && "$CONFIRM" != "S" ]]; then
    log_message "Restauración cancelada por el usuario"
    # Limpiar archivos temporales
    if [[ "$TEMP_FILE" == /tmp/backup_restore_* ]]; then
        rm -f "$TEMP_FILE"
    fi
    docker exec $CONTAINER_NAME rm -f /tmp/restore.dump
    exit 0
fi

# Detener servicios que dependen de la base de datos
log_message "Deteniendo servicios dependientes"
docker-compose stop backend

# Restaurar la base de datos
log_message "Ejecutando pg_restore en el contenedor"
docker exec $CONTAINER_NAME bash -c "dropdb -U $DB_USER --if-exists $DB_NAME && createdb -U $DB_USER $DB_NAME && pg_restore -U $DB_USER -d $DB_NAME /tmp/restore.dump"

# Verificar el resultado
if [ $? -eq 0 ]; then
    log_message "Restauración completada con éxito"
else
    log_message "ERROR: Falló la restauración de la base de datos"
fi

# Limpiar archivos temporales
log_message "Limpiando archivos temporales"
if [[ "$TEMP_FILE" == /tmp/backup_restore_* ]]; then
    rm -f "$TEMP_FILE"
fi
docker exec $CONTAINER_NAME rm -f /tmp/restore.dump

# Reiniciar servicios
log_message "Reiniciando servicios"
docker-compose start backend

log_message "Proceso de restauración completado"
