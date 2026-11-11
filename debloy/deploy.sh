#!/bin/bash
# =============================================
# ALFA ERP — Script de despliegue
# Ejecutar en el servidor después de setup-server.sh
# =============================================
set -e

APP_DIR="/opt/alfa-erp"

echo "======================================"
echo "  ALFA ERP — Desplegando aplicación"
echo "======================================"

# Verificar que existe el archivo de entorno
if [ ! -f "$APP_DIR/.env.prod" ]; then
  echo "❌ ERROR: No se encontró $APP_DIR/.env.prod"
  echo "   Copia .env.prod.example → .env.prod y configura las variables"
  exit 1
fi

cd $APP_DIR

# Cargar variables de entorno
export $(grep -v '^#' .env.prod | xargs)

echo "🔨 Construyendo imágenes Docker..."
docker compose -f docker-compose.prod.yml --env-file .env.prod build

echo "🚀 Iniciando servicios..."
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

echo "⏳ Esperando que los servicios estén listos..."
sleep 15

echo "🔍 Verificando estado..."
docker compose -f docker-compose.prod.yml ps

echo ""
echo "======================================"
echo "  ✅ ALFA ERP desplegado correctamente"
echo "======================================"
echo "  Frontend: http://$(curl -s ifconfig.me)"
echo "  API:      http://$(curl -s ifconfig.me):8080"
echo "======================================"
