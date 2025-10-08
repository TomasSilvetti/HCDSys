"""
Script para inicializar las categorías y tipos de documentos en la base de datos.
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.models import Categoria, TipoDocumento
from app.utils.config import settings

def init_categories_types():
    """
    Inicializa las categorías y tipos de documentos en la base de datos.
    """
    # Crear conexión a la base de datos
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar si ya existen categorías
        existing_categories = db.query(Categoria).count()
        if existing_categories == 0:
            print("Creando categorías...")
            categories = [
                Categoria(nombre="Administrativo", descripcion="Documentos administrativos internos"),
                Categoria(nombre="Legal", descripcion="Documentos legales y jurídicos"),
                Categoria(nombre="Técnico", descripcion="Documentos técnicos y de ingeniería"),
                Categoria(nombre="Financiero", descripcion="Documentos financieros y contables"),
                Categoria(nombre="Recursos Humanos", descripcion="Documentos relacionados con personal"),
                Categoria(nombre="Proyectos", descripcion="Documentos de proyectos específicos")
            ]
            
            db.add_all(categories)
            db.commit()
            print(f"Se crearon {len(categories)} categorías.")
        else:
            print(f"Ya existen {existing_categories} categorías en la base de datos.")
        
        # Verificar si ya existen tipos de documento
        existing_types = db.query(TipoDocumento).count()
        if existing_types == 0:
            print("Creando tipos de documento...")
            document_types = [
                TipoDocumento(
                    nombre="PDF", 
                    descripcion="Documento en formato PDF", 
                    extensiones_permitidas=".pdf"
                ),
                TipoDocumento(
                    nombre="Word", 
                    descripcion="Documento de Microsoft Word", 
                    extensiones_permitidas=".doc,.docx"
                ),
                TipoDocumento(
                    nombre="Excel", 
                    descripcion="Hoja de cálculo de Microsoft Excel", 
                    extensiones_permitidas=".xls,.xlsx"
                ),
                TipoDocumento(
                    nombre="PowerPoint", 
                    descripcion="Presentación de Microsoft PowerPoint", 
                    extensiones_permitidas=".ppt,.pptx"
                ),
                TipoDocumento(
                    nombre="Imagen", 
                    descripcion="Archivo de imagen", 
                    extensiones_permitidas=".jpg,.jpeg,.png,.gif"
                ),
                TipoDocumento(
                    nombre="Texto", 
                    descripcion="Archivo de texto plano", 
                    extensiones_permitidas=".txt"
                )
            ]
            
            db.add_all(document_types)
            db.commit()
            print(f"Se crearon {len(document_types)} tipos de documento.")
        else:
            print(f"Ya existen {existing_types} tipos de documento en la base de datos.")
            
    except Exception as e:
        db.rollback()
        print(f"Error al inicializar categorías y tipos de documento: {str(e)}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_categories_types()
    print("Inicialización completada.")
