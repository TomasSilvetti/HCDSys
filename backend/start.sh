#!/bin/bash
set -e

echo "🚀 Iniciando HCDSys Backend..."

# Verificar que DATABASE_URL esté configurada
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL no está configurada"
    exit 1
fi

echo "✅ DATABASE_URL configurada"

# Esperar a que PostgreSQL esté disponible
echo "⏳ Esperando a que PostgreSQL esté disponible..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if python -c "
import psycopg2
import os
import sys
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f'Intento {$retry_count + 1}/{$max_retries}: {e}')
    sys.exit(1)
" 2>/dev/null; then
        echo "✅ PostgreSQL está disponible"
        break
    fi
    
    retry_count=$((retry_count + 1))
    if [ $retry_count -eq $max_retries ]; then
        echo "❌ ERROR: No se pudo conectar a PostgreSQL después de $max_retries intentos"
        exit 1
    fi
    
    echo "⏳ Reintentando en 2 segundos... ($retry_count/$max_retries)"
    sleep 2
done

# Ejecutar migraciones de Alembic
echo "🔄 Ejecutando migraciones de base de datos..."
cd /app
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migraciones ejecutadas correctamente"
else
    echo "❌ ERROR: Fallo al ejecutar migraciones"
    exit 1
fi

# Inicializar roles y permisos
echo "🔐 Inicializando roles y permisos..."
python -c "
from app.db.database import SessionLocal
from app.db.init_roles import init_roles_and_permissions

db = SessionLocal()
try:
    init_roles_and_permissions(db)
    print('✅ Roles y permisos inicializados')
except Exception as e:
    print(f'⚠️  Advertencia al inicializar roles: {e}')
finally:
    db.close()
"

# Intentar crear usuario admin (ignorar si ya existe)
echo "👤 Verificando usuario admin..."
python -c "
from app.db.database import SessionLocal
from app.services.user_service import UserService

db = SessionLocal()
try:
    # Crear servicio de usuario
    user_service = UserService(db)
    
    # Intentar crear usuario admin (el método maneja si ya existe)
    user_service.create_admin_user(
        email='admin@hcdsys.com',
        password='Admin123!',
        nombre='Administrador',
        apellido='del Sistema',
        dni='00000000'
    )
    print('✅ Usuario admin verificado/creado')
except Exception as e:
    print(f'⚠️  Advertencia al crear admin: {e}')
finally:
    db.close()
"

# Iniciar Gunicorn
echo "🚀 Iniciando servidor Gunicorn..."
exec gunicorn -c gunicorn_config.py app.main:app

