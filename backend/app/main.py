from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from .db.database import engine, Base
from .routes import auth, documents, users
from .utils.config import settings

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

# Incluir rutas
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(users.router, prefix="/api", tags=["users"])

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)
