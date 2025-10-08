import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.init_roles import create_admin_user
from passlib.context import CryptContext

# Configurar el contexto de contraseña
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Crear una sesión de base de datos
db = SessionLocal()

try:
    # Datos del administrador
    email = "admin@example.com"
    password = "Admin123!"
    nombre = "Administrador"
    apellido = "Sistema"
    dni = "12345678"
    
    # Hashear la contraseña
    password_hash = pwd_context.hash(password)
    
    # Crear el usuario administrador
    create_admin_user(db, email, password_hash, nombre, apellido, dni)
    
    print(f"Usuario administrador creado: {email}")
    print(f"Contraseña: {password}")
finally:
    db.close()