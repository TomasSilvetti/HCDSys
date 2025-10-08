import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.init_roles import init_roles_and_permissions

# Crear una sesión de base de datos
db = SessionLocal()

try:
    # Inicializar roles y permisos
    init_roles_and_permissions(db)
    print("Roles y permisos inicializados correctamente")
finally:
    db.close()