#!/bin/bash

# Script para desplegar el frontend en producción

# Directorio de destino en el servidor
DEPLOY_DIR="/var/www/hcdsys/frontend"

# Verificar si estamos en la rama principal
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
  echo "⚠️ ADVERTENCIA: No estás en la rama principal (main/master)."
  read -p "¿Deseas continuar con el despliegue? (s/N): " CONTINUE
  if [[ $CONTINUE != "s" && $CONTINUE != "S" ]]; then
    echo "Despliegue cancelado."
    exit 1
  fi
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
npm ci

# Ejecutar pruebas
echo "🧪 Ejecutando pruebas..."
npm test
if [ $? -ne 0 ]; then
  echo "❌ Las pruebas fallaron. Despliegue cancelado."
  exit 1
fi

# Construir la aplicación para producción
echo "🏗️ Construyendo la aplicación para producción..."
npm run build:prod
if [ $? -ne 0 ]; then
  echo "❌ La construcción falló. Despliegue cancelado."
  exit 1
fi

# Crear directorio de despliegue si no existe
echo "📁 Preparando directorio de despliegue..."
mkdir -p $DEPLOY_DIR

# Limpiar directorio de despliegue (preservar algunos archivos si es necesario)
echo "🧹 Limpiando directorio de despliegue..."
find $DEPLOY_DIR -mindepth 1 -maxdepth 1 ! -name ".env*" -exec rm -rf {} \;

# Copiar archivos de construcción al directorio de despliegue
echo "📋 Copiando archivos al directorio de despliegue..."
cp -r dist/* $DEPLOY_DIR/

# Verificar que el archivo index.html existe en el directorio de despliegue
if [ ! -f "$DEPLOY_DIR/index.html" ]; then
  echo "❌ El archivo index.html no se encontró en el directorio de despliegue. Algo salió mal."
  exit 1
fi

echo "✅ Despliegue completado con éxito."
echo "🌐 La aplicación está disponible en: https://hcdsys.example.com"
