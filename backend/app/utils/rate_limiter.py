"""
Módulo para implementar limitación de tasa (rate limiting) en la API
"""
from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..utils.config import settings
import os

# Crear instancia del limitador de tasa sin requerir archivo .env
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

def configure_rate_limiter(app):
    """
    Configura el limitador de tasa para la aplicación FastAPI
    
    Args:
        app: Instancia de FastAPI
    """
    if not settings.ENVIRONMENT == "production" or not getattr(settings, "RATE_LIMIT_ENABLED", False):
        return
    
    # Configurar el limitador en la aplicación
    app.state.limiter = limiter
    app.add_exception_handler(HTTPException, _rate_limit_exception_handler)

async def _rate_limit_exception_handler(request: Request, exc: HTTPException):
    """
    Manejador de excepciones para el limitador de tasa
    """
    if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        return {
            "detail": "Demasiadas solicitudes. Por favor, inténtelo de nuevo más tarde.",
            "status_code": exc.status_code
        }
    raise exc

# Decorador para aplicar límites de tasa a rutas específicas
def rate_limit(limit_string=None):
    """
    Decorador para aplicar límites de tasa a rutas específicas
    
    Args:
        limit_string: Cadena de límite (por ejemplo, "5/minute")
    
    Returns:
        Decorador configurado
    """
    if not settings.ENVIRONMENT == "production" or not getattr(settings, "RATE_LIMIT_ENABLED", False):
        # Si no estamos en producción o el rate limiting está desactivado,
        # devolver un decorador que no hace nada
        def dummy_decorator(func):
            return func
        return dummy_decorator
    
    # Usar el límite predeterminado si no se proporciona uno
    if limit_string is None:
        limit_string = f"{getattr(settings, 'RATE_LIMIT_PER_MINUTE', 60)}/minute"
    
    # Devolver el decorador real
    return limiter.limit(limit_string)
