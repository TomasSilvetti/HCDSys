# Historia de Usuario: Registro de Usuario 🔴

## HU002: Registro de Usuario Básico
Como visitante del sistema
Quiero poder registrarme como usuario
Para poder acceder a las funcionalidades básicas del sistema

### Criterios de Aceptación
1. Dado que soy un visitante
   Cuando hago clic en "Registrarse"
   Entonces veo un formulario con los siguientes campos:
   - Nombre y Apellido
   - Email (será el usuario)
   - Contraseña
   - Confirmar Contraseña
   - DNI

2. Dado que estoy en el formulario de registro
   Cuando ingreso datos inválidos
   Entonces veo mensajes de error específicos:
   - Email debe tener formato válido
   - Contraseña debe tener al menos 8 caracteres y una mayuscula
   - Las contraseñas deben coincidir
   - DNI debe ser un número válido

3. Dado que completo el formulario correctamente
   Cuando presiono "Crear Cuenta"
   Entonces:
   - Se crea mi cuenta
   - Recibo un mensaje de éxito
   - Soy redirigido a la página de login

4. Dado que intento registrarme
   Cuando el email o DNI ya existe
   Entonces veo un mensaje de error indicando que el usuario ya existe

### Explicación Simple de la Implementación 🎓

Imagina que estamos creando un formulario de registro en la municipalidad:

#### 1. El Formulario (Frontend) 📝
- `RegisterForm.jsx`: Es como el formulario en papel que llenas en la municipalidad
- `InputField.jsx`: Son los campos individuales del formulario
- `ValidationMessage.jsx`: Son las notificaciones cuando algo está mal escrito

#### 2. El Proceso (Backend) 🔄
Es como cuando el empleado municipal:
1. Verifica que el formulario esté completo
2. Revisa que no exista otro formulario con el mismo DNI
3. Guarda tus datos en el archivo correspondiente
4. Te da un comprobante de registro

#### 3. La Base de Datos 📚
Como el archivo donde guardan todos los formularios:
- Tabla `users`: Archiva los datos de cada persona
- Se guarda la contraseña de forma segura (como en clave)

### Detalles Técnicos
#### Frontend
- Componentes:
  - `RegisterPage.jsx`: Página de registro
  - `RegisterForm.jsx`: Formulario de registro
  - `InputField.jsx`: Campo de entrada reutilizable
  - `ValidationMessage.jsx`: Mensajes de error/éxito

- Validaciones:
  - Email con regex
  - Contraseña: mínimo 8 caracteres, 1 mayúscula, 1 número
  - DNI: solo números, longitud válida

#### Backend
- Endpoints:
  - `POST /api/auth/register`: Crear nuevo usuario (asigna automáticamente rol de consulta)
  - `GET /api/auth/check-email`: Verificar email disponible
  - `GET /api/auth/check-dni`: Verificar DNI disponible

Nota: La gestión de roles se manejará en una historia de usuario separada, exclusiva para administradores.

#### Base de Datos
- Tabla `users`:
  - id: SERIAL PRIMARY KEY
  - email: VARCHAR(100) UNIQUE
  - password_hash: VARCHAR(255)
  - nombre: VARCHAR(100)
  - apellido: VARCHAR(100)
  - dni: VARCHAR(20) UNIQUE
  - role_id: INTEGER REFERENCES roles(id) DEFAULT 3  -- Por defecto: Usuario de Consulta
  - activo: BOOLEAN DEFAULT true
  - fecha_creacion: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  - ultimo_acceso: TIMESTAMP NULL

- Tabla `roles`:
  - id: SERIAL PRIMARY KEY
  - nombre: VARCHAR(50)
  - descripcion: VARCHAR(255)

Roles del sistema:
1. Administrador: Control total del sistema (asignado manualmente)
2. Gestor de Documentos: Gestión de documentos (asignado por administrador)
3. Usuario de Consulta: Solo lectura (rol por defecto al registrarse)

#### Seguridad
- Hash de contraseña con bcrypt
- Validación de datos en frontend y backend
- Sanitización de inputs
- Rate limiting para prevenir spam