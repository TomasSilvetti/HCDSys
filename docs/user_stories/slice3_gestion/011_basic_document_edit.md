# HU011: Edición Básica de Documentos

Como gestor de documentos
Quiero poder editar los documentos que he cargado
Para mantener la información actualizada

## Descripción
El sistema debe permitir a los gestores de documentos editar la información básica de los documentos que han cargado, manteniendo un registro de los cambios realizados.

## Criterios de Aceptación

1. Dado que soy un gestor de documentos
   Cuando accedo a editar un documento que he cargado
   Entonces puedo modificar:
   - Título del documento
   - Descripción
   - Número de expediente
   - Tipo de documento

2. Dado que estoy editando un documento
   Cuando intento guardar cambios
   Entonces:
   - Se valida que el nuevo título no exista para otro documento
   - Se actualiza la fecha de modificación
   - Se registra la acción en el historial de acceso

3. Dado que intento editar un documento
   Cuando mi rol no tiene permisos de edición
   Entonces:
   - Se me muestra un mensaje indicando que no tengo permisos suficientes
   - No se me permite acceder al formulario de edición
   - Se registra el intento de acceso no autorizado en el historial

4. Dado que estoy editando un documento
   Cuando realizo cambios en el formulario
   Entonces:
   - Se muestran los campos obligatorios claramente marcados
   - Se validan los datos ingresados en tiempo real
   - Se muestra un botón para cancelar los cambios

5. Dado que cancelo la edición
   Cuando hay cambios sin guardar
   Entonces:
   - Se me muestra una advertencia
   - Se me da la opción de descartar o continuar editando

## Notas Técnicas
- Utilizar los campos de la tabla Documento del modelo de datos
- Implementar validaciones en frontend y backend
- Registrar en HistorialAcceso cada modificación realizada
- Verificar permisos del rol del usuario antes de permitir ediciones
- Integrar con el sistema de roles y permisos para validar accesos
- Mantener consistencia en la base de datos durante las actualizaciones
- Implementar validaciones de permisos tanto en frontend (UI) como en backend (API)

## Criterios de Calidad
- Las validaciones deben ser claras y mostrar mensajes de error específicos
- La interfaz debe ser intuitiva y responsive
- El tiempo de respuesta para guardar cambios no debe superar 1 segundo
- Se debe mantener la integridad referencial en la base de datos