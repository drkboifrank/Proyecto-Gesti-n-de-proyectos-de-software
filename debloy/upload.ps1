# Sube el proyecto al servidor y compila el frontend localmente
param([string]$ServerIP = "142.93.241.97", [string]$User = "root")

$dest = "$User@${ServerIP}:/opt/alfa-erp/"
$project = "C:\Users\HP\Alfa 2.0"

Write-Host "=== ALFA ERP Deploy ===" -ForegroundColor Cyan

# 1. Compilar frontend localmente
Write-Host "[1/4] Compilando frontend localmente..." -ForegroundColor Yellow
$env:VITE_API_URL        = "https://erp.alfavidrioyaluminio.com/api"
$env:VITE_WS_URL         = "wss://erp.alfavidrioyaluminio.com/ws"
$env:VITE_VAPID_PUBLIC_KEY = "BNmPTc7KvwxKRMMkwz06LlkVjasaZrnmVkfyTVCvJHN3kKdW01dvNNOMCu7c848AyfF1TE-wfXdyoBxUW11mqwg"
Push-Location "$project\frontend"
try {
    npm.cmd run build
    if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Build del frontend fallo" -ForegroundColor Red; exit 1 }
} finally {
    Pop-Location
}

if (-not (Test-Path "$project\frontend\dist\index.html")) {
    Write-Host "ERROR: No se encontro frontend\dist\index.html despues del build" -ForegroundColor Red
    exit 1
}
Write-Host "Frontend compilado OK" -ForegroundColor Green

# 2. Subir servicios y config
Write-Host "[2/4] Subiendo servicios y configuracion..." -ForegroundColor Yellow

# Empaquetar servicios excluyendo __pycache__ y .pyc (evita cientos de archivos innecesarios)
python -c "
import tarfile, os
def exclude(ti):
    if '__pycache__' in ti.name or ti.name.endswith('.pyc'):
        return None
    return ti
with tarfile.open(r'$project\deploy\services.tar.gz', 'w:gz') as tar:
    tar.add(r'$project\services', arcname='services', filter=exclude)
print('services.tar.gz creado')
"
scp "$project\deploy\services.tar.gz" "${User}@${ServerIP}:/tmp/services.tar.gz"
ssh "$User@$ServerIP" "tar -xzf /tmp/services.tar.gz -C /opt/alfa-erp/ && rm /tmp/services.tar.gz"

scp "$project\docker-compose.prod.yml" "${dest}"
ssh "$User@$ServerIP" "mkdir -p /opt/alfa-erp/deploy"
scp "$project\deploy\update.sh" "${dest}deploy/"
ssh "$User@$ServerIP" "chmod +x /opt/alfa-erp/deploy/update.sh"

# 3. Subir frontend (solo src + dist precompilado)
Write-Host "[3/4] Subiendo frontend..." -ForegroundColor Yellow
ssh "$User@$ServerIP" "mkdir -p /opt/alfa-erp/frontend"
scp "$project\frontend\Dockerfile"        "${dest}frontend/"
scp "$project\frontend\nginx.conf"        "${dest}frontend/" 2>$null
scp "$project\frontend\package.json"      "${dest}frontend/"
scp "$project\frontend\vite.config.ts"    "${dest}frontend/"
scp "$project\frontend\tsconfig.json"     "${dest}frontend/"
scp "$project\frontend\tailwind.config.js" "${dest}frontend/"
scp "$project\frontend\postcss.config.js" "${dest}frontend/"
scp "$project\frontend\index.html"        "${dest}frontend/"
scp -r "$project\frontend\src"            "${dest}frontend/"
scp -r "$project\frontend\public"         "${dest}frontend/" 2>$null

# Subir dist precompilado y Dockerfile especial
python -c "
import tarfile
with tarfile.open(r'$project\deploy\dist.tar.gz', 'w:gz') as tar:
    tar.add(r'$project\frontend\dist', arcname='dist')
print('dist.tar.gz creado')
"
scp "$project\deploy\dist.tar.gz" "${User}@${ServerIP}:/tmp/dist.tar.gz"

# Crear Dockerfile.prebuilt en el servidor
ssh "$User@$ServerIP" @"
tar -xzf /tmp/dist.tar.gz -C /opt/alfa-erp/frontend/
cat > /opt/alfa-erp/frontend/Dockerfile.prebuilt << 'EOF'
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY dist /usr/share/nginx/html
EXPOSE 80
CMD [\"nginx\", \"-g\", \"daemon off;\"]
EOF
echo Dockerfile.prebuilt creado
"@

# 4. Instrucciones finales
Write-Host ""
Write-Host "[4/4] Archivos subidos. Ahora en el servidor ejecuta:" -ForegroundColor Green
Write-Host "  ssh root@$ServerIP" -ForegroundColor White
Write-Host "  cd /opt/alfa-erp && bash deploy/update.sh" -ForegroundColor White
