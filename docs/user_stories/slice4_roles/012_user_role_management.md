# HU012: Gestión de Roles de Usuario

Como administrador del sistema
Quiero poder asignar y modificar roles a los usuarios
Para controlar los niveles de acceso al sistema

## Descripción
El sistema debe proporcionar una interfaz donde los administradores puedan gestionar los roles de los usuarios registrados, permitiendo visualizar y modificar sus niveles de acceso de manera eficiente y segura.

## Criterios de Aceptación

1. Dado que soy administrador
   Cuando accedo a la sección de gestión de usuarios
   Entonces:
   - Veo una lista de todos los usuarios registrados
   - Cada entrada muestra: nombre, email, rol actual y estado (activo/inactivo)
   - La lista está ordenada alfabéticamente por nombre
   - Puedo buscar usuarios por nombre o email

2. Dado que estoy en la lista de usuarios
   Cuando selecciono un usuario
   Entonces puedo ver:
   - Detalles completos del usuario
   - Su rol actual
   - Historial de cambios de rol
   - Fecha del último acceso

3. Dado que estoy editando un usuario
   Cuando cambio su rol
   Entonces:
   - El sistema registra el cambio inmediatamente
   - Se actualiza el campo role_id en la tabla Usuario
   - Se registra en el historial quién hizo el cambio y cuándo
   - Se muestra un mensaje de confirmación

4. Dado que estoy en la gestión de usuarios
   Cuando intento modificar roles
   Entonces solo puedo asignar los roles predefinidos:
   - Administrador
   - Gestor de Documentos
   - Usuario de Consulta

5. Dado que soy administrador
   Cuando intento modificar mi propio rol
   Entonces:
   - El sistema me impide hacerlo
   - Muestra un mensaje explicando que no puedo cambiar mi propio rol
   - Mantiene mi rol actual

## Notas Técnicas
- Utilizar las tablas Usuario y Rol del modelo de datos
- Implementar caché para la lista de roles disponibles
- Mantener un registro de cambios en el historial
- Verificar que siempre exista al menos un administrador en el sistema
- Implementar validaciones para prevenir la degradación accidental de todos los administradores

## Detalles de Implementación
### Backend
```typescript
interface UserRole {
  userId: number;
  currentRole: string;
  newRole: string;
  changedBy: number;
  changeDate: Date;
}

interface RoleChangeResponse {
  success: boolean;
  message: string;
  newRole?: string;
  error?: string;
}
```

### Frontend
- Implementar tabla de usuarios con ordenamiento y filtrado
- Mostrar confirmación antes de cambios de rol
- Deshabilitar opciones no permitidas según contexto
- Actualizar UI inmediatamente tras cambios exitosos

## Criterios de Calidad
- La interfaz debe ser intuitiva y responsive
- Los cambios de rol deben ser inmediatos (< 1 segundo)
- Los mensajes de error deben ser claros y específicos
- El sistema debe mantener consistencia en los datos
- La lista de usuarios debe cargar de forma eficiente incluso con grandes volúmenes de datos