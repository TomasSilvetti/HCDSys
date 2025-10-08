#!/bin/bash

# Script para inicializar el entorno de producción

# Crear directorios necesarios
mkdir -p certbot/conf certbot/www backend/logs backend/storage/documents

# Verificar si existe el archivo .env
if [ ! -f ".env" ]; then
  echo "Creando archivo .env para variables de entorno..."
  cat > .env << EOL
# Configuración de la base de datos
DB_NAME=hcdsys_prod
DB_USER=hcdsys_user
DB_PASSWORD=strong_password_here

# Configuración de seguridad
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=https://hcdsys.example.com

# Configuración del dominio
DOMAIN_NAME=hcdsys.example.com
EMAIL=admin@example.com
EOL
  echo "Archivo .env creado. Por favor, edita los valores según tus necesidades."
else
  echo "El archivo .env ya existe. Asegúrate de que contiene las variables necesarias."
fi

# Verificar si Docker y Docker Compose están instalados
if ! command -v docker &> /dev/null; then
  echo "Docker no está instalado. Por favor, instálalo antes de continuar."
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  echo "Docker Compose no está instalado. Por favor, instálalo antes de continuar."
  exit 1
fi

# Construir el frontend para producción
echo "Construyendo el frontend para producción..."
cd frontend
npm ci
npm run build:prod
cd ..

# Iniciar los servicios
echo "Iniciando servicios..."
docker-compose up -d

# Obtener certificado SSL inicial
echo "Obteniendo certificado SSL..."
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot \
  -d $(grep DOMAIN_NAME .env | cut -d '=' -f2) \
  --email $(grep EMAIL .env | cut -d '=' -f2) \
  --agree-tos --no-eff-email

# Reiniciar Nginx para cargar el certificado
docker-compose restart nginx

echo "Entorno de producción inicializado correctamente."
echo "La aplicación estará disponible en: https://$(grep DOMAIN_NAME .env | cut -d '=' -f2)"
