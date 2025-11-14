# Costos de Servidor - HCDSys en Railway.app

**Fecha de análisis:** Octubre 2025
**Proveedor seleccionado:** Railway.app
**Tipo de facturación:** Mensual (no disponible pago anual)

---

## Resumen Ejecutivo

Servidores Railway.app para la Consejo deliberante de Lules, Tucumán, Argentina

**Costo mensual estimado:** USD $45-50
**Costo anual estimado:** USD $540-600

---

## Desglose de Costos Mensuales

| Servicio | Especificaciones | Costo Mensual (USD) |
|----------|------------------|---------------------|
| **Backend (FastAPI)** | 2GB RAM, 2 vCPUs | $10 |
| **PostgreSQL Managed** | 1GB RAM, 10GB storage | $5 |
| **Almacenamiento Documentos** | 30GB (incluye crecimiento inicial) | $3 |
| **Ancho de Banda** | ~100GB/mes | $2 |
| **Plan Base (Hobby)** | Incluye $5 de uso | $5 |
| **Mantenimiento** | mantenimiento de servidor, backups | $25 |
| **TOTAL MENSUAL** | | **$45-50** |

 
---

## Proyección de Costos a Futuro

### Año 1 (2025-2026)
- **Documentos iniciales:** 3,000-4,000 documentos (~8GB)
- **Crecimiento mensual:** 200-400 documentos (~0.6GB/mes)
- **Costo estimado:** USD $540-600/año

### Año 2 (2026-2027)
- **Documentos acumulados:** ~8,000 documentos (~18GB)
- **Almacenamiento adicional:** +10GB
- **Costo estimado:** USD $600-660/año

### Año 3 (2027-2028)
- **Documentos acumulados:** ~12,000 documentos (~28GB)
- **Posible upgrade de recursos:** +1GB RAM para PostgreSQL
- **Costo estimado:** USD $660-720/año

---

### Importante sobre Facturación
- Railway **NO ofrece planes anuales prepagos**
- La facturación es **siempre mensual**

---

## Requisitos del Proyecto

### Usuarios
- **Simultáneos:** ~30 usuarios máximo
- **Totales:** 100-200 usuarios
- **Ubicación:** Lules, Tucumán, Argentina

### Documentos
- **Iniciales:** 3,000-4,000 documentos físicos a digitalizar
- **Crecimiento:** 200-400 documentos/mes
- **Tamaño promedio:** ~2MB por documento (PDFs de actas/documentos gubernamentales)

### Disponibilidad
- **Uptime requerido:** 99% (24/7)
- **Latencia:** Baja (usuarios en Argentina)
- **Backups:** Críticos (datos municipales)

### Backups
- **Snapshots diarios** de PostgreSQL
- **Retención de 7 días** (Hobby plan)

## Notas Importantes

### consideracion para aumentar recursos en caso de necesitarlo - Upgrade a Pro Plan
- Si superan **50 usuarios simultáneos**
- Si necesitan **más de 5GB RAM** por servicio
- Si requieren **backups con más retención** (30 días)

**Costo Pro Plan:** $20 USD/mes base + uso de recursos


