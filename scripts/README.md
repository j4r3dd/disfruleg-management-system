# Database Cleanup Scripts

This directory contains scripts to safely clean and reset the Disfruleg database for production deployment.

## ⚠️ WARNING

**These scripts will DELETE ALL business data including:**
- Products, Clients, Groups, Customer Types
- Invoices, Orders, Debts
- Purchase history, Pricing data
- Financial records
- System logs (optional)

**These scripts will PRESERVE:**
- Database structure (tables, views, triggers)
- User accounts
- Sequences (reset to 1)

## 📋 Prerequisites

1. **Backup your database first!**
2. Python 3.8+ installed
3. Database connection configured
4. Google Cloud credentials (if using Cloud SQL)

## 🚀 Usage

### Option 1: Python Script (Recommended)

The Python script provides an interactive experience with statistics and confirmations:

```bash
cd /mnt/c/Users/j4r3d/Programacion/di_senos
python scripts/cleanup_database.py
```

**Features:**
- ✅ Shows current database statistics
- 💰 Displays financial summary (sales, costs, profits, debts)
- 🔒 Multiple confirmation prompts
- 📝 Option to keep system logs
- ✅ Post-cleanup verification
- 📊 Detailed reporting

**Interactive Flow:**
1. Shows backup recommendations
2. Confirms backup was created
3. Displays current stats and financial summary
4. Asks for final confirmation
5. Asks if you want to keep logs
6. Executes cleanup
7. Shows post-cleanup verification

### Option 2: Direct SQL Execution

If you prefer to run the SQL directly:

```bash
# Using MySQL client
mysql -u Jared -p disfruleg < scripts/cleanup_database.sql

# Or using gcloud for Cloud SQL
gcloud sql connect bodega-disfruleg-dev --user=Jared --database=disfruleg < scripts/cleanup_database.sql
```

## 📊 What Gets Cleaned

### Transactional Tables (ALL DATA DELETED)
```
✓ detalle_factura       - Invoice line items
✓ seccion_factura       - Invoice sections
✓ factura_metadata      - Invoice metadata
✓ deuda                 - Accounts receivable
✓ factura               - Invoices
✓ ordenes_guardadas     - Saved orders
✓ precio_por_grupo      - Group pricing
✓ compra                - Purchase records
✓ producto_locks        - Product locks
✓ producto              - Products
✓ cliente               - Clients
✓ grupo                 - Customer groups
✓ tipo_cliente          - Customer types
```

### System Tables (OPTIONAL - Can be preserved)
```
✓ logs_sistema          - Application logs
✓ eventos_sistema       - System events
✓ log_accesos           - Access logs
```

### Reset Sequences
```
✓ folio_sequence        - Reset to 1
✓ factura_sequence      - Reset to 1
```

### Preserved Tables
```
✗ usuarios_sistema      - User accounts (PRESERVED)
```

## 🔄 After Cleanup - Next Steps

1. **Verify Application Starts**
   ```bash
   python main.py
   ```

2. **Create Customer Types** (tipos_cliente)
   - Mayorista (Wholesale)
   - Minorista (Retail)
   - Distribuidor (Distributor)
   - etc.

3. **Create Customer Groups** (grupos)
   - Associate with customer types
   - Define group codes

4. **Import Product Catalog**
   - Add all products
   - Set units and stock levels

5. **Configure Group Pricing**
   - Set prices for each product/group combination
   - Different prices per customer segment

6. **Create Initial Clients**
   - Add customer information
   - Assign to appropriate groups

## 💾 Backup Recommendations

### Cloud SQL Backup
```bash
# Export to Google Cloud Storage
gcloud sql export sql bodega-disfruleg-dev \
  gs://YOUR_BUCKET_NAME/backup_$(date +%Y%m%d_%H%M%S).sql \
  --database=disfruleg
```

### Local Backup
```bash
# Create local backup
mysqldump -u Jared -p disfruleg > backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore from Backup
```bash
# Restore from local backup
mysql -u Jared -p disfruleg < backups/backup_20250105_143000.sql

# Or from Cloud Storage
gcloud sql import sql bodega-disfruleg-dev \
  gs://YOUR_BUCKET_NAME/backup_20250105_143000.sql \
  --database=disfruleg
```

## 🛡️ Safety Features

The Python script includes multiple safety checks:

1. **Backup Confirmation** - Must confirm backup was created
2. **Statistics Display** - Shows what will be deleted
3. **Financial Summary** - Shows money earned/spent/owed
4. **Final Confirmation** - Double-check before execution
5. **Options** - Choose to keep logs
6. **Verification** - Shows post-cleanup stats
7. **Error Handling** - Graceful error messages

## 🔧 Customization

### Keep User Accounts
The script always keeps user accounts. To also delete users, edit `cleanup_database.sql`:

```sql
-- Uncomment this line to delete all users
TRUNCATE TABLE usuarios_sistema;
```

### Keep Only Admin User
```sql
-- Keep only admin user
DELETE FROM usuarios_sistema WHERE rol != 'admin' OR username != 'admin';
```

### Keep System Logs
When running the Python script, choose "yes" when asked:
```
📝 ¿Deseas mantener los logs del sistema? (yes/no): yes
```

## 📝 Example Output

```
======================================================================
                  DATABASE CLEANUP TOOL - DISFRULEG
======================================================================

⚠️  WARNING: This will DELETE ALL business data from the database!
   - Products, Clients, Invoices, Debts, Orders
   - Purchase history, pricing, financial records
   - System logs and events

✅  This will PRESERVE:
   - Database structure (tables, views, triggers)
   - User accounts (optional)
======================================================================

======================================================================
                        ESTADÍSTICAS ACTUALES
======================================================================
Tabla                                           Registros
----------------------------------------------------------------------
Productos                                             152
Clientes                                               43
Grupos                                                  5
Tipos de Cliente                                        3
Facturas                                              234
Detalles de Factura                                 1,458
Deudas                                                 89
Órdenes Guardadas                                      12
======================================================================

======================================================================
                        RESUMEN FINANCIERO
======================================================================

  Total Ventas:          $    45,678.50
  Total Costos:          $    32,100.25
  ─────────────────────────────────────────────
  Ganancia Bruta:        $    13,578.25

  Deudas Pagadas:        $    38,200.00
  Deudas Pendientes:     $     7,478.50

======================================================================

🧹 Ejecutando limpieza de base de datos...
✅ Limpieza completada exitosamente!

======================================================================
                   ESTADÍSTICAS POST-LIMPIEZA
======================================================================
Tabla                                           Registros
----------------------------------------------------------------------
Productos                                               0
Clientes                                                0
Grupos                                                  0
======================================================================

======================================================================
              ✅ BASE DE DATOS LISTA PARA PRODUCCIÓN
======================================================================

📝 Próximos pasos:
   1. Verificar que la aplicación inicia correctamente
   2. Crear los tipos de cliente necesarios
   3. Crear los grupos de clientes
   4. Importar el catálogo de productos
   5. Configurar los precios por grupo

======================================================================
```

## 🆘 Troubleshooting

### Connection Issues
- Verify Google Cloud credentials are configured
- Check that `credentials.json` exists in the project root
- Ensure Cloud SQL instance is running

### Permission Errors
- Verify database user has TRUNCATE, DELETE, UPDATE permissions
- Check that foreign key checks can be disabled

### Script Errors
- Make sure you're running from the project root
- Verify Python dependencies are installed
- Check database connection in `.env` file

## 📞 Support

If you encounter issues:
1. Check the error message carefully
2. Verify your backup exists and is complete
3. Review the SQL script for any database-specific syntax
4. Test on a development database first

## 🔐 Security Notes

- ⚠️ Never commit database backups to version control
- ⚠️ Keep `credentials.json` secure and out of git
- ✅ Always test on non-production databases first
- ✅ Verify backups can be restored before cleanup
- ✅ Document any custom data that needs manual recreation
