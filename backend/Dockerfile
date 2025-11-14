FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Dar permisos de ejecución al script de inicio
RUN chmod +x start.sh

# Crear directorios necesarios
# /tmp/documents: almacenamiento temporal (se pierde al reiniciar)
# /app/logs: logs de la aplicación
RUN mkdir -p /tmp/documents /app/logs && \
    chmod 777 /tmp/documents

# Exponer el puerto
EXPOSE 8000

# Iniciar usando el script de inicio
CMD ["./start.sh"]
