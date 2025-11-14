# Guía de Deploy: Render.com + Vercel

Esta guía te llevará paso a paso para desplegar HCDSys con el backend en Render.com y el frontend en Vercel.

## 📋 Requisitos Previos

- Cuenta en [Render.com](https://render.com) (gratis)
- Cuenta en [Vercel](https://vercel.com) (gratis)
- Repositorio de Git con el código de HCDSys
- Git instalado localmente

## 🎯 Arquitectura del Deploy

```
┌─────────────────┐
│   Vercel        │
│   (Frontend)    │
│   React + Vite  │
└────────┬────────┘
         │ HTTPS
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│   Render.com    │◄────►│  PostgreSQL  │
│   (Backend)     │      │  (Render DB) │
│   FastAPI       │      └──────────────┘
└─────────────────┘
```

## 🚀 Parte 1: Deploy del Backend en Render.com

### Paso 1: Crear Base de Datos PostgreSQL

1. Ve a [Render Dashboard](https://dashboard.render.com/)
2. Haz clic en **"New +"** → **"PostgreSQL"**
3. Configura la base de datos:
   - **Name**: `hcdsys-db`
   - **Database**: `hcdsys_prod`
   - **User**: `hcdsys_user`
   - **Region**: Selecciona la más cercana a tus usuarios
   - **PostgreSQL Version**: 16 (o la más reciente)
   - **Plan**: Free
4. Haz clic en **"Create Database"**
5. **⚠️ IMPORTANTE**: Guarda la **Internal Database URL** (la necesitarás después)

> **Nota sobre el Plan Gratuito**: El plan gratuito de PostgreSQL en Render expira después de 90 días. Para producción real, considera un plan de pago.

### Paso 2: Preparar el Repositorio

Asegúrate de que tu repositorio tenga todos los archivos necesarios:

```bash
# Verifica que existan estos archivos
git status

# Deberías ver:
# - backend/start.sh
# - backend/Dockerfile
# - render.yaml
# - vercel.json
```

Si falta alguno, asegúrate de hacer commit:

```bash
git add .
git commit -m "feat: Configuración de deploy para Render y Vercel"
git push origin main
```

### Paso 3: Crear Web Service en Render

1. En Render Dashboard, haz clic en **"New +"** → **"Blueprint"**
2. Conecta tu repositorio de GitHub/GitLab
3. Render detectará automáticamente el archivo `render.yaml`
4. Revisa la configuración:
   - **Service Name**: `hcdsys-backend`
   - **Environment**: Docker
   - **Region**: La misma que la base de datos
   - **Branch**: `main` (o tu rama principal)
5. **Configura las Variables de Entorno**:
   - La mayoría ya están en `render.yaml`
   - **IMPORTANTE**: Actualiza `CORS_ORIGINS` (ver Paso 5)
6. Haz clic en **"Apply"**

Render comenzará a:
1. Construir la imagen Docker
2. Ejecutar el script `start.sh`
3. Conectarse a PostgreSQL
4. Ejecutar migraciones de Alembic
5. Inicializar roles y permisos
6. Crear usuario admin
7. Iniciar Gunicorn

### Paso 4: Verificar el Deploy del Backend

1. Espera a que el deploy termine (puede tomar 5-10 minutos la primera vez)
2. Ve a la pestaña **"Logs"** para ver el progreso
3. Busca estos mensajes en los logs:
   ```
   ✅ PostgreSQL está disponible
   ✅ Migraciones ejecutadas correctamente
   ✅ Roles y permisos inicializados
   ✅ Usuario admin creado (o ya existe)
   🚀 Iniciando servidor Gunicorn...
   ```
4. Una vez completado, copia la **URL del servicio** (ej: `https://hcdsys-backend.onrender.com`)
5. Verifica que funcione:
   ```bash
   curl https://hcdsys-backend.onrender.com/api/health
   ```
   Deberías recibir: `{"status": "healthy"}`

### Paso 5: Configurar CORS (Primera Parte)

Por ahora, deja `CORS_ORIGINS` con el valor placeholder. Lo actualizaremos después de desplegar el frontend.

---

## 🎨 Parte 2: Deploy del Frontend en Vercel

### Paso 1: Preparar Variables de Entorno

1. Crea el archivo `.env.production` en el directorio `frontend/`:
   ```bash
   cd frontend
   cp .env.production.example .env.production
   ```

2. Edita `.env.production` y actualiza la URL del backend:
   ```env
   VITE_API_URL=https://hcdsys-backend.onrender.com/api
   ```
   *(Reemplaza con tu URL real de Render)*

3. **NO hagas commit de este archivo** (ya está en `.gitignore`)

### Paso 2: Deploy en Vercel

#### Opción A: Desde la Web (Recomendado)

1. Ve a [Vercel Dashboard](https://vercel.com/dashboard)
2. Haz clic en **"Add New..."** → **"Project"**
3. Importa tu repositorio de Git
4. Configura el proyecto:
   - **Framework Preset**: Vite
   - **Root Directory**: `./` (raíz del proyecto)
   - **Build Command**: `cd frontend && npm ci && npm run build`
   - **Output Directory**: `frontend/dist`
5. **Variables de Entorno**:
   - Haz clic en **"Environment Variables"**
   - Agrega:
     - **Name**: `VITE_API_URL`
     - **Value**: `https://hcdsys-backend.onrender.com/api`
     - **Environment**: Production
6. Haz clic en **"Deploy"**

#### Opción B: Desde la CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod

# Sigue las instrucciones interactivas
```

### Paso 3: Verificar el Deploy del Frontend

1. Espera a que el deploy termine (1-3 minutos)
2. Vercel te dará una URL (ej: `https://hcdsys.vercel.app`)
3. Abre la URL en tu navegador
4. **Verás errores de CORS** - esto es normal, lo arreglaremos en el siguiente paso

---

## 🔧 Parte 3: Configuración Final de CORS

Ahora que tienes ambas URLs, debes actualizar la configuración de CORS:

### Paso 1: Actualizar CORS en Render

1. Ve a tu servicio backend en Render Dashboard
2. Ve a **"Environment"** en el menú lateral
3. Encuentra la variable `CORS_ORIGINS`
4. Actualízala con tu URL de Vercel:
   ```
   https://hcdsys.vercel.app
   ```
   *(Si tienes un dominio personalizado, agrégalo también separado por comas)*
5. Haz clic en **"Save Changes"**
6. El servicio se reiniciará automáticamente (toma ~1 minuto)

### Paso 2: Verificar CORS

1. Abre tu aplicación en Vercel
2. Intenta hacer login
3. Si todo funciona correctamente, ¡el deploy está completo! 🎉

---

## 🔐 Credenciales de Acceso Inicial

El sistema crea automáticamente un usuario administrador:

- **Usuario**: `admin`
- **Contraseña**: `Admin123!`
- **Email**: `admin@hcdsys.com`

**⚠️ IMPORTANTE**: Cambia esta contraseña inmediatamente después del primer login.

---

## 📊 Monitoreo y Logs

### Ver Logs del Backend (Render)

1. Ve a tu servicio en Render Dashboard
2. Haz clic en **"Logs"** en el menú lateral
3. Aquí verás todos los logs en tiempo real

### Ver Logs del Frontend (Vercel)

1. Ve a tu proyecto en Vercel Dashboard
2. Haz clic en **"Deployments"**
3. Selecciona un deployment
4. Haz clic en **"View Function Logs"**

### Métricas de Rendimiento

- **Render**: Ve a **"Metrics"** para ver uso de CPU, memoria y red
- **Vercel**: Ve a **"Analytics"** para ver métricas de frontend

---

## 🔄 Actualizaciones y Re-deploys

### Actualizar Backend

Render hace deploy automático cuando haces push a tu rama principal:

```bash
git add .
git commit -m "feat: Nueva funcionalidad"
git push origin main
```

Render detectará el cambio y hará re-deploy automáticamente.

### Actualizar Frontend

Vercel también hace deploy automático:

```bash
cd frontend
# Haz tus cambios
git add .
git commit -m "feat: Actualización de UI"
git push origin main
```

Vercel detectará el cambio y hará re-deploy automáticamente.

### Deploy Manual

Si necesitas hacer deploy manual:

**Render:**
1. Ve a tu servicio
2. Haz clic en **"Manual Deploy"** → **"Deploy latest commit"**

**Vercel:**
```bash
cd frontend
vercel --prod
```

---

## 🗄️ Gestión de Base de Datos

### Conectarse a PostgreSQL

Render proporciona varias formas de conexión:

#### Opción 1: Usar Render Shell

1. Ve a tu base de datos en Render Dashboard
2. Haz clic en **"Connect"** → **"External Connection"**
3. Copia el comando PSQL
4. Ejecútalo en tu terminal local:
   ```bash
   PGPASSWORD=<password> psql -h <host> -U <user> <database>
   ```

#### Opción 2: Usar Cliente GUI (TablePlus, DBeaver, pgAdmin)

Usa la **External Database URL** de Render:
```
postgresql://user:password@host:port/database
```

### Backups

**Plan Gratuito**: No incluye backups automáticos. Debes hacerlos manualmente:

```bash
# Backup
pg_dump -h <host> -U <user> -d <database> > backup.sql

# Restore
psql -h <host> -U <user> -d <database> < backup.sql
```

**Plan de Pago**: Incluye backups automáticos diarios.

### Migraciones de Base de Datos

Las migraciones se ejecutan automáticamente en cada deploy gracias al script `start.sh`.

Si necesitas crear una nueva migración:

```bash
# Localmente
cd backend
alembic revision --autogenerate -m "Descripción del cambio"

# Commit y push
git add .
git commit -m "feat: Nueva migración de BD"
git push origin main
```

Render ejecutará la migración automáticamente en el siguiente deploy.

---

## 🛡️ Seguridad

### Variables de Entorno Sensibles

**Render:**
- Todas las variables sensibles están en el Dashboard
- Nunca las incluyas en `render.yaml` directamente
- Usa `generateValue: true` para secrets automáticos

**Vercel:**
- Configura variables de entorno en el Dashboard
- Nunca hagas commit de `.env.production`
- Usa variables de entorno diferentes para Preview y Production

### HTTPS

Ambos servicios proporcionan HTTPS automático:
- Render: Certificado SSL gratuito
- Vercel: Certificado SSL gratuito

### Dominios Personalizados

**Render:**
1. Ve a tu servicio → **"Settings"** → **"Custom Domains"**
2. Agrega tu dominio
3. Configura los registros DNS según las instrucciones

**Vercel:**
1. Ve a tu proyecto → **"Settings"** → **"Domains"**
2. Agrega tu dominio
3. Configura los registros DNS según las instrucciones

---

## 🐛 Solución de Problemas Comunes

### Error: "Cannot connect to database"

**Síntomas**: El backend no puede conectarse a PostgreSQL

**Soluciones**:
1. Verifica que la base de datos esté activa en Render Dashboard
2. Revisa que `DATABASE_URL` esté configurada correctamente
3. Verifica los logs del backend:
   ```
   ⏳ Esperando a que PostgreSQL esté disponible...
   ```
4. Si el problema persiste después de 30 intentos, revisa la configuración de la BD

### Error: "CORS policy blocked"

**Síntomas**: El frontend no puede hacer peticiones al backend

**Soluciones**:
1. Verifica que `CORS_ORIGINS` en Render incluya tu URL de Vercel
2. Asegúrate de no tener espacios extra en la URL
3. Incluye el protocolo completo: `https://` (no `http://`)
4. Si usas un dominio personalizado, agrégalo también
5. Reinicia el servicio backend después de cambiar CORS

### Error: "Migrations failed"

**Síntomas**: El backend no inicia, logs muestran error en migraciones

**Soluciones**:
1. Verifica que todas las migraciones estén en el repositorio
2. Revisa los logs para ver el error específico de Alembic
3. Conecta a la BD y verifica la tabla `alembic_version`
4. Si es necesario, ejecuta manualmente:
   ```bash
   # Conecta a la BD via Render Shell
   psql <connection_string>
   
   # Verifica versión actual
   SELECT * FROM alembic_version;
   
   # Si necesitas resetear (⚠️ CUIDADO en producción)
   DELETE FROM alembic_version;
   ```

### Error: "Module not found" en Vercel

**Síntomas**: El build falla en Vercel

**Soluciones**:
1. Verifica que `package.json` esté en el directorio `frontend/`
2. Asegúrate de que todas las dependencias estén en `package.json`
3. Verifica el comando de build en `vercel.json`
4. Revisa los logs de build en Vercel Dashboard

### Error: "Disk quota exceeded" en Render

**Síntomas**: El servicio se detiene, logs muestran error de disco

**Soluciones**:
1. El plan gratuito tiene 1GB de disco persistente
2. Revisa el uso en Render Dashboard → **"Metrics"**
3. Limpia archivos antiguos si es necesario
4. Considera aumentar el tamaño del disco (requiere plan de pago)

### Error: "Service unavailable" después de inactividad

**Síntomas**: El backend no responde después de estar inactivo

**Explicación**: El plan gratuito de Render pone los servicios en "sleep" después de 15 minutos de inactividad.

**Soluciones**:
1. La primera petición después del sleep puede tardar 30-60 segundos
2. Implementa un "keep-alive" ping (requiere servicio externo)
3. Considera un plan de pago para evitar el sleep

### Frontend muestra página en blanco

**Síntomas**: La aplicación carga pero muestra pantalla blanca

**Soluciones**:
1. Abre las DevTools del navegador (F12)
2. Revisa la consola para errores
3. Verifica que `VITE_API_URL` esté configurada en Vercel
4. Asegúrate de que la URL del API termine en `/api`
5. Verifica que el backend esté respondiendo:
   ```bash
   curl https://tu-backend.onrender.com/api/health
   ```

---

## 📈 Optimizaciones

### Backend (Render)

1. **Aumentar workers de Gunicorn**:
   Edita `backend/gunicorn_config.py`:
   ```python
   workers = 2  # Aumenta según tu plan
   ```

2. **Habilitar caching**:
   Considera usar Redis para sesiones y cache (requiere servicio adicional)

3. **Optimizar queries**:
   Usa índices en PostgreSQL para queries frecuentes

### Frontend (Vercel)

1. **Code splitting**:
   Vite ya lo hace automáticamente

2. **Lazy loading**:
   Implementa lazy loading para rutas:
   ```javascript
   const DocumentPage = lazy(() => import('./pages/DocumentPage'));
   ```

3. **Optimizar imágenes**:
   Usa formatos modernos (WebP, AVIF)

4. **CDN**:
   Vercel ya usa CDN global automáticamente

---

## 💰 Costos

### Plan Gratuito

**Render:**
- 750 horas/mes de compute (suficiente para 1 servicio 24/7)
- PostgreSQL gratuito por 90 días
- 1GB de disco persistente
- Servicios duermen después de 15 min de inactividad

**Vercel:**
- 100GB de bandwidth/mes
- Builds ilimitados
- Dominios personalizados ilimitados
- HTTPS automático

### Plan de Pago (Recomendado para Producción)

**Render:**
- Starter: $7/mes (sin sleep, más recursos)
- PostgreSQL: $7/mes (1GB RAM, 1GB disco)

**Vercel:**
- Pro: $20/mes (más bandwidth, analytics avanzados)

---

## 🔗 Enlaces Útiles

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 📞 Soporte

Si encuentras problemas no cubiertos en esta guía:

1. Revisa los logs detalladamente
2. Consulta la documentación oficial de Render/Vercel
3. Busca en Stack Overflow
4. Abre un issue en el repositorio del proyecto

---

## ✅ Checklist de Deploy

Usa esta lista para verificar que todo esté configurado correctamente:

### Pre-Deploy
- [ ] Código commiteado y pusheado a Git
- [ ] `backend/start.sh` existe y tiene permisos de ejecución
- [ ] `backend/Dockerfile` actualizado con CMD correcto
- [ ] `render.yaml` configurado correctamente
- [ ] `vercel.json` existe en la raíz
- [ ] `frontend/.env.production.example` existe

### Deploy Backend (Render)
- [ ] Base de datos PostgreSQL creada
- [ ] Internal Database URL guardada
- [ ] Web Service creado desde Blueprint
- [ ] Variables de entorno configuradas
- [ ] Deploy completado exitosamente
- [ ] Logs muestran mensajes de éxito (✅)
- [ ] `/api/health` responde correctamente
- [ ] URL del backend guardada

### Deploy Frontend (Vercel)
- [ ] Proyecto creado en Vercel
- [ ] `VITE_API_URL` configurada
- [ ] Build completado exitosamente
- [ ] Sitio accesible en la URL de Vercel
- [ ] URL del frontend guardada

### Configuración Final
- [ ] `CORS_ORIGINS` actualizada en Render con URL de Vercel
- [ ] Servicio backend reiniciado
- [ ] Login funciona correctamente
- [ ] No hay errores de CORS en la consola
- [ ] Usuario admin puede acceder
- [ ] Contraseña del admin cambiada

### Post-Deploy
- [ ] Backups de BD configurados (si es necesario)
- [ ] Dominios personalizados configurados (si aplica)
- [ ] Monitoreo configurado
- [ ] Documentación actualizada con URLs reales

---

¡Felicitaciones! 🎉 Tu aplicación HCDSys ahora está desplegada y lista para usar.

