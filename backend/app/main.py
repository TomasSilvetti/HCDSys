from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .db.database import engine, Base, get_db
from .routes import auth, documents, users, roles, permissions, websockets, security, document_history
from .utils.config import settings
from .db.init_roles import init_roles_and_permissions
from .utils.middleware import AuthenticationMiddleware, AuthorizationMiddleware, IPBlockMiddleware

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HCDSys API",
    description="API para el Sistema de Gestión Documental del HCD",
    version="0.1.0"
)

# Configuración de CORS
import logging
cors_logger = logging.getLogger("app.cors")

# Obtener orígenes permitidos
cors_origins = settings.CORS_ORIGINS.split(",")
cors_logger.info(f"Configurando CORS con orígenes permitidos: {cors_origins}")

# Asegurar que localhost:5173 esté incluido para desarrollo
if "http://localhost:5173" not in cors_origins:
    cors_origins.append("http://localhost:5173")
    cors_logger.info(f"Añadido origen http://localhost:5173 para desarrollo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cors_logger.info(f"Middleware CORS configurado con éxito. Orígenes permitidos: {cors_origins}")

# Añadir middlewares de seguridad
# El orden es importante: primero IPBlock, luego Authentication, finalmente Authorization
app.add_middleware(IPBlockMiddleware)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(AuthorizationMiddleware)

# Incluir rutas
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(document_history.router, prefix="/api", tags=["document_history"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(roles.router, prefix="/api", tags=["roles"])
app.include_router(permissions.router, prefix="/api", tags=["permissions"])
app.include_router(security.router, prefix="/api", tags=["security"])
app.include_router(websockets.router, prefix="/api")

@app.get("/api/health")
def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "ok", "version": app.version}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Evento de inicio para inicializar roles y permisos
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    try:
        # Inicializar roles y permisos
        init_roles_and_permissions(db)
    finally:
        db.close()

# Configurar tareas periódicas
@app.on_event("startup")
async def setup_periodic_tasks():
    import asyncio
    from .utils.tasks import verify_document_integrity, cleanup_old_backups
    
    async def run_periodic_tasks():
        while True:
            # Verificar integridad de documentos cada 24 horas
            try:
                db = next(get_db())
                try:
                    await verify_document_integrity(db)
                    await cleanup_old_backups(db, 30)  # Mantener respaldos por 30 días
                finally:
                    db.close()
            except Exception as e:
                print(f"Error en tareas periódicas: {str(e)}")
            
            # Esperar 24 horas
            await asyncio.sleep(24 * 60 * 60)
    
    # Iniciar tareas en segundo plano
    asyncio.create_task(run_periodic_tasks())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)
