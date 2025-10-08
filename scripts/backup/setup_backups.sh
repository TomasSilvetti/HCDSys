#!/bin/bash

# Script para configurar las copias de seguridad automáticas

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DB_SCRIPT="$SCRIPT_DIR/backup_db.sh"
BACKUP_FILES_SCRIPT="$SCRIPT_DIR/backup_files.sh"
BACKUP_DIR="/var/backups/hcdsys"
LOG_DIR="/var/log/hcdsys"

# Verificar si se está ejecutando como root
if [ "$(id -u)" -ne 0 ]; then
    echo "Este script debe ejecutarse como root"
    exit 1
fi

echo "Configurando sistema de copias de seguridad automáticas para HCDSys"

# Crear directorios necesarios
echo "Creando directorios de respaldo y logs..."
mkdir -p "$BACKUP_DIR/db"
mkdir -p "$BACKUP_DIR/files"
mkdir -p "$LOG_DIR"

# Establecer permisos adecuados
echo "Configurando permisos..."
chmod 750 "$BACKUP_DIR"
chmod 750 "$LOG_DIR"
chmod 750 "$BACKUP_DIR/db"
chmod 750 "$BACKUP_DIR/files"

# Hacer ejecutables los scripts de respaldo
chmod +x "$BACKUP_DB_SCRIPT"
chmod +x "$BACKUP_FILES_SCRIPT"

# Configurar crontab para respaldos automáticos
echo "Configurando crontab para respaldos automáticos..."

# Verificar si las entradas ya existen en crontab
CRON_DB=$(crontab -l 2>/dev/null | grep -F "$BACKUP_DB_SCRIPT")
CRON_FILES=$(crontab -l 2>/dev/null | grep -F "$BACKUP_FILES_SCRIPT")

# Crear archivo temporal para crontab
TEMP_CRON=$(mktemp)
crontab -l 2>/dev/null > "$TEMP_CRON" || echo "" > "$TEMP_CRON"

# Añadir entrada para respaldo diario de base de datos (si no existe)
if [ -z "$CRON_DB" ]; then
    echo "# Respaldo diario de base de datos HCDSys a las 2 AM" >> "$TEMP_CRON"
    echo "0 2 * * * $BACKUP_DB_SCRIPT >> $LOG_DIR/backup.log 2>&1" >> "$TEMP_CRON"
    echo "Configurado respaldo diario de base de datos a las 2 AM"
else
    echo "El respaldo de base de datos ya está configurado en crontab"
fi

# Añadir entrada para respaldo semanal de archivos (si no existe)
if [ -z "$CRON_FILES" ]; then
    echo "# Respaldo semanal de archivos HCDSys los domingos a las 3 AM" >> "$TEMP_CRON"
    echo "0 3 * * 0 $BACKUP_FILES_SCRIPT >> $LOG_DIR/backup.log 2>&1" >> "$TEMP_CRON"
    echo "Configurado respaldo semanal de archivos los domingos a las 3 AM"
else
    echo "El respaldo de archivos ya está configurado en crontab"
fi

# Instalar el nuevo crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

# Configurar rotación de logs
echo "Configurando rotación de logs..."
cat > /etc/logrotate.d/hcdsys << EOF
$LOG_DIR/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload rsyslog >/dev/null 2>&1 || true
    endscript
}
EOF

echo "Configuración de copias de seguridad completada"
echo "Directorios de respaldo:"
echo "  - Base de datos: $BACKUP_DIR/db"
echo "  - Archivos: $BACKUP_DIR/files"
echo "Archivo de log: $LOG_DIR/backup.log"
echo ""
echo "Para ejecutar un respaldo manual:"
echo "  - Base de datos: $BACKUP_DB_SCRIPT"
echo "  - Archivos: $BACKUP_FILES_SCRIPT"
echo ""
echo "Para restaurar desde un respaldo:"
echo "  - Base de datos: $SCRIPT_DIR/restore_db.sh <archivo_de_respaldo>"
echo "  - Archivos: $SCRIPT_DIR/restore_files.sh <archivo_de_respaldo>"
