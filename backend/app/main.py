from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .db.database import engine, Base, get_db
from .routes import auth, documents, users, roles, permissions, websockets, security
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Añadir middlewares de seguridad
# El orden es importante: primero IPBlock, luego Authentication, finalmente Authorization
app.add_middleware(IPBlockMiddleware)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(AuthorizationMiddleware)

# Incluir rutas
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)
