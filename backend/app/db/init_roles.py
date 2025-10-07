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

# Definición de permisos del sistema
PERMISOS = [
    # Permisos de administración
    {
        "id": 1,
        "nombre": "Gestionar usuarios",
        "descripcion": "Permite crear, editar y eliminar usuarios",
        "codigo": "admin:users:manage"
    },
    {
        "id": 2,
        "nombre": "Gestionar roles",
        "descripcion": "Permite asignar y modificar roles de usuarios",
        "codigo": "admin:roles:manage"
    },
    {
        "id": 3,
        "nombre": "Ver historial del sistema",
        "descripcion": "Permite ver el historial completo de acciones en el sistema",
        "codigo": "admin:history:view"
    },
    
    # Permisos de documentos
    {
        "id": 4,
        "nombre": "Crear documentos",
        "descripcion": "Permite crear nuevos documentos en el sistema",
        "codigo": "docs:create"
    },
    {
        "id": 5,
        "nombre": "Editar documentos",
        "descripcion": "Permite editar documentos existentes",
        "codigo": "docs:edit"
    },
    {
        "id": 6,
        "nombre": "Eliminar documentos",
        "descripcion": "Permite eliminar documentos del sistema",
        "codigo": "docs:delete"
    },
    {
        "id": 7,
        "nombre": "Ver documentos",
        "descripcion": "Permite ver documentos en el sistema",
        "codigo": "docs:view"
    },
    {
        "id": 8,
        "nombre": "Descargar documentos",
        "descripcion": "Permite descargar documentos del sistema",
        "codigo": "docs:download"
    },
    
    # Permisos de versiones
    {
        "id": 9,
        "nombre": "Gestionar versiones",
        "descripcion": "Permite gestionar versiones de documentos",
        "codigo": "versions:manage"
    },
    {
        "id": 10,
        "nombre": "Ver versiones",
        "descripcion": "Permite ver versiones anteriores de documentos",
        "codigo": "versions:view"
    },
    
    # Permisos de categorías
    {
        "id": 11,
        "nombre": "Gestionar categorías",
        "descripcion": "Permite crear, editar y eliminar categorías de documentos",
        "codigo": "categories:manage"
    }
]

# Asignación de permisos a roles
ROL_PERMISOS = {
    # Administrador tiene todos los permisos
    1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    
    # Gestor de Documentos
    2: [4, 5, 6, 7, 8, 9, 10],
    
    # Usuario de Consulta
    3: [7, 8, 10]
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
    
    # Crear permisos
    permisos_db = {}
    for permiso in PERMISOS:
        permiso_obj = models.Permiso(
            id=permiso["id"],
            nombre=permiso["nombre"],
            descripcion=permiso["descripcion"],
            codigo=permiso["codigo"]
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
            rol_obj.permisos.append(permisos_db[permiso_id])
    
    # Confirmar cambios
    db.commit()
    print("Roles y permisos inicializados correctamente")

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
