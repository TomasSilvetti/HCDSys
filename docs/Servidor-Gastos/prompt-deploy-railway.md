# Prompt para Configurar Deploy en Railway.app

**Usa este prompt cuando estés listo para hacer el deploy del proyecto HCDSys a Railway**

---

## 📋 Prompt para Claude Code

```
Claude, necesito tu ayuda para configurar el deploy de HCDSys a Railway.app.

Información del proyecto:
- Backend: FastAPI (Python) con Docker
- Frontend: React + Vite
- Base de datos: PostgreSQL
- Arquitectura: Docker Compose con nginx
- Repositorio: GitHub (actual)

Tareas que necesito:

1. **Preparar el proyecto para Railway:**
   - Revisar y optimizar docker-compose.yml para Railway
   - Crear railway.json si es necesario
   - Configurar variables de entorno para producción
   - Ajustar configuraciones de build

2. **Configurar CI/CD:**
   - Configurar deploy automático desde GitHub
   - Crear workflows para testing antes del deploy 
   - Configurar preview deployments para PRs

3. **Guía paso a paso:**
   - Dame instrucciones detalladas para crear la cuenta en Railway
   - Cómo conectar el repositorio de GitHub
   - Qué variables de entorno configurar
   - Cómo configurar la base de datos PostgreSQL
   - Cómo hacer el primer deploy

4. **Post-deploy:**
   - Cómo configurar un dominio personalizado
   - Cómo verificar que todo funciona correctamente
   - Cómo acceder a los logs
   - Cómo monitorear el uso de recursos
   - Como configurar los test para CI/CD

5. **Backups:**
   - Cómo configurar backups automáticos adicionales
   - En caso de necesitar usar un backup como hago para restaurar la base de datos y los archivos de documentos

Prioriza la simplicidad y facilidad de mantenimiento.
El objetivo es un deploy confiable con mínimo mantenimiento manual.
```

---

## 🔧 Información Adicional que Puede Necesitar Claude

### Estructura del Proyecto
```
HCDSys/
├── backend/          # FastAPI application
├── frontend/         # React + Vite
├── nginx.conf        # Nginx configuration
├── docker-compose.yml
└── .env              # Variables de entorno locales
```

### Variables de Entorno Actuales (revisar antes del deploy)
Estas están en el archivo `.env` y deben configurarse en Railway:

**Backend:**
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `SECRET_KEY` (para JWT)
- `API_PORT`, `API_HOST`
- `CORS_ORIGINS`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `DOCUMENT_STORAGE_PATH`
- `LOG_LEVEL`, `LOG_FILE`
- `RATE_LIMIT_ENABLED`, `RATE_LIMIT_PER_MINUTE`

**Frontend:**
- `VITE_API_URL` (URL del backend)

### Servicios a Deployar
1. **PostgreSQL** - Base de datos managed de Railway
2. **Backend** - FastAPI app (container Docker)
3. **Frontend** - React SPA (static files o container)
4. **Nginx** - Proxy reverso (puede no ser necesario en Railway)

---

## ✅ Checklist Pre-Deploy

Antes de ejecutar el prompt, asegúrate de:

- [ ] Código commiteado y pusheado a GitHub
- [ ] Tests pasando correctamente
- [ ] Variables de entorno documentadas
- [ ] Archivos sensibles en .gitignore
- [ ] README.md actualizado con instrucciones
- [ ] Datos de prueba listos para carga inicial

---

## 🚀 Proceso Esperado

1. **Claude analizará el proyecto** y sugerirá optimizaciones
2. **Creará/modificará archivos** necesarios para Railway
3. **Generará documentación** paso a paso para el deploy
4. **Configurará CI/CD** básico con GitHub Actions (si es necesario)
5. **Proporcionará scripts** de backup y mantenimiento

---

## 🔍 Verificación Post-Deploy

Después del deploy, usar este checklist:

### Funcionalidad
- [ ] Frontend carga correctamente
- [ ] Backend responde en /docs (FastAPI Swagger)
- [ ] Login funciona correctamente
- [ ] Carga de documentos funciona
- [ ] Búsqueda funciona
- [ ] Descargas de documentos funcionan

### Seguridad
- [ ] HTTPS activo y funcionando
- [ ] CORS configurado correctamente
- [ ] Rate limiting activo
- [ ] Variables de entorno seguras (no en el código)
- [ ] Tokens JWT funcionando

### Performance
- [ ] Tiempos de respuesta < 2 segundos
- [ ] Carga de archivos funciona para PDFs de ~5MB
- [ ] Base de datos responde rápidamente

### Monitoreo
- [ ] Logs accesibles en Railway dashboard
- [ ] Métricas de uso visibles
- [ ] Alertas configuradas (opcional pero recomendado)

---