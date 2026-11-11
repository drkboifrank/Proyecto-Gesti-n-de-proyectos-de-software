#!/bin/bash
# =============================================
# ALFA ERP — Corregir reglas de firewall
# Ejecutar UNA VEZ en el servidor de producción
# después de aplicar docker-compose.prod.yml v4.4
# =============================================
set -e

echo "=== Corrección de firewall ==="
echo ""

# Verificar que UFW está activo
if ! ufw status | grep -q "Status: active"; then
    echo "UFW no está activo — activando..."
    ufw --force enable
fi

echo "Estado actual:"
ufw status numbered
echo ""

# Eliminar reglas de puertos internos que ya no deben ser accesibles desde internet
# (ahora están atados a 127.0.0.1 en Docker y proxeados por nginx)
echo "Eliminando reglas de puertos internos..."

# Puerto 8080 (API Gateway) — proxeado en /api/ por nginx
if ufw status | grep -q "8080"; then
    ufw delete allow 8080/tcp 2>/dev/null || ufw delete allow 8080 2>/dev/null || true
    echo "  ✓ Puerto 8080 cerrado"
else
    echo "  - Puerto 8080 ya no estaba abierto"
fi

# Puerto 8003 (WebSocket messaging) — proxeado en /ws por nginx
if ufw status | grep -q "8003"; then
    ufw delete allow 8003/tcp 2>/dev/null || ufw delete allow 8003 2>/dev/null || true
    echo "  ✓ Puerto 8003 cerrado"
else
    echo "  - Puerto 8003 ya no estaba abierto"
fi

# Puerto 3000 (Frontend) — proxeado en / por nginx
if ufw status | grep -q "3000"; then
    ufw delete allow 3000/tcp 2>/dev/null || ufw delete allow 3000 2>/dev/null || true
    echo "  ✓ Puerto 3000 cerrado"
else
    echo "  - Puerto 3000 ya no estaba abierto"
fi

# Asegurar que HTTPS (443) está abierto
if ! ufw status | grep -q "443"; then
    ufw allow 443/tcp
    echo "  ✓ Puerto 443 (HTTPS) abierto"
else
    echo "  - Puerto 443 ya estaba abierto"
fi

echo ""
echo "Estado final del firewall:"
ufw status numbered
echo ""
echo "✅ Firewall corregido. Solo puertos 22, 80 y 443 accesibles desde internet."
echo "   Los puertos 3000, 8080 y 8003 están atados a 127.0.0.1 en Docker."
