# Akura AI - Update Azure VM with latest code + dual-model support
# Run from project root: .\scripts\update-azure-vm.ps1
# Optionally set: $env:AZURE_VM_IP = "20.212.24.114" and $env:AZURE_USER = "azureuser"

$ErrorActionPreference = "Stop"

$VM_IP = if ($env:AZURE_VM_IP) { $env:AZURE_VM_IP } else { "20.212.24.114" }
$USER  = if ($env:AZURE_USER) { $env:AZURE_USER } else { "azureuser" }
$REMOTE_DIR = "/home/$USER/akura-ai"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Host "=== Akura AI - Update Azure VM (Dual-Model) ===" -ForegroundColor Cyan
Write-Host "Target: ${USER}@${VM_IP}"
Write-Host "Remote app dir: $REMOTE_DIR"
Write-Host ""

# Sync app code, config, and requirements
Write-Host "[1/6] Syncing app/ and requirements to VM..." -ForegroundColor Yellow
scp -r "$projectRoot\app" "${USER}@${VM_IP}:$REMOTE_DIR/"
scp "$projectRoot\requirements.txt" "${USER}@${VM_IP}:$REMOTE_DIR/"
if (Test-Path "$projectRoot\pyproject.toml") {
    scp "$projectRoot\pyproject.toml" "${USER}@${VM_IP}:$REMOTE_DIR/"
}
Write-Host "OK" -ForegroundColor Green

# Sync .env with dual-model configuration
Write-Host "[2/6] Updating .env on VM with dual-model config..." -ForegroundColor Yellow
$envContent = @"
# Akura AI - Production Environment (Azure VM)
HOST=0.0.0.0
PORT=8000
DEBUG=false
ENVIRONMENT=production

# Ollama (running on same VM)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M
OLLAMA_TIMEOUT=300

# Dual Model Pipeline (Akura primary + secondary model)
ENABLE_DUAL_MODEL=true
SECONDARY_OLLAMA_MODEL=gemini-3-flash-preview:latest
SECONDARY_OLLAMA_TIMEOUT=300
SECONDARY_OLLAMA_TEMPERATURE=0.3

# Model
MODEL_TEMPERATURE=0.3
MODEL_MAX_TOKENS=2048
AI_CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
ALLOWED_ORIGINS=*
"@
$envContent | ssh "${USER}@${VM_IP}" "cat > $REMOTE_DIR/.env"
Write-Host "OK" -ForegroundColor Green

# Configure Ollama to listen on all interfaces (for GCP Cloud Run access)
Write-Host "[3/6] Configuring Ollama to listen on 0.0.0.0..." -ForegroundColor Yellow
ssh "${USER}@${VM_IP}" @"
sudo mkdir -p /etc/systemd/system/ollama.service.d
echo '[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"' | sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart ollama
"@
Write-Host "OK" -ForegroundColor Green

# Wait for Ollama to be ready
Write-Host "[4/6] Waiting for Ollama to start..." -ForegroundColor Yellow
ssh "${USER}@${VM_IP}" 'for i in $(seq 1 30); do curl -sf http://localhost:11434/api/tags > /dev/null 2>&1 && break; sleep 2; done'
Write-Host "OK" -ForegroundColor Green

# Verify models are available, pull if missing
Write-Host "[5/6] Verifying models..." -ForegroundColor Yellow
ssh "${USER}@${VM_IP}" @"
echo 'Checking Akura model...'
ollama list | grep -q 'akura_ai_sinhala_dyslexic_word_corrector_4bit' && echo '  Akura model: OK' || {
    echo '  Pulling Akura model...'
    ollama pull hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M
}
echo 'Checking secondary model...'
ollama list | grep -q 'gemini-3-flash-preview' && echo '  Secondary model: OK' || {
    echo '  Secondary model not found. You need to run on the VM:'
    echo '    ollama login google'
    echo '    ollama pull gemini-3-flash-preview:latest'
}
"@
Write-Host "OK" -ForegroundColor Green

# Restart the API service
Write-Host "[6/6] Restarting akura-ai service..." -ForegroundColor Yellow
ssh "${USER}@${VM_IP}" "cd $REMOTE_DIR && source venv/bin/activate && pip install -r requirements.txt -q && sudo systemctl restart akura-ai"
ssh "${USER}@${VM_IP}" "sudo systemctl status akura-ai --no-pager"
Write-Host "OK" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Azure VM update complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  API:    http://${VM_IP}:8000"
Write-Host "  Health: http://${VM_IP}:8000/api/v1/health"
Write-Host "  Ollama: http://${VM_IP}:11434"
Write-Host ""
Write-Host "If the secondary model is missing, SSH in and run:" -ForegroundColor Yellow
Write-Host "  ssh ${USER}@${VM_IP}" -ForegroundColor Gray
Write-Host "  ollama login google" -ForegroundColor Gray
Write-Host "  ollama pull gemini-3-flash-preview:latest" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan
