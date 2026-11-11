#!/bin/bash
# =============================================
# ALFA ERP — Setup inicial del servidor
# Ejecutar como root en Ubuntu 22.04
# =============================================
set -e

echo "======================================"
echo "  ALFA ERP — Configurando servidor"
echo "======================================"

# 1. Actualizar sistema
apt-get update && apt-get upgrade -y

# 2. Instalar dependencias básicas
apt-get install -y \
  curl wget git unzip \
  ufw fail2ban \
  ca-certificates gnupg

# 3. Instalar Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 4. Habilitar Docker al inicio
systemctl enable docker
systemctl start docker

# 5. Configurar Firewall
# Solo se exponen al internet: 22 (SSH), 80 (HTTP→redirige a HTTPS), 443 (HTTPS)
# Los puertos 3000/8080/8003 están atados a 127.0.0.1 en Docker y nginx los proxea
# internamente — nunca deben ser accesibles desde el exterior.
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh         # Puerto 22  — administración
ufw allow 80/tcp      # Puerto 80  — HTTP (nginx redirige a HTTPS)
ufw allow 443/tcp     # Puerto 443 — HTTPS (nginx, entrada principal)
ufw --force enable

echo ""
echo "✅ Servidor configurado correctamente"
echo "   Docker: $(docker --version)"
echo "   Firewall: activo"
echo ""
echo "➡️  Siguiente paso: ejecutar deploy.sh"
