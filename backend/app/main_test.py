from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Crear la aplicación FastAPI
app = FastAPI(
    title="HCDSys API",
    description="API para el Sistema de Gestión de Documentos HCDSys",
    version="0.1.0"
)

# Importar rutas
from .routes import auth, documents, users, roles, permissions, websockets, security, document_history

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para pruebas, en producción especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(users.router, prefix="/users", tags=["Usuarios"])
app.include_router(roles.router, prefix="/roles", tags=["Roles"])
app.include_router(permissions.router, prefix="/permissions", tags=["Permisos"])
app.include_router(documents.router, prefix="/documents", tags=["Documentos"])
app.include_router(document_history.router, prefix="/document-history", tags=["Historial de Documentos"])
app.include_router(security.router, prefix="/security", tags=["Seguridad"])
app.include_router(websockets.router, tags=["WebSockets"])

@app.get("/", tags=["Raíz"])
async def root():
    """
    Endpoint raíz que devuelve un mensaje de bienvenida
    """
    return {"message": "Bienvenido a la API de HCDSys"}
