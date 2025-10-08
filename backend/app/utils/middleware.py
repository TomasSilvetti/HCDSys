import time
from datetime import datetime, timedelta
from typing import Callable, List, Optional, Dict, Any
from fastapi import Request, Response, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from ..db import models, schemas
from ..db.database import get_db
from .config import settings
from .security import check_permission

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware para autenticación de usuarios.
    Verifica el token JWT en los headers y extrae la información del usuario.
    """
    
    def __init__(self, app, db_func=get_db):
        super().__init__(app)
        self.db_func = db_func
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
        # Rutas que no requieren autenticación
        self.public_paths = [
            "/api/auth/login",
            "/api/auth/register",
            "/api/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Iniciar temporizador para medir tiempo de respuesta
        start_time = time.time()
        
        # Extraer información de la solicitud
        path = request.url.path
        method = request.method
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Variables para registro
        user_id = None
        is_authenticated = False
        response_code = 200
        error_message = None
        
        # Verificar si la ruta es pública
        if any(path.startswith(public_path) for public_path in self.public_paths):
            # Ruta pública, no se requiere autenticación
            response = await call_next(request)
            response_code = response.status_code
        else:
            # Ruta protegida, verificar autenticación
            db = next(self.db_func())
            try:
                # Extraer token
                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="No se proporcionó token de autenticación",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                token = auth_header.split(" ")[1]
                
                # Verificar token
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                    email: str = payload.get("sub")
                    if email is None:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token inválido",
                            headers={"WWW-Authenticate": "Bearer"},
                        )
                except JWTError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token inválido o expirado",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Obtener usuario
                user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Usuario no encontrado",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Verificar si el usuario está activo
                if not user.activo:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Usuario inactivo. Contacte al administrador."
                    )
                
                # Actualizar último acceso
                user.ultimo_acceso = datetime.utcnow()
                db.commit()
                
                # Añadir usuario a la solicitud para que esté disponible en los endpoints
                request.state.user = user
                user_id = user.id
                is_authenticated = True
                
                # Continuar con la solicitud
                response = await call_next(request)
                response_code = response.status_code
                
            except HTTPException as e:
                response_code = e.status_code
                error_message = e.detail
                # Crear respuesta de error
                response = Response(
                    content={"detail": e.detail}.get("detail", "Error de autenticación"),
                    status_code=e.status_code,
                    media_type="application/json"
                )
                if e.headers:
                    for name, value in e.headers.items():
                        response.headers[name] = value
            except Exception as e:
                response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                error_message = str(e)
                response = Response(
                    content={"detail": "Error interno del servidor"}.get("detail"),
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    media_type="application/json"
                )
            finally:
                # Registrar intento de acceso
                end_time = time.time()
                tiempo_respuesta = (end_time - start_time) * 1000  # en milisegundos
                
                try:
                    # Crear registro de acceso
                    registro = models.RegistroAcceso(
                        usuario_id=user_id,
                        ip_address=client_host,
                        user_agent=user_agent,
                        endpoint=path,
                        metodo=method,
                        exitoso=(response_code < 400),
                        codigo_respuesta=response_code,
                        mensaje_error=error_message,
                        tiempo_respuesta=tiempo_respuesta
                    )
                    db.add(registro)
                    db.commit()
                except Exception as e:
                    print(f"Error al registrar acceso: {str(e)}")
                    db.rollback()
                finally:
                    db.close()
        
        return response

class AuthorizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware para autorización basada en permisos.
    Verifica si el usuario tiene los permisos necesarios para acceder a un recurso.
    """
    
    def __init__(self, app, db_func=get_db):
        super().__init__(app)
        self.db_func = db_func
        # Definición de permisos requeridos por ruta
        self.route_permissions: Dict[str, Dict[str, List[str]]] = {
            # Rutas de usuarios
            "/api/users": {
                "GET": ["users:view"],
                "POST": ["users:create"],
            },
            "/api/users/{user_id}": {
                "GET": ["users:view"],
                "PUT": ["users:edit"],
                "DELETE": ["users:deactivate"],
            },
            # Rutas de documentos
            "/api/documents": {
                "GET": ["docs:view"],
                "POST": ["docs:create"],
            },
            "/api/documents/{documento_id}": {
                "GET": ["docs:view"],
                "PUT": ["docs:edit"],
                "DELETE": ["docs:delete"],
            },
            # Rutas de roles
            "/api/roles": {
                "GET": ["admin:roles:manage"],
            },
            "/api/roles/{role_id}": {
                "GET": ["admin:roles:manage"],
            },
            "/api/roles/users/{user_id}": {
                "PUT": ["admin:roles:manage"],
            },
            # Rutas de permisos
            "/api/permissions/categories": {
                "GET": ["admin:permissions:manage"],
            },
            "/api/permissions": {
                "GET": ["admin:permissions:manage"],
            },
            "/api/permissions/roles/{role_id}": {
                "GET": ["admin:permissions:manage"],
            },
            "/api/permissions/roles/assign": {
                "POST": ["admin:permissions:manage"],
            },
            "/api/permissions/roles/remove": {
                "POST": ["admin:permissions:manage"],
            },
        }
        # Rutas que no requieren autorización
        self.public_paths = [
            "/api/auth/login",
            "/api/auth/register",
            "/api/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
    
    def _get_required_permissions(self, path: str, method: str) -> List[str]:
        """
        Obtiene los permisos requeridos para una ruta y método específicos.
        """
        # Verificar rutas exactas
        if path in self.route_permissions and method in self.route_permissions[path]:
            return self.route_permissions[path][method]
        
        # Verificar rutas con parámetros
        for route_pattern, methods in self.route_permissions.items():
            if "{" in route_pattern:
                # Convertir patrón de ruta a una expresión regular
                import re
                pattern = route_pattern.replace("{", "(?P<").replace("}", ">[^/]+)")
                match = re.match(f"^{pattern}$", path)
                if match and method in methods:
                    return methods[method]
        
        # Si no se encuentra una coincidencia, no se requieren permisos específicos
        return []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extraer información de la solicitud
        path = request.url.path
        method = request.method
        
        # Verificar si la ruta es pública
        if any(path.startswith(public_path) for public_path in self.public_paths):
            # Ruta pública, no se requiere autorización
            return await call_next(request)
        
        # Verificar si el usuario está autenticado
        if not hasattr(request.state, "user"):
            # Si no hay usuario autenticado, continuar con la solicitud
            # El middleware de autenticación debería haber manejado esto
            return await call_next(request)
        
        # Obtener permisos requeridos
        required_permissions = self._get_required_permissions(path, method)
        
        # Si no se requieren permisos específicos, continuar con la solicitud
        if not required_permissions:
            return await call_next(request)
        
        # Verificar permisos
        db = next(self.db_func())
        try:
            user = request.state.user
            
            # Verificar cada permiso requerido
            for permission_code in required_permissions:
                if not check_permission(user, permission_code, db):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"No tiene permiso para acceder a este recurso: {permission_code}"
                    )
            
            # Si tiene todos los permisos, continuar con la solicitud
            return await call_next(request)
            
        except HTTPException as e:
            return Response(
                content={"detail": e.detail}.get("detail", "Error de autorización"),
                status_code=e.status_code,
                media_type="application/json"
            )
        finally:
            db.close()

class IPBlockMiddleware(BaseHTTPMiddleware):
    """
    Middleware para bloquear IPs que han realizado demasiados intentos fallidos.
    """
    
    def __init__(self, app, db_func=get_db):
        super().__init__(app)
        self.db_func = db_func
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Obtener IP del cliente
        client_host = request.client.host if request.client else "unknown"
        
        # Verificar si la IP está bloqueada
        db = next(self.db_func())
        try:
            # Buscar bloqueo activo para esta IP
            bloqueo = db.query(models.BloqueoIP).filter(
                models.BloqueoIP.ip_address == client_host,
                models.BloqueoIP.activo == True,
                models.BloqueoIP.fecha_fin > datetime.utcnow()
            ).first()
            
            if bloqueo:
                # IP bloqueada, devolver error 403
                tiempo_restante = bloqueo.fecha_fin - datetime.utcnow()
                minutos_restantes = int(tiempo_restante.total_seconds() / 60)
                
                return Response(
                    content={"detail": f"Acceso bloqueado temporalmente. Intente nuevamente en {minutos_restantes} minutos."}.get("detail"),
                    status_code=status.HTTP_403_FORBIDDEN,
                    media_type="application/json"
                )
            
            # IP no bloqueada, continuar con la solicitud
            return await call_next(request)
            
        finally:
            db.close()

def require_permissions(permission_codes: List[str]):
    """
    Dependencia para verificar permisos específicos en endpoints individuales.
    Más granular que el middleware de autorización.
    """
    async def _require_permissions(
        request: Request,
        db: Session = Depends(get_db)
    ):
        # Verificar si el usuario está autenticado
        if not hasattr(request.state, "user"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autenticado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = request.state.user
        
        # Verificar cada permiso requerido
        for permission_code in permission_codes:
            if not check_permission(user, permission_code, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No tiene permiso para realizar esta acción: {permission_code}"
                )
        
        return True
    
    return _require_permissions

# Función para verificar intentos fallidos y bloquear IP si es necesario
def check_and_block_ip(email: str, ip_address: str, db: Session):
    """
    Verifica si una IP ha realizado demasiados intentos fallidos y la bloquea si es necesario.
    """
    # Configuración
    MAX_INTENTOS_FALLIDOS = 5  # Número máximo de intentos fallidos permitidos
    PERIODO_VERIFICACION = 10  # Minutos para verificar intentos fallidos
    DURACION_BLOQUEO = 30  # Minutos de bloqueo
    
    # Verificar intentos fallidos recientes
    desde = datetime.utcnow() - timedelta(minutes=PERIODO_VERIFICACION)
    intentos_fallidos = db.query(models.IntentosLogin).filter(
        models.IntentosLogin.ip_address == ip_address,
        models.IntentosLogin.exitoso == False,
        models.IntentosLogin.fecha >= desde
    ).count()
    
    # Si hay demasiados intentos fallidos, bloquear IP
    if intentos_fallidos >= MAX_INTENTOS_FALLIDOS:
        # Verificar si ya existe un bloqueo activo
        bloqueo_existente = db.query(models.BloqueoIP).filter(
            models.BloqueoIP.ip_address == ip_address,
            models.BloqueoIP.activo == True
        ).first()
        
        if not bloqueo_existente:
            # Crear nuevo bloqueo
            fecha_fin = datetime.utcnow() + timedelta(minutes=DURACION_BLOQUEO)
            bloqueo = models.BloqueoIP(
                ip_address=ip_address,
                motivo="intentos_fallidos",
                fecha_fin=fecha_fin
            )
            db.add(bloqueo)
            db.commit()
            
            return True, DURACION_BLOQUEO
    
    return False, 0
