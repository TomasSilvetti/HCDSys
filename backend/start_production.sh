#!/bin/bash

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Establecer variables de entorno
export PYTHONPATH=$(pwd)
export ENV_FILE=.env.production

# Aplicar migraciones de base de datos
echo "Aplicando migraciones de base de datos..."
alembic upgrade head

# Iniciar Gunicorn con la configuración de producción
echo "Iniciando servidor en modo producción..."
gunicorn -c gunicorn_config.py app.main:app
