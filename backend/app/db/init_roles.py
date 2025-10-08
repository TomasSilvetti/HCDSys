from sqlalchemy.orm import Session
from . import models

# Definición de roles predefinidos
ROLES = [
    {
        "id": 1,
        "nombre": "Administrador",
        "descripcion": "Acceso completo al sistema, gestión de usuarios y configuraciones"
    },
    {
        "id": 2,
        "nombre": "Gestor de Documentos",
        "descripcion": "Puede crear, editar y gestionar documentos en el sistema"
    },
    {
        "id": 3,
        "nombre": "Usuario de Consulta",
        "descripcion": "Acceso de solo lectura a documentos según permisos asignados"
    }
]

# Definición de categorías de permisos
CATEGORIAS_PERMISO = [
    {
        "id": 1,
        "nombre": "Administración del Sistema",
        "descripcion": "Permisos para administrar el sistema",
        "codigo": "admin"
    },
    {
        "id": 2,
        "nombre": "Gestión de Documentos",
        "descripcion": "Permisos para gestionar documentos",
        "codigo": "docs"
    },
    {
        "id": 3,
        "nombre": "Gestión de Usuarios",
        "descripcion": "Permisos para gestionar usuarios",
        "codigo": "users"
    },
    {
        "id": 4,
        "nombre": "Búsqueda y Consulta",
        "descripcion": "Permisos para buscar y consultar información",
        "codigo": "search"
    }
]

# Definición de permisos del sistema
PERMISOS = [
    # Permisos de administración del sistema
    {
        "id": 1,
        "nombre": "Gestionar usuarios",
        "descripcion": "Permite crear, editar y eliminar usuarios",
        "codigo": "admin:users:manage",
        "categoria_id": 1,
        "es_critico": True
    },
    {
        "id": 2,
        "nombre": "Gestionar roles",
        "descripcion": "Permite asignar y modificar roles de usuarios",
        "codigo": "admin:roles:manage",
        "categoria_id": 1,
        "es_critico": True
    },
    {
        "id": 3,
        "nombre": "Ver historial del sistema",
        "descripcion": "Permite ver el historial completo de acciones en el sistema",
        "codigo": "admin:history:view",
        "categoria_id": 1,
        "es_critico": False
    },
    {
        "id": 4,
        "nombre": "Gestionar permisos",
        "descripcion": "Permite asignar y modificar permisos de roles",
        "codigo": "admin:permissions:manage",
        "categoria_id": 1,
        "es_critico": True
    },
    {
        "id": 5,
        "nombre": "Configurar sistema",
        "descripcion": "Permite modificar configuraciones generales del sistema",
        "codigo": "admin:system:config",
        "categoria_id": 1,
        "es_critico": True
    },
    
    # Permisos de gestión de documentos
    {
        "id": 6,
        "nombre": "Crear documentos",
        "descripcion": "Permite crear nuevos documentos en el sistema",
        "codigo": "docs:create",
        "categoria_id": 2,
        "es_critico": False
    },
    {
        "id": 7,
        "nombre": "Editar documentos",
        "descripcion": "Permite editar documentos existentes",
        "codigo": "docs:edit",
        "categoria_id": 2,
        "es_critico": False
    },
    {
        "id": 8,
        "nombre": "Eliminar documentos",
        "descripcion": "Permite eliminar documentos del sistema",
        "codigo": "docs:delete",
        "categoria_id": 2,
        "es_critico": True
    },
    {
        "id": 9,
        "nombre": "Ver documentos",
        "descripcion": "Permite ver documentos en el sistema",
        "codigo": "docs:view",
        "categoria_id": 2,
        "es_critico": False
    },
    {
        "id": 10,
        "nombre": "Descargar documentos",
        "descripcion": "Permite descargar documentos del sistema",
        "codigo": "docs:download",
        "categoria_id": 2,
        "es_critico": False
    },
    {
        "id": 11,
        "nombre": "Gestionar versiones",
        "descripcion": "Permite gestionar versiones de documentos",
        "codigo": "docs:versions:manage",
        "categoria_id": 2,
        "es_critico": False
    },
    {
        "id": 12,
        "nombre": "Ver versiones",
        "descripcion": "Permite ver versiones anteriores de documentos",
        "codigo": "docs:versions:view",
        "categoria_id": 2,
        "es_critico": False
    },
    {
        "id": 13,
        "nombre": "Gestionar categorías",
        "descripcion": "Permite crear, editar y eliminar categorías de documentos",
        "codigo": "docs:categories:manage",
        "categoria_id": 2,
        "es_critico": False
    },
    
    # Permisos de gestión de usuarios
    {
        "id": 14,
        "nombre": "Ver usuarios",
        "descripcion": "Permite ver la lista de usuarios",
        "codigo": "users:view",
        "categoria_id": 3,
        "es_critico": False
    },
    {
        "id": 15,
        "nombre": "Crear usuarios",
        "descripcion": "Permite crear nuevos usuarios",
        "codigo": "users:create",
        "categoria_id": 3,
        "es_critico": True
    },
    {
        "id": 16,
        "nombre": "Editar usuarios",
        "descripcion": "Permite editar información de usuarios",
        "codigo": "users:edit",
        "categoria_id": 3,
        "es_critico": True
    },
    {
        "id": 17,
        "nombre": "Desactivar usuarios",
        "descripcion": "Permite desactivar cuentas de usuario",
        "codigo": "users:deactivate",
        "categoria_id": 3,
        "es_critico": True
    },
    
    # Permisos de búsqueda y consulta
    {
        "id": 18,
        "nombre": "Búsqueda básica",
        "descripcion": "Permite realizar búsquedas básicas en el sistema",
        "codigo": "search:basic",
        "categoria_id": 4,
        "es_critico": False
    },
    {
        "id": 19,
        "nombre": "Búsqueda avanzada",
        "descripcion": "Permite realizar búsquedas avanzadas con filtros complejos",
        "codigo": "search:advanced",
        "categoria_id": 4,
        "es_critico": False
    },
    {
        "id": 20,
        "nombre": "Ver documentos restringidos",
        "descripcion": "Permite ver documentos con restricciones de acceso",
        "codigo": "search:restricted",
        "categoria_id": 4,
        "es_critico": True
    }
]

# Asignación de permisos a roles
ROL_PERMISOS = {
    # Administrador tiene todos los permisos
    1: list(range(1, 21)),  # IDs del 1 al 20
    
    # Gestor de Documentos
    2: [6, 7, 9, 10, 11, 12, 13, 18, 19],  # Permisos de gestión de documentos y búsqueda
    
    # Usuario de Consulta
    3: [9, 10, 12, 18]  # Solo permisos básicos de visualización
}

def init_roles_and_permissions(db: Session):
    """
    Inicializa los roles y permisos predefinidos en la base de datos.
    Solo se ejecuta si no existen roles en la base de datos.
    """
    # Verificar si ya existen roles
    existing_roles = db.query(models.Rol).count()
    if existing_roles > 0:
        print("Los roles ya están inicializados en la base de datos")
        return
    
    # Crear categorías de permisos
    categorias_db = {}
    for categoria in CATEGORIAS_PERMISO:
        categoria_obj = models.CategoriaPermiso(
            id=categoria["id"],
            nombre=categoria["nombre"],
            descripcion=categoria["descripcion"],
            codigo=categoria["codigo"]
        )
        db.add(categoria_obj)
        categorias_db[categoria["id"]] = categoria_obj
    
    # Guardar para obtener IDs de categorías
    db.flush()
    
    # Crear permisos
    permisos_db = {}
    for permiso in PERMISOS:
        permiso_obj = models.Permiso(
            id=permiso["id"],
            nombre=permiso["nombre"],
            descripcion=permiso["descripcion"],
            codigo=permiso["codigo"],
            categoria_id=permiso["categoria_id"],
            es_critico=permiso["es_critico"]
        )
        db.add(permiso_obj)
        permisos_db[permiso["id"]] = permiso_obj
    
    # Crear roles
    roles_db = {}
    for rol in ROLES:
        rol_obj = models.Rol(
            id=rol["id"],
            nombre=rol["nombre"],
            descripcion=rol["descripcion"]
        )
        db.add(rol_obj)
        roles_db[rol["id"]] = rol_obj
    
    # Guardar para obtener IDs
    db.flush()
    
    # Asignar permisos a roles
    for rol_id, permisos_ids in ROL_PERMISOS.items():
        rol_obj = roles_db[rol_id]
        for permiso_id in permisos_ids:
            if permiso_id in permisos_db:
                rol_obj.permisos.append(permisos_db[permiso_id])
    
    # Confirmar cambios
    db.commit()
    print("Roles, categorías y permisos inicializados correctamente")

# Función para crear usuario administrador inicial
def create_admin_user(db: Session, email: str, password_hash: str, nombre: str, apellido: str, dni: str):
    """
    Crea un usuario administrador inicial si no existe.
    """
    # Verificar si ya existe un usuario con ese email
    existing_user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if existing_user:
        print(f"El usuario {email} ya existe")
        return existing_user
    
    # Crear usuario administrador
    admin_user = models.Usuario(
        email=email,
        password_hash=password_hash,
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        role_id=1,  # Rol de Administrador
        activo=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"Usuario administrador {email} creado correctamente")
    return admin_user

# La clase HistorialRol se define en models.py
