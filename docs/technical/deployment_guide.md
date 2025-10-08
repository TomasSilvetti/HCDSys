# Guía de Despliegue - HCDSys

Esta guía proporciona instrucciones detalladas para desplegar el sistema HCDSys en un entorno de producción.

## Requisitos Previos

### Hardware Recomendado

- **CPU**: 4 núcleos o más
- **RAM**: 8GB mínimo, 16GB recomendado
- **Almacenamiento**: 50GB mínimo, SSD recomendado
- **Red**: Conexión estable con ancho de banda mínimo de 10Mbps

### Software Requerido

- **Sistema Operativo**: Ubuntu Server 22.04 LTS o superior
- **Docker**: versión 24.0.0 o superior
- **Docker Compose**: versión 2.20.0 o superior
- **Nginx**: versión 1.22.0 o superior (si no se usa la versión de Docker)
- **Certbot**: Para certificados SSL (Let's Encrypt)

## Arquitectura de Despliegue

El sistema HCDSys se despliega utilizando contenedores Docker orquestados con Docker Compose, lo que facilita la configuración y el mantenimiento.

```
                   Internet
                      |
                      v
                 [Firewall]
                      |
                      v
                  [Nginx]
                      |
          +-----------+-----------+
          |                       |
          v                       v
   [Frontend Container]    [Backend Container]
                                  |
                                  v
                         [PostgreSQL Container]
                                  |
                                  v
                         [Volumen de Datos]
```

## Preparación del Servidor

### 1. Actualizar el Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Instalar Docker y Docker Compose

```bash
# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Añadir repositorio de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce

# Añadir usuario al grupo docker
sudo usermod -aG docker ${USER}

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalaciones
docker --version
docker-compose --version
```

### 3. Configurar Firewall

```bash
# Instalar UFW si no está instalado
sudo apt install -y ufw

# Configurar reglas básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Activar firewall
sudo ufw enable
```

## Despliegue del Sistema

### 1. Clonar el Repositorio

```bash
# Crear directorio para la aplicación
sudo mkdir -p /var/www/hcdsys
sudo chown -R $USER:$USER /var/www/hcdsys

# Clonar el repositorio
git clone https://github.com/tu-usuario/hcdsys.git /var/www/hcdsys
cd /var/www/hcdsys
```

### 2. Configurar Variables de Entorno

Crear un archivo `.env` en el directorio raíz:

```bash
# Crear archivo .env
cat > .env << EOL
# Configuración de la base de datos
DB_NAME=hcdsys_prod
DB_USER=hcdsys_user
DB_PASSWORD=<contraseña_segura>

# Configuración de seguridad
SECRET_KEY=<clave_secreta_generada>
CORS_ORIGINS=https://tu-dominio.com

# Configuración del dominio
DOMAIN_NAME=tu-dominio.com
EMAIL=admin@tu-dominio.com
EOL

# Generar clave secreta
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/<clave_secreta_generada>/$SECRET_KEY/g" .env

# Generar contraseña segura para la base de datos
DB_PASSWORD=$(openssl rand -base64 16)
sed -i "s/<contraseña_segura>/$DB_PASSWORD/g" .env

# Reemplazar dominio
read -p "Ingresa el dominio (ej: hcdsys.example.com): " DOMAIN
sed -i "s/tu-dominio.com/$DOMAIN/g" .env

# Reemplazar email
read -p "Ingresa el email de administrador: " EMAIL
sed -i "s/admin@tu-dominio.com/$EMAIL/g" .env
```

### 3. Construir y Desplegar con Docker Compose

```bash
# Construir las imágenes
docker-compose build

# Iniciar los servicios en segundo plano
docker-compose up -d
```

### 4. Configurar Certificados SSL

```bash
# Detener Nginx temporalmente
docker-compose stop nginx

# Obtener certificados SSL con Certbot
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot \
  -d $(grep DOMAIN_NAME .env | cut -d '=' -f2) \
  --email $(grep EMAIL .env | cut -d '=' -f2) \
  --agree-tos --no-eff-email

# Reiniciar Nginx para cargar certificados
docker-compose start nginx
```

### 5. Verificar el Despliegue

```bash
# Verificar que todos los contenedores están en ejecución
docker-compose ps

# Verificar logs
docker-compose logs -f
```

## Configuración de Base de Datos

### 1. Aplicar Migraciones

```bash
# Ejecutar migraciones de Alembic
docker-compose exec backend alembic upgrade head
```

### 2. Crear Usuario Administrador Inicial

```bash
# Ejecutar script de inicialización
docker-compose exec backend python -m app.scripts.create_admin \
  --email admin@tu-dominio.com \
  --password <contraseña_admin> \
  --first-name Admin \
  --last-name User
```

## Configuración de Nginx

El archivo `nginx.conf` ya está configurado para:

- Redirigir HTTP a HTTPS
- Servir archivos estáticos del frontend
- Proxy inverso para la API del backend
- Configuración de seguridad (HSTS, X-Content-Type-Options, etc.)
- Compresión de respuestas

## Configuración de Respaldos

### 1. Respaldo de Base de Datos

Crear un script de respaldo en `/var/www/hcdsys/scripts/backup_db.sh`:

```bash
#!/bin/bash

# Configuración
BACKUP_DIR="/var/www/hcdsys/backups/db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTAINER_NAME="hcdsys-db"
DB_NAME="hcdsys_prod"
DB_USER="hcdsys_user"
RETENTION_DAYS=30

# Crear directorio de respaldos si no existe
mkdir -p $BACKUP_DIR

# Realizar respaldo
docker exec $CONTAINER_NAME pg_dump -U $DB_USER -d $DB_NAME -F c -f /tmp/backup_$TIMESTAMP.dump
docker cp $CONTAINER_NAME:/tmp/backup_$TIMESTAMP.dump $BACKUP_DIR/
docker exec $CONTAINER_NAME rm /tmp/backup_$TIMESTAMP.dump

# Comprimir respaldo
gzip $BACKUP_DIR/backup_$TIMESTAMP.dump

# Eliminar respaldos antiguos
find $BACKUP_DIR -type f -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete

echo "Respaldo completado: $BACKUP_DIR/backup_$TIMESTAMP.dump.gz"
```

Configurar permisos y programar con cron:

```bash
chmod +x /var/www/hcdsys/scripts/backup_db.sh

# Añadir a crontab para ejecución diaria a las 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /var/www/hcdsys/scripts/backup_db.sh >> /var/log/hcdsys_backup.log 2>&1") | crontab -
```

### 2. Respaldo de Documentos

Crear un script de respaldo en `/var/www/hcdsys/scripts/backup_docs.sh`:

```bash
#!/bin/bash

# Configuración
BACKUP_DIR="/var/www/hcdsys/backups/documents"
DOCS_DIR="/var/www/hcdsys/storage/documents"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

# Crear directorio de respaldos si no existe
mkdir -p $BACKUP_DIR

# Realizar respaldo
tar -czf $BACKUP_DIR/documents_$TIMESTAMP.tar.gz $DOCS_DIR

# Eliminar respaldos antiguos
find $BACKUP_DIR -type f -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Respaldo completado: $BACKUP_DIR/documents_$TIMESTAMP.tar.gz"
```

Configurar permisos y programar con cron:

```bash
chmod +x /var/www/hcdsys/scripts/backup_docs.sh

# Añadir a crontab para ejecución semanal los domingos a las 3 AM
(crontab -l 2>/dev/null; echo "0 3 * * 0 /var/www/hcdsys/scripts/backup_docs.sh >> /var/log/hcdsys_backup.log 2>&1") | crontab -
```

## Monitoreo y Mantenimiento

### 1. Configuración de Logs

Los logs se almacenan en:

- **Backend**: `/var/www/hcdsys/logs/`
- **Nginx**: `/var/log/nginx/`
- **Docker**: Accesibles mediante `docker-compose logs`

### 2. Monitoreo con Prometheus y Grafana

```bash
# Clonar repositorio de configuración de monitoreo
git clone https://github.com/tu-usuario/hcdsys-monitoring.git /var/www/hcdsys-monitoring
cd /var/www/hcdsys-monitoring

# Iniciar servicios de monitoreo
docker-compose up -d
```

Acceder a Grafana en `https://tu-dominio.com:3000` con las credenciales por defecto (admin/admin) y cambiar la contraseña.

### 3. Actualizaciones del Sistema

```bash
# Detener servicios
cd /var/www/hcdsys
docker-compose down

# Actualizar código
git pull

# Reconstruir imágenes
docker-compose build

# Aplicar migraciones
docker-compose up -d db
sleep 10  # Esperar a que la base de datos esté lista
docker-compose run --rm backend alembic upgrade head

# Iniciar servicios
docker-compose up -d
```

## Solución de Problemas

### Verificar Estado de los Servicios

```bash
docker-compose ps
```

### Revisar Logs

```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
```

### Problemas Comunes

1. **Error de conexión a la base de datos**:
   - Verificar que el contenedor de PostgreSQL está en ejecución
   - Comprobar credenciales en `.env`
   - Verificar logs: `docker-compose logs db`

2. **Error 502 Bad Gateway**:
   - Verificar que el backend está en ejecución
   - Comprobar logs: `docker-compose logs backend`
   - Verificar configuración de Nginx

3. **Certificado SSL expirado**:
   - Renovar certificado: `docker-compose run --rm certbot renew`
   - Reiniciar Nginx: `docker-compose restart nginx`

## Contacto y Soporte

Para obtener ayuda adicional, contactar a:

- Soporte Técnico: soporte@tu-dominio.com
- Desarrollador Principal: desarrollador@tu-dominio.com
