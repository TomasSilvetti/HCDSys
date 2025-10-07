from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..utils.config import settings

# Crear motor de base de datos
engine = create_engine(settings.DATABASE_URL)

# Crear sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear base para modelos declarativos
Base = declarative_base()

# Dependencia para obtener la sesión de base de datos
def get_db():
    """
    Dependencia para obtener una sesión de base de datos.
    Utilizar como parámetro en endpoints que requieran acceso a la base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
