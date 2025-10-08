# Manual de Usuario - HCDSys

## Introducción

Bienvenido al Sistema de Gestión Documental HCDSys. Este manual le guiará a través de las funcionalidades principales del sistema y le ayudará a aprovechar al máximo todas sus características.

HCDSys es una plataforma diseñada para facilitar el almacenamiento, búsqueda y gestión de documentos digitales, con especial énfasis en la organización y control de versiones.

## Acceso al Sistema

### Requisitos Técnicos

- Navegador web actualizado (recomendados: Chrome, Firefox, Edge)
- Conexión a Internet
- Resolución de pantalla mínima: 1280x720

### Inicio de Sesión

1. Abra su navegador web y acceda a la URL del sistema: `https://[dominio]`
2. En la página de inicio, haga clic en el botón "Iniciar Sesión" ubicado en la esquina superior derecha.
3. Ingrese su dirección de correo electrónico y contraseña en los campos correspondientes.
4. Haga clic en el botón "Ingresar".

![Pantalla de Inicio de Sesión](../images/login_screen.png)

### Recuperación de Contraseña

Si ha olvidado su contraseña:

1. En la pantalla de inicio de sesión, haga clic en "¿Olvidó su contraseña?".
2. Ingrese su dirección de correo electrónico registrada.
3. Haga clic en "Enviar Enlace de Recuperación".
4. Recibirá un correo electrónico con instrucciones para restablecer su contraseña.
5. Siga el enlace en el correo y establezca una nueva contraseña.

### Registro de Nuevo Usuario

Si no tiene una cuenta:

1. En la pantalla de inicio de sesión, haga clic en "Registrarse".
2. Complete el formulario con sus datos personales:
   - Correo electrónico
   - Nombre
   - Apellido
   - Contraseña (mínimo 8 caracteres)
3. Haga clic en "Crear Cuenta".
4. Se enviará un correo de verificación a su dirección de correo electrónico.
5. Haga clic en el enlace de verificación para activar su cuenta.

**Nota**: Dependiendo de la configuración del sistema, es posible que los nuevos registros requieran aprobación por parte de un administrador.

## Interfaz Principal

Una vez que haya iniciado sesión, se encontrará con la interfaz principal del sistema:

![Interfaz Principal](../images/main_interface.png)

### Elementos de la Interfaz

1. **Barra de Navegación Superior**:
   - Logo del sistema (izquierda)
   - Barra de búsqueda rápida (centro)
   - Notificaciones (derecha)
   - Menú de usuario (derecha)

2. **Menú Lateral**:
   - Inicio
   - Documentos
   - Búsqueda Avanzada
   - Administración (visible según permisos)
   - Configuración

3. **Área Principal de Contenido**:
   - Muestra el contenido seleccionado
   - Documentos recientes
   - Estadísticas y gráficos

4. **Barra de Estado**:
   - Información del sistema
   - Estado de conexión

## Gestión de Documentos

### Visualización de Documentos

La sección "Documentos" muestra una lista de los documentos disponibles:

![Lista de Documentos](../images/documents_list.png)

Cada entrada de documento muestra:
- Título del documento
- Categoría
- Fecha de creación/modificación
- Etiquetas
- Acciones disponibles

Para ver un documento:
1. Haga clic en el título del documento o en el botón "Ver".
2. Se abrirá la vista detallada del documento.

### Vista Detallada de Documento

La vista detallada muestra toda la información del documento:

![Vista Detallada de Documento](../images/document_detail.png)

Elementos de la vista detallada:
- Título y descripción
- Metadatos (categoría, etiquetas, fechas)
- Historial de versiones
- Visor de documento
- Acciones disponibles

### Búsqueda de Documentos

#### Búsqueda Rápida

1. Utilice la barra de búsqueda en la parte superior de la interfaz.
2. Escriba términos relacionados con el documento (título, contenido, etiquetas).
3. Presione Enter o haga clic en el icono de lupa.
4. Se mostrarán los resultados coincidentes.

#### Búsqueda Avanzada

Para realizar búsquedas más específicas:

1. Haga clic en "Búsqueda Avanzada" en el menú lateral.
2. Complete los criterios de búsqueda:
   - Texto a buscar
   - Categoría
   - Rango de fechas
   - Etiquetas
   - Autor
3. Haga clic en "Buscar".
4. Los resultados se mostrarán en una lista filtrada.

![Búsqueda Avanzada](../images/advanced_search.png)

### Carga de Nuevos Documentos

Para cargar un nuevo documento:

1. Haga clic en el botón "Nuevo Documento" en la sección de Documentos.
2. Complete el formulario de carga:
   - Título del documento
   - Descripción
   - Categoría (seleccione de la lista desplegable)
   - Etiquetas (separadas por comas)
3. Arrastre y suelte el archivo o haga clic en "Seleccionar Archivo" para elegir el documento a cargar.
4. Haga clic en "Cargar".
5. Espere a que se complete la carga y procesamiento del documento.

![Formulario de Carga](../images/upload_form.png)

**Formatos Soportados**:
- PDF
- Word (.docx, .doc)
- Excel (.xlsx, .xls)
- PowerPoint (.pptx, .ppt)
- Texto (.txt)
- Imágenes (.jpg, .png)

**Límite de Tamaño**: 10MB por archivo

### Edición de Documentos

Para editar la información de un documento existente:

1. Abra la vista detallada del documento.
2. Haga clic en el botón "Editar".
3. Modifique los campos necesarios:
   - Título
   - Descripción
   - Categoría
   - Etiquetas
4. Haga clic en "Guardar Cambios".

**Nota**: La edición de metadatos no crea una nueva versión del documento.

### Carga de Nuevas Versiones

Para actualizar un documento con una nueva versión:

1. Abra la vista detallada del documento.
2. Haga clic en el botón "Subir Nueva Versión".
3. Seleccione el archivo actualizado.
4. Opcionalmente, añada un comentario sobre los cambios realizados.
5. Haga clic en "Cargar Versión".

![Carga de Nueva Versión](../images/new_version.png)

### Historial de Versiones

Para ver el historial de versiones de un documento:

1. Abra la vista detallada del documento.
2. Desplácese hasta la sección "Historial de Versiones".
3. Cada versión muestra:
   - Número de versión
   - Fecha de carga
   - Usuario que realizó la carga
   - Comentario (si existe)
4. Para descargar una versión específica, haga clic en el botón "Descargar" junto a la versión deseada.
5. Para comparar versiones, seleccione dos versiones y haga clic en "Comparar".

![Historial de Versiones](../images/version_history.png)

### Eliminación de Documentos

Para eliminar un documento:

1. Abra la vista detallada del documento.
2. Haga clic en el botón "Eliminar".
3. Confirme la eliminación en el cuadro de diálogo.

**Nota**: Dependiendo de sus permisos, es posible que no pueda eliminar documentos o que la eliminación requiera aprobación.

## Administración del Sistema

**Nota**: Esta sección solo es visible para usuarios con rol de Administrador.

### Gestión de Usuarios

Para gestionar usuarios:

1. Haga clic en "Administración" en el menú lateral.
2. Seleccione "Usuarios".
3. Se mostrará la lista de usuarios registrados.

![Gestión de Usuarios](../images/user_management.png)

Desde esta interfaz puede:
- Ver detalles de usuarios
- Crear nuevos usuarios
- Editar usuarios existentes
- Activar/desactivar cuentas
- Asignar roles

#### Creación de Usuarios

1. En la sección de Usuarios, haga clic en "Nuevo Usuario".
2. Complete el formulario:
   - Correo electrónico
   - Nombre
   - Apellido
   - Rol (seleccione de la lista)
   - Contraseña inicial
3. Haga clic en "Crear Usuario".

#### Asignación de Roles

1. En la lista de usuarios, haga clic en el botón "Editar" junto al usuario deseado.
2. En el formulario de edición, seleccione el rol adecuado del menú desplegable.
3. Haga clic en "Guardar Cambios".

### Gestión de Roles y Permisos

Para gestionar roles:

1. Haga clic en "Administración" en el menú lateral.
2. Seleccione "Roles y Permisos".
3. Se mostrará la lista de roles disponibles.

![Gestión de Roles](../images/role_management.png)

#### Creación de Roles

1. En la sección de Roles, haga clic en "Nuevo Rol".
2. Complete el formulario:
   - Nombre del rol
   - Descripción
   - Seleccione los permisos aplicables
3. Haga clic en "Crear Rol".

#### Edición de Permisos

1. En la lista de roles, haga clic en el botón "Editar" junto al rol deseado.
2. Modifique los permisos seleccionando o deseleccionando las casillas correspondientes.
3. Haga clic en "Guardar Cambios".

## Configuración de Usuario

### Perfil de Usuario

Para acceder y modificar su perfil:

1. Haga clic en su nombre de usuario en la esquina superior derecha.
2. Seleccione "Mi Perfil".
3. Se mostrará su información personal.

![Perfil de Usuario](../images/user_profile.png)

Desde esta interfaz puede:
- Actualizar su información personal
- Cambiar su contraseña
- Configurar preferencias de notificación

### Cambio de Contraseña

1. En su perfil, haga clic en "Cambiar Contraseña".
2. Ingrese su contraseña actual.
3. Ingrese y confirme su nueva contraseña.
4. Haga clic en "Actualizar Contraseña".

### Preferencias de Notificación

1. En su perfil, haga clic en "Preferencias de Notificación".
2. Configure las opciones según sus necesidades:
   - Notificaciones por correo electrónico
   - Notificaciones en la plataforma
   - Tipos de eventos a notificar
3. Haga clic en "Guardar Preferencias".

## Preguntas Frecuentes

### ¿Cómo puedo recuperar una versión anterior de un documento?

Para recuperar una versión anterior:
1. Abra la vista detallada del documento.
2. Vaya a la sección "Historial de Versiones".
3. Localice la versión que desea recuperar.
4. Haga clic en "Descargar" para obtener esa versión.
5. Si desea establecer esa versión como la actual, haga clic en "Restaurar" junto a la versión deseada.

### ¿Qué hago si no puedo cargar un documento?

Verifique lo siguiente:
1. El formato del archivo es compatible.
2. El tamaño del archivo no excede el límite de 10MB.
3. Tiene permisos para cargar documentos.
4. Su conexión a Internet es estable.

Si el problema persiste, contacte al administrador del sistema.

### ¿Cómo puedo compartir un documento con alguien que no tiene acceso al sistema?

Para compartir un documento:
1. Abra la vista detallada del documento.
2. Haga clic en "Compartir".
3. Seleccione una de las opciones:
   - Generar enlace de acceso temporal
   - Enviar por correo electrónico
   - Descargar para compartir externamente
4. Siga las instrucciones según la opción seleccionada.

### ¿Puedo acceder al sistema desde dispositivos móviles?

Sí, HCDSys es compatible con dispositivos móviles. Puede acceder desde:
- Navegadores web en smartphones y tablets
- Aplicación móvil dedicada (si está disponible)

La interfaz se adapta automáticamente al tamaño de pantalla del dispositivo.

## Soporte Técnico

Si encuentra problemas o tiene preguntas adicionales:

1. Consulte la sección de Ayuda dentro del sistema.
2. Contacte al administrador del sistema.
3. Envíe un correo electrónico a soporte@tu-dominio.com.
4. Llame a la línea de soporte: +XX XXX XXXXXXX (horario de atención: Lunes a Viernes, 9:00 - 18:00).
