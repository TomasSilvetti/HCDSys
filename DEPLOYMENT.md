# 🚀 Guía de Deployment - HCDSys

## 📋 Configuración Actual

### Estado: **DEMO/PRUEBA** (Almacenamiento Temporal)

Esta configuración usa el **plan gratuito** de Render con almacenamiento temporal.

⚠️ **IMPORTANTE**: Los documentos subidos se almacenan en `/tmp/documents` y **se pierden al reiniciar el servicio**.

---

## 🏗️ Arquitectura de Deployment

```
┌─────────────────┐
│  Vercel (Free)  │  ← Frontend React
│  hcdsys.vercel  │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│ Render (Free)   │  ← Backend FastAPI
│ hcdsys-backend  │
└────────┬────────┘
         │
         ├─→ /tmp/documents (Temporal - se pierde al reiniciar)
         │
         ▼
┌─────────────────┐
│ Render (Free)   │  ← PostgreSQL Database
│ hcdsys-db       │
└─────────────────┘
```

---

## 📦 Paso 1: Deploy del Backend en Render

### Opción A: Deploy Automático con Blueprint (Recomendado)

1. **Accede a Render**: https://dashboard.render.com

2. **Nuevo Blueprint**:
   - Click en "New" → "Blueprint"
   - Conecta tu repositorio de GitHub
   - Render detectará automáticamente el archivo `render.yaml`

3. **Configuración**:
   - **Repository**: Selecciona tu repositorio HCDSys
   - **Branch**: `main` (o tu rama principal)
   - Click en "Apply"

4. **Espera el Deploy**:
   - Base de datos: ~2-3 minutos
   - Backend: ~5-10 minutos (primera vez)

5. **Obtén la URL del Backend**:
   ```
   https://hcdsys-backend.onrender.com
   ```

### Opción B: Deploy Manual

Si prefieres crear los servicios manualmente, sigue la guía en `docs/deployment/render-vercel-guide.md`.

---

## 🌐 Paso 2: Deploy del Frontend en Vercel

### 2.1 Preparar Variables de Entorno

Crea un archivo `.env.production` en la carpeta `frontend/`:

```env
VITE_API_URL=https://hcdsys-backend.onrender.com
```

### 2.2 Deploy en Vercel

1. **Accede a Vercel**: https://vercel.com

2. **Importar Proyecto**:
   - Click en "Add New..." → "Project"
   - Importa tu repositorio de GitHub

3. **Configuración del Proyecto**:
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```

4. **Variables de Entorno**:
   - Agrega: `VITE_API_URL` = `https://hcdsys-backend.onrender.com`

5. **Deploy**:
   - Click en "Deploy"
   - Espera ~2-3 minutos

6. **Obtén tu URL**:
   ```
   https://hcdsys-tu-proyecto.vercel.app
   ```

---

## 🔧 Paso 3: Actualizar CORS

Una vez que tengas la URL de Vercel, actualiza el CORS en Render:

1. Ve a tu servicio backend en Render
2. Settings → Environment
3. Edita `CORS_ORIGINS`:
   ```
   https://hcdsys-tu-proyecto.vercel.app
   ```
4. Guarda los cambios (el servicio se reiniciará automáticamente)

---

## ✅ Verificación del Deployment

### Backend Health Check
```powershell
Invoke-WebRequest -Uri "https://hcdsys-backend.onrender.com/api/health"
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Frontend
Abre tu navegador en: `https://hcdsys-tu-proyecto.vercel.app`

### Test de Integración
1. Inicia sesión en el frontend
2. Intenta crear un usuario
3. Intenta subir un documento (recuerda: se perderá al reiniciar)

---

## ⚠️ Limitaciones del Plan Gratuito

### Backend (Render Free)
- ❌ **Almacenamiento temporal**: Los archivos se pierden al reiniciar
- ⏸️ **Suspensión automática**: Tras 15 minutos de inactividad
- 🐌 **Cold start**: Primera petición tarda ~30 segundos
- 💾 **RAM**: 512 MB
- ⏱️ **Tiempo de build**: 500 horas/mes

### Base de Datos (Render Free)
- ✅ **Persistente**: Los datos NO se pierden
- 💾 **Almacenamiento**: 1 GB
- 🔄 **Expira en 90 días**: Sin actividad

### Frontend (Vercel Free)
- ✅ **Sin limitaciones significativas** para este proyecto
- 🚀 **CDN global**
- 📊 **100 GB bandwidth/mes**

---

## 🎯 Roadmap: Upgrade a Producción

### Cuándo Actualizar
- ✅ Cuando entregues al cliente
- ✅ Cuando necesites persistencia de documentos
- ✅ Cuando el servicio deba estar siempre activo

### Costo Estimado
```
Backend Render Starter: $7/mes
  ├─ Disco persistente 1GB (incluido)
  ├─ Sin suspensión automática
  ├─ 512 MB RAM
  └─ Cold start más rápido

Base de datos: $0 (puede quedarse en free)
Frontend Vercel: $0

TOTAL: $7/mes
```

### Pasos para el Upgrade

#### 1. Backup de la Base de Datos
```powershell
# En Render Dashboard:
# hcdsys-db → Connect → Copiar comando de conexión
# Ejecutar pg_dump para backup
```

#### 2. Actualizar Plan en Render
```
1. Dashboard → hcdsys-backend → Settings
2. Plan → Change to "Starter" ($7/mes)
3. Confirm
```

#### 3. Agregar Disco Persistente
```
1. Settings → Disks → Add Disk
2. Name: hcdsys-storage
3. Mount Path: /app/storage
4. Size: 1 GB (incluido en plan)
5. Save
```

#### 4. Actualizar Variables de Entorno
```
Settings → Environment → Edit:

DOCUMENT_STORAGE_PATH=/app/storage/documents
```

#### 5. Actualizar Dockerfile
Descomentar en `backend/Dockerfile`:
```dockerfile
# Cambiar de:
RUN mkdir -p /tmp/documents /app/logs

# A:
RUN mkdir -p /app/storage/documents /app/logs
```

#### 6. Redeploy
```powershell
git add .
git commit -m "feat: upgrade to persistent storage"
git push origin main
```

#### 7. Verificar
```powershell
# Subir un documento de prueba
# Reiniciar el servicio manualmente
# Verificar que el documento sigue disponible
```

---

## 🆘 Troubleshooting

### Error: "Service Unavailable"
**Causa**: Cold start (plan free)
**Solución**: Espera 30 segundos y reintenta

### Error: CORS
**Causa**: URL de Vercel no configurada en CORS_ORIGINS
**Solución**: Actualiza la variable de entorno en Render

### Error: "Database connection failed"
**Causa**: La base de datos está iniciándose
**Solución**: Espera 2-3 minutos después del deploy

### Error: "Document not found" después de reinicio
**Causa**: Almacenamiento temporal (esperado en plan free)
**Solución**: Upgrade a plan Starter o usa almacenamiento externo (S3)

### Build Failed
**Causa**: Dependencias o configuración incorrecta
**Solución**: Revisa los logs en Render Dashboard

---

## 📞 Soporte

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Guía Detallada**: `docs/deployment/render-vercel-guide.md`

---

## 📝 Checklist de Deployment

### Pre-Deploy
- [ ] Código en GitHub/GitLab
- [ ] Variables de entorno documentadas
- [ ] Tests pasando localmente
- [ ] Dockerfile funcional

### Deploy Backend
- [ ] Servicio de base de datos creado
- [ ] Backend deployado
- [ ] Health check respondiendo
- [ ] Variables de entorno configuradas

### Deploy Frontend
- [ ] Proyecto importado en Vercel
- [ ] VITE_API_URL configurada
- [ ] Build exitoso
- [ ] Aplicación accesible

### Post-Deploy
- [ ] CORS actualizado con URL de Vercel
- [ ] Login funcional
- [ ] Crear usuario funcional
- [ ] Subir documento funcional (temporal)
- [ ] Documentación actualizada

### Para Producción
- [ ] Backup de base de datos
- [ ] Plan Starter activado
- [ ] Disco persistente agregado
- [ ] Variables actualizadas
- [ ] Dockerfile actualizado
- [ ] Persistencia verificada

---

**Última actualización**: 2024-01-15
**Versión**: 1.0.0 (Demo/Temporal)

