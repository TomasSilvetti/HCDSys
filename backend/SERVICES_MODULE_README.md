# Módulo Services - HCDSys Backend

## 📋 Resumen

Este documento describe el módulo `services` creado para resolver el error de deployment en Render.com.

## 🐛 Problema Original

Durante el deployment en Render.com, el script `start.sh` intentaba importar `app.services.user_service`, que no existía, causando el siguiente error:

```
ModuleNotFoundError: No module named 'app.services'
```

## ✅ Solución Implementada

Se creó una estructura completa de servicios siguiendo las mejores prácticas de arquitectura de software:

### Estructura de Archivos Creados

```
backend/app/
├── services/
│   ├── __init__.py          # Exporta UserService
│   └── user_service.py      # Lógica de negocio para usuarios
└── schemas/
    ├── __init__.py          # Exporta schemas de usuario
    └── user.py              # Schemas Pydantic para validación
```

### Componentes Principales

#### 1. UserService (`app/services/user_service.py`)

Servicio completo para la gestión de usuarios con los siguientes métodos:

- **Autenticación:**
  - `authenticate_user()` - Autentica usuario con email y contraseña
  - `verify_password()` - Verifica contraseñas
  - `get_password_hash()` - Genera hash de contraseñas

- **CRUD de Usuarios:**
  - `create_user()` - Crea un nuevo usuario
  - `update_user()` - Actualiza un usuario existente
  - `get_user_by_id()` - Obtiene usuario por ID
  - `get_user_by_email()` - Obtiene usuario por email
  - `get_user_by_dni()` - Obtiene usuario por DNI
  - `get_users()` - Lista usuarios con paginación

- **Gestión de Estado:**
  - `activate_user()` - Activa un usuario
  - `deactivate_user()` - Desactiva un usuario

- **Administración:**
  - `create_admin_user()` - Crea usuario administrador (usado en deployment)

#### 2. Schemas (`app/schemas/user.py`)

Schemas Pydantic para validación de datos:

- `UserBase` - Schema base con campos comunes
- `UserCreate` - Para crear usuarios (incluye validación de contraseña)
- `UserUpdate` - Para actualizar usuarios
- `UserInDB` - Representación de usuario en BD
- `UserBasic` - Información básica (sin datos sensibles)
- `User` - Schema completo

**Validaciones Incluidas:**
- DNI: 7-8 dígitos numéricos
- Contraseña: Mínimo 8 caracteres, al menos una mayúscula
- Email: Validación con EmailStr de Pydantic

#### 3. Script de Inicio Actualizado

El archivo `start.sh` fue modificado para usar el nuevo servicio:

```python
from app.db.database import SessionLocal
from app.services.user_service import UserService

db = SessionLocal()
try:
    user_service = UserService(db)
    user_service.create_admin_user(
        email='admin@hcdsys.com',
        password='Admin123!',
        nombre='Administrador',
        apellido='del Sistema',
        dni='00000000'
    )
    print('✅ Usuario admin verificado/creado')
except Exception as e:
    print(f'⚠️  Advertencia al crear admin: {e}')
finally:
    db.close()
```

## 🎯 Beneficios de esta Implementación

1. **Separación de Responsabilidades:** La lógica de negocio está separada de las rutas y modelos
2. **Reutilización:** Los servicios pueden ser usados en cualquier parte de la aplicación
3. **Testeable:** Fácil de probar unitariamente
4. **Escalable:** Fácil agregar nuevos servicios (DocumentService, RoleService, etc.)
5. **Mantenible:** Código organizado y documentado

## 🚀 Uso en la Aplicación

### Ejemplo: Crear un usuario en una ruta

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services import UserService
from app.schemas.user import UserCreate
from app.db.database import get_db

router = APIRouter()

@router.post("/users/")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    try:
        user = user_service.create_user(user_data)
        return {"message": "Usuario creado", "user_id": user.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 🔧 Próximos Pasos Sugeridos

1. Crear `DocumentService` para la lógica de documentos
2. Crear `RoleService` para la gestión de roles y permisos
3. Agregar tests unitarios para los servicios
4. Implementar caché para consultas frecuentes
5. Agregar logging detallado en los servicios

## 📝 Notas Técnicas

- **Pydantic v2:** Se usa `from_attributes = True` en lugar de `orm_mode = True`
- **Seguridad:** Las contraseñas se hashean con bcrypt
- **Base de Datos:** Compatible con PostgreSQL (usado en Render.com)
- **Validación:** Todas las entradas son validadas con Pydantic

## ✅ Verificación

El módulo fue probado exitosamente y está listo para deployment en Render.com.

---

**Fecha de Creación:** 2024-11-14  
**Autor:** Sistema HCDSys  
**Versión:** 1.0.0

