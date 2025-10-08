"""
Configuración de Gunicorn para producción
"""
import multiprocessing

# Configuración básica - reducida para evitar problemas de memoria
bind = "0.0.0.0:8000"
workers = 2  # Reducido a solo 2 workers
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 500  # Reducido a la mitad
max_requests_jitter = 50
timeout = 60  # Aumentado para dar más tiempo a las operaciones
keepalive = 5

# Logging - simplificado para evitar problemas de recursión
accesslog = "-"  # Enviar a stdout en lugar de archivo
errorlog = "-"   # Enviar a stderr en lugar de archivo
loglevel = "warning"  # Reducir el nivel de log

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de rendimiento - reducida para evitar problemas de memoria
worker_connections = 500  # Reducido a la mitad
