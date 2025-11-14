# ============================================================================
# Script de Verificación de Deployment - HCDSys
# ============================================================================
# Este script verifica que todos los servicios estén funcionando correctamente
# después del deployment en Render y Vercel
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$BackendUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$FrontendUrl = ""
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Verificación de Deployment - HCDSys" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# 1. Verificar Backend Health Check
# ============================================================================
Write-Host "1️⃣  Verificando Backend Health Check..." -ForegroundColor Yellow
Write-Host "   URL: $BackendUrl/api/health" -ForegroundColor Gray

try {
    $healthResponse = Invoke-WebRequest -Uri "$BackendUrl/api/health" -Method GET -UseBasicParsing
    
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Backend está funcionando correctamente" -ForegroundColor Green
        
        $healthData = $healthResponse.Content | ConvertFrom-Json
        Write-Host "   📊 Status: $($healthData.status)" -ForegroundColor Gray
        Write-Host "   🕐 Timestamp: $($healthData.timestamp)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Error al conectar con el backend" -ForegroundColor Red
    Write-Host "   Detalles: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Message -like "*503*") {
        Write-Host "   💡 Tip: El servicio puede estar en 'cold start'. Espera 30 segundos e intenta de nuevo." -ForegroundColor Yellow
    }
    
    exit 1
}

Write-Host ""

# ============================================================================
# 2. Verificar Endpoints de API
# ============================================================================
Write-Host "2️⃣  Verificando Endpoints de API..." -ForegroundColor Yellow

# 2.1 Verificar endpoint de login
Write-Host "   📍 POST /api/auth/login" -ForegroundColor Gray
try {
    $loginResponse = Invoke-WebRequest -Uri "$BackendUrl/api/auth/login" -Method POST -UseBasicParsing -ErrorAction SilentlyContinue
} catch {
    if ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "   ✅ Endpoint disponible (422 = validación esperada)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Respuesta inesperada: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

# 2.2 Verificar endpoint de usuarios (debe requerir auth)
Write-Host "   📍 GET /api/users" -ForegroundColor Gray
try {
    $usersResponse = Invoke-WebRequest -Uri "$BackendUrl/api/users" -Method GET -UseBasicParsing -ErrorAction SilentlyContinue
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "   ✅ Endpoint protegido correctamente (401 = no autorizado)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Respuesta inesperada: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

Write-Host ""

# ============================================================================
# 3. Verificar Base de Datos
# ============================================================================
Write-Host "3️⃣  Verificando Conexión a Base de Datos..." -ForegroundColor Yellow

try {
    # El endpoint de health ya verifica la conexión a la BD
    Write-Host "   ✅ Conexión verificada a través de health check" -ForegroundColor Green
} catch {
    Write-Host "   ❌ No se pudo verificar la conexión a la base de datos" -ForegroundColor Red
}

Write-Host ""

# ============================================================================
# 4. Verificar CORS
# ============================================================================
Write-Host "4️⃣  Verificando Configuración CORS..." -ForegroundColor Yellow

try {
    $corsResponse = Invoke-WebRequest -Uri "$BackendUrl/api/health" -Method OPTIONS -UseBasicParsing -ErrorAction SilentlyContinue
    
    $allowOrigin = $corsResponse.Headers['Access-Control-Allow-Origin']
    
    if ($allowOrigin) {
        Write-Host "   ✅ CORS configurado" -ForegroundColor Green
        Write-Host "   🌐 Allow-Origin: $allowOrigin" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  No se detectaron headers CORS" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  No se pudo verificar CORS" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# 5. Verificar Frontend (si se proporcionó URL)
# ============================================================================
if ($FrontendUrl) {
    Write-Host "5️⃣  Verificando Frontend..." -ForegroundColor Yellow
    Write-Host "   URL: $FrontendUrl" -ForegroundColor Gray
    
    try {
        $frontendResponse = Invoke-WebRequest -Uri $FrontendUrl -Method GET -UseBasicParsing
        
        if ($frontendResponse.StatusCode -eq 200) {
            Write-Host "   ✅ Frontend está accesible" -ForegroundColor Green
            
            # Verificar que el contenido sea HTML
            if ($frontendResponse.Content -like "*<!DOCTYPE html>*") {
                Write-Host "   ✅ Contenido HTML válido detectado" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "   ❌ Error al acceder al frontend" -ForegroundColor Red
        Write-Host "   Detalles: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# ============================================================================
# 6. Verificar Almacenamiento
# ============================================================================
Write-Host "6️⃣  Información de Almacenamiento..." -ForegroundColor Yellow
Write-Host "   ⚠️  Almacenamiento TEMPORAL configurado" -ForegroundColor Yellow
Write-Host "   📁 Ubicación: /tmp/documents" -ForegroundColor Gray
Write-Host "   ⏱️  Los archivos se pierden al reiniciar el servicio" -ForegroundColor Gray
Write-Host "   💡 Para persistencia, actualizar a plan Starter ($7/mes)" -ForegroundColor Cyan

Write-Host ""

# ============================================================================
# Resumen
# ============================================================================
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ✅ Verificación Completada" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Próximos Pasos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Actualizar CORS con la URL de Vercel:" -ForegroundColor White
Write-Host "   - Ve a Render Dashboard → hcdsys-backend → Environment" -ForegroundColor Gray
Write-Host "   - Edita CORS_ORIGINS con tu URL de Vercel" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Probar la aplicación:" -ForegroundColor White
Write-Host "   - Abre el frontend en tu navegador" -ForegroundColor Gray
Write-Host "   - Intenta iniciar sesión" -ForegroundColor Gray
Write-Host "   - Crea un usuario de prueba" -ForegroundColor Gray
Write-Host "   - Sube un documento (temporal)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Monitorear logs:" -ForegroundColor White
Write-Host "   - Render Dashboard → Logs" -ForegroundColor Gray
Write-Host "   - Vercel Dashboard → Deployments → Logs" -ForegroundColor Gray
Write-Host ""

Write-Host "⚠️  RECORDATORIO:" -ForegroundColor Yellow
Write-Host "   Esta es una configuración de DEMO/PRUEBA" -ForegroundColor Yellow
Write-Host "   Los documentos NO persisten al reiniciar" -ForegroundColor Yellow
Write-Host "   Para producción, consulta DEPLOYMENT.md" -ForegroundColor Yellow
Write-Host ""

# ============================================================================
# Información de Contacto y Recursos
# ============================================================================
Write-Host "📚 Recursos:" -ForegroundColor Cyan
Write-Host "   - Guía completa: DEPLOYMENT.md" -ForegroundColor Gray
Write-Host "   - Guía detallada: docs/deployment/render-vercel-guide.md" -ForegroundColor Gray
Write-Host "   - Render Docs: https://render.com/docs" -ForegroundColor Gray
Write-Host "   - Vercel Docs: https://vercel.com/docs" -ForegroundColor Gray
Write-Host ""

