# Historia de Usuario: Login de Usuario 🔴

## HU003: Login de Usuario
Como usuario registrado
Quiero poder iniciar sesión en el sistema
Para acceder a las funcionalidades según mi rol

### Criterios de Aceptación
1. Dado que soy un usuario registrado
   Cuando visito la página de login
   Entonces veo un formulario con:
   - Campo para email
   - Campo para contraseña
   - Botón "Iniciar Sesión"
   - Enlace "¿Olvidaste tu contraseña?"
   - Enlace "Registrarse"

2. Dado que ingreso credenciales válidas
   Cuando presiono "Iniciar Sesión"
   Entonces:
   - Soy autenticado en el sistema
   - Soy redirigido a la página principal
   - Veo mi nombre en la barra de navegación
   - Se actualiza mi último acceso en la base de datos

3. Dado que ingreso credenciales inválidas
   Cuando presiono "Iniciar Sesión"
   Entonces:
   - Veo un mensaje de error
   - Los campos se mantienen (excepto la contraseña)
   - No soy redirigido

4. Dado que mi cuenta está desactivada
   Cuando intento iniciar sesión
   Entonces veo un mensaje indicando que contacte al administrador

### Explicación Simple de la Implementación 🎓

Imagina que es como entrar a un edificio seguro:

#### 1. El Formulario (Frontend) 📝
- `LoginPage.jsx`: Es como la puerta principal
- `LoginForm.jsx`: Es como el mostrador de seguridad donde te identificas
- `ValidationMessage.jsx`: Es como los carteles que te indican si puedes pasar

#### 2. El Proceso (Backend) 🔄
Es como cuando el guardia de seguridad:
1. Mira tu identificación (email)
2. Verifica que la clave sea correcta
3. Revisa que tengas permiso para entrar (cuenta activa)
4. Anota en su registro que entraste (último acceso)
5. Te da una credencial (token JWT) para que puedas moverte por el edificio

#### 3. La Base de Datos 📚
Como el registro del guardia donde:
- Verifica tus datos en la tabla de usuarios
- Actualiza la hora de tu último acceso
- Consulta qué permisos tienes (rol)

### Detalles Técnicos
#### Frontend
- Componentes:
  - `LoginPage.jsx`: Página de login
  - `LoginForm.jsx`: Formulario de inicio de sesión
  - `ValidationMessage.jsx`: Mensajes de error/éxito

- Validaciones:
  - Email con formato válido
  - Contraseña no vacía

#### Backend
- Endpoints:
  - `POST /api/auth/login`: Iniciar sesión
    - Request:
      ```json
      {
        "email": "string",
        "password": "string"
      }
      ```
    - Response:
      ```json
      {
        "token": "string",
        "user": {
          "id": "number",
          "nombre": "string",
          "apellido": "string",
          "email": "string",
          "rol": "string"
        }
      }
      ```

#### Base de Datos
- Consultas principales:
  ```sql
  -- Verificar credenciales y estado de cuenta
  SELECT id, email, password_hash, nombre, apellido, activo, role_id 
  FROM users 
  WHERE email = $1;

  -- Actualizar último acceso
  UPDATE users 
  SET ultimo_acceso = CURRENT_TIMESTAMP 
  WHERE id = $1;
  ```

#### Seguridad
- Autenticación con JWT
- Tokens con expiración
- Protección contra ataques de fuerza bruta (rate limiting)
- HTTPS obligatorio
- Sanitización de inputs
- No almacenar tokens en localStorage (usar httpOnly cookies)