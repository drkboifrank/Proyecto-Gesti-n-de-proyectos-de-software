#!/bin/bash
# =============================================
# ALFA ERP — Actualizar aplicación en servidor
# =============================================
set -e
APP_DIR="/opt/alfa-erp"
cd $APP_DIR

# Siempre usar .env.prod como .env principal
cp .env.prod .env

echo "Reconstruyendo servicios..."
docker compose -f docker-compose.prod.yml --env-file .env.prod build \
    auth crm inventory accounting gateway messaging

echo "Construyendo frontend con dist precompilado..."
docker build --no-cache -f frontend/Dockerfile.prebuilt -t alfa-erp-frontend:latest frontend/

# Migraciones de BD (columnas nuevas si no existen)
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db-crm \
    psql -U ${POSTGRES_USER:-erp_prod} -d crm_db -c \
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS warranty_start TIMESTAMP; ALTER TABLE projects ADD COLUMN IF NOT EXISTS warranty_notes TEXT;" 2>/dev/null || true

# Migración: is_readonly_super en auth_db
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db-auth \
    psql -U ${POSTGRES_USER:-erp_prod} -d auth_db -c \
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_readonly_super BOOLEAN DEFAULT FALSE;" 2>/dev/null || true

# Migración: email y teléfono del asesor en cotizaciones
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db-crm \
    psql -U ${POSTGRES_USER:-erp_prod} -d crm_db -c \
    "ALTER TABLE quotes ADD COLUMN IF NOT EXISTS assigned_to_email VARCHAR(255); ALTER TABLE quotes ADD COLUMN IF NOT EXISTS assigned_to_phone VARCHAR(50);" 2>/dev/null || true

# Migración: vendor_name en proyectos (vendedor que creó el proyecto)
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db-crm \
    psql -U ${POSTGRES_USER:-erp_prod} -d crm_db -c \
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS vendor_name VARCHAR(255);" 2>/dev/null || true

# Migración: target_role en notificaciones (para notificar por rol, ej. Contador)
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db-crm \
    psql -U ${POSTGRES_USER:-erp_prod} -d crm_db -c \
    "ALTER TABLE notifications ADD COLUMN IF NOT EXISTS target_role VARCHAR(50);" 2>/dev/null || true

# Migración: vendor_photo_url en proyectos
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db-crm \
    psql -U ${POSTGRES_USER:-erp_prod} -d crm_db -c \
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS vendor_photo_url TEXT;" 2>/dev/null || true

# Migración: category de expenses de ENUM nativo a texto libre (categorías custom)
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db-accounting \
    psql -U ${POSTGRES_USER:-erp_prod} -d accounting_db -c \
    "ALTER TABLE expenses ALTER COLUMN category TYPE VARCHAR(50) USING category::text; ALTER TABLE expenses ALTER COLUMN category SET DEFAULT 'other';" 2>/dev/null || true

# Migración: tablas de reportes generales
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db-crm \
    psql -U ${POSTGRES_USER:-erp_prod} -d crm_db -c \
    "CREATE TABLE IF NOT EXISTS general_reports (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        report_date DATE NOT NULL,
        description TEXT,
        created_by VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS general_report_photos (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        report_id UUID REFERENCES general_reports(id) ON DELETE CASCADE,
        filename VARCHAR(255) NOT NULL,
        original_name VARCHAR(255),
        url TEXT NOT NULL,
        uploaded_by VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW()
    );" 2>/dev/null || true

# Migración: trabajadores y proyecto en reportes generales (Reportes Diarios v2)
docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db-crm \
    psql -U ${POSTGRES_USER:-erp_prod} -d crm_db -c \
    "ALTER TABLE general_reports ADD COLUMN IF NOT EXISTS project_id UUID REFERENCES projects(id) ON DELETE SET NULL;
    CREATE TABLE IF NOT EXISTS general_report_workers (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        report_id UUID NOT NULL REFERENCES general_reports(id) ON DELETE CASCADE,
        worker_id UUID NOT NULL REFERENCES workers(id) ON DELETE CASCADE
    );" 2>/dev/null || true

echo "Levantando contenedores..."
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --no-build \
    --force-recreate auth crm inventory accounting gateway messaging

# Frontend: recrear manualmente (evita que docker compose rebuilde con npm)
docker rm -f alfa-erp-frontend-1 2>/dev/null || true
docker run -d \
    --name alfa-erp-frontend-1 \
    --network alfa-erp_erp-net \
    -p 127.0.0.1:3000:80 \
    --restart always \
    alfa-erp-frontend:latest

echo ""
echo "Actualizacion completada"
docker ps --filter name=alfa-erp --format "table {{.Names}}\t{{.Status}}"
