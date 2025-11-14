# ⚡ Quick Start - Deployment en 10 Minutos

Esta guía te permite deployar HCDSys en **menos de 10 minutos** usando el plan gratuito.

---

## 🎯 Lo que vas a hacer

1. ✅ Deploy automático del backend + base de datos en Render (5 min)
2. ✅ Deploy del frontend en Vercel (3 min)
3. ✅ Configurar CORS (1 min)
4. ✅ Verificar que todo funciona (1 min)

**Costo total: $0** 💰

---

## 📋 Requisitos Previos

- [ ] Cuenta en GitHub (con tu código subido)
- [ ] Cuenta en Render (gratis): https://render.com
- [ ] Cuenta en Vercel (gratis): https://vercel.com

---

## 🚀 Paso 1: Deploy en Render (5 minutos)

### 1.1 Accede a Render
```
https://dashboard.render.com
```

### 1.2 Nuevo Blueprint
1. Click en **"New"** → **"Blueprint"**
2. Conecta tu repositorio de GitHub
3. Selecciona el repositorio **HCDSys**
4. Click en **"Apply"**

### 1.3 Espera el Deploy
- ⏱️ Base de datos: ~2 minutos
- ⏱️ Backend: ~5 minutos

### 1.4 Obtén la URL del Backend
```
https://hcdsys-backend.onrender.com
```

📝 **Copia esta URL, la necesitarás para el frontend**

---

## 🌐 Paso 2: Deploy en Vercel (3 minutos)

### 2.1 Accede a Vercel
```
https://vercel.com
```

### 2.2 Importar Proyecto
1. Click en **"Add New..."** → **"Project"**
2. Importa tu repositorio de GitHub
3. Selecciona **HCDSys**

### 2.3 Configuración
```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

### 2.4 Variable de Entorno
Agrega esta variable:
```
VITE_API_URL = https://hcdsys-backend.onrender.com
```
*(Usa la URL que copiaste en el paso 1.4)*

### 2.5 Deploy
1. Click en **"Deploy"**
2. Espera ~2 minutos

### 2.6 Obtén tu URL
```
https://hcdsys-XXXXXX.vercel.app
```

📝 **Copia esta URL, la necesitarás para CORS**

---

## 🔧 Paso 3: Configurar CORS (1 minuto)

### 3.1 Vuelve a Render
```
https://dashboard.render.com
```

### 3.2 Edita Variable de Entorno
1. Click en **hcdsys-backend**
2. Ve a **Settings** → **Environment**
3. Busca **CORS_ORIGINS**
4. Edita el valor:
   ```
   https://hcdsys-XXXXXX.vercel.app
   ```
   *(Usa la URL que copiaste en el paso 2.6)*
5. Click en **"Save Changes"**

⏱️ El servicio se reiniciará automáticamente (~1 minuto)

---

## ✅ Paso 4: Verificar (1 minuto)

### 4.1 Verificar Backend
Abre PowerShell y ejecuta:

```powershell
Invoke-WebRequest -Uri "https://hcdsys-backend.onrender.com/api/health"
```

✅ Deberías ver: `StatusCode: 200`

### 4.2 Verificar Frontend
Abre tu navegador en:
```
https://hcdsys-XXXXXX.vercel.app
```

✅ Deberías ver la página de login

### 4.3 Script de Verificación Completo
```powershell
.\scripts\verify-deployment.ps1 -BackendUrl "https://hcdsys-backend.onrender.com" -FrontendUrl "https://hcdsys-XXXXXX.vercel.app"
```

---

## 🎉 ¡Listo!

Tu aplicación está deployada y funcionando en:

- **Frontend**: https://hcdsys-XXXXXX.vercel.app
- **Backend**: https://hcdsys-backend.onrender.com
- **Base de Datos**: PostgreSQL en Render

---

## ⚠️ Limitaciones Actuales

Esta es una configuración de **DEMO/PRUEBA**:

| Característica | Estado |
|----------------|--------|
| ✅ Login/Auth | Funcional |
| ✅ Gestión de Usuarios | Funcional |
| ✅ Base de Datos | Persistente |
| ⚠️ Documentos | **TEMPORAL** (se pierden al reiniciar) |
| ⏸️ Suspensión | Tras 15 min de inactividad |

### ¿Por qué los documentos son temporales?

El plan gratuito de Render **no incluye almacenamiento persistente**. Los archivos se guardan en `/tmp/documents` y se pierden cuando el servicio se reinicia.

---

## 🚀 Próximos Pasos

### Para Producción (Cuando entregues al cliente)

**Costo: $7/mes** para almacenamiento persistente

1. **Upgrade a Plan Starter**:
   ```
   Render Dashboard → hcdsys-backend → Settings → Plan → Starter
   ```

2. **Agregar Disco Persistente**:
   ```
   Settings → Disks → Add Disk
   Name: hcdsys-storage
   Mount Path: /app/storage
   Size: 1 GB
   ```

3. **Actualizar Variable**:
   ```
   DOCUMENT_STORAGE_PATH=/app/storage/documents
   ```

4. **Redeploy**

📖 **Guía completa**: Ver `DEPLOYMENT.md`

---

## 🆘 Problemas Comunes

### "Service Unavailable" (503)
**Causa**: Cold start (plan gratuito)
**Solución**: Espera 30 segundos e intenta de nuevo

### CORS Error en el Frontend
**Causa**: URL de Vercel no configurada
**Solución**: Revisa el Paso 3

### "Database connection failed"
**Causa**: La BD está iniciándose
**Solución**: Espera 2-3 minutos

### Documento no encontrado después de reinicio
**Causa**: Almacenamiento temporal (esperado)
**Solución**: Upgrade a plan Starter o usa S3

---

## 📞 Más Información

- 📖 **Guía Completa**: `DEPLOYMENT.md`
- 📚 **Guía Detallada**: `docs/deployment/render-vercel-guide.md`
- 🔧 **Script de Verificación**: `scripts/verify-deployment.ps1`

---

**¡Felicidades! Tu aplicación está en producción** 🎉

