# 💾 Respaldos y Seguridad

## Respaldos Automáticos

CHUMI incluye respaldos:
- ✅ Cada hora (local)
- ✅ Cada día (externo)
- ✅ Cloud híbrido (si habilitado)

## Restaurar Respaldo

1. Módulo → Configuración
2. [Administración] → [Respaldos]
3. Seleccionar fecha
4. [Restaurar]

## Respaldos Manuales

```bash
mysqldump -u root -p bodegadisfruleg > backup.sql
```

**Verificar respaldos regularmente**
