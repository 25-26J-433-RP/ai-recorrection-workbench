# Akura AI - Update Azure VM Ollama (Models Only)
# The VM only hosts Ollama models. The FastAPI backend runs on GCP Cloud Run.
# Run from project root: .\scripts\update-azure-vm.ps1
# Optionally set: $env:AZURE_VM_IP = "20.212.24.114" and $env:AZURE_USER = "azureuser"

$ErrorActionPreference = "Stop"

$VM_IP = if ($env:AZURE_VM_IP) { $env:AZURE_VM_IP } else { "20.212.24.114" }
$USER  = if ($env:AZURE_USER) { $env:AZURE_USER } else { "azureuser" }

Write-Host "=== Akura AI - Update Azure VM (Models Only) ===" -ForegroundColor Cyan
Write-Host "Target: ${USER}@${VM_IP}"
Write-Host "Role:   Ollama model server (no FastAPI backend)"
Write-Host ""

# Configure Ollama to listen on all interfaces (for GCP Cloud Run access)
Write-Host "[1/3] Configuring Ollama to listen on 0.0.0.0..." -ForegroundColor Yellow
ssh "${USER}@${VM_IP}" 'sudo mkdir -p /etc/systemd/system/ollama.service.d && printf "[Service]\nEnvironment=\"OLLAMA_HOST=0.0.0.0\"\nEnvironment=\"OLLAMA_ORIGINS=*\"\n" | sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null && sudo systemctl daemon-reload && sudo systemctl restart ollama'
Write-Host "OK" -ForegroundColor Green

# Wait for Ollama to be ready
Write-Host "[2/3] Waiting for Ollama to start..." -ForegroundColor Yellow
ssh "${USER}@${VM_IP}" 'for i in $(seq 1 30); do curl -sf http://localhost:11434/api/tags > /dev/null 2>&1 && break; sleep 2; done'
Write-Host "OK" -ForegroundColor Green

# Verify models are available, pull if missing
Write-Host "[3/3] Verifying models..." -ForegroundColor Yellow
ssh "${USER}@${VM_IP}" 'echo "Checking Akura model..." && if ollama list | grep -q "akura_ai_sinhala_dyslexic_word_corrector_4bit"; then echo "  Akura model: OK"; else echo "  Pulling Akura model..." && ollama pull hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M; fi && echo "Checking secondary model..." && if ollama list | grep -q "gemini-3-flash-preview"; then echo "  Secondary model: OK"; else echo "  Secondary model not found. Run on VM: ollama signin google && ollama pull gemini-3-flash-preview:latest"; fi'
Write-Host "OK" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Azure VM update complete (Models Only)!" -ForegroundColor Green
Write-Host ""
Write-Host "  Ollama: http://${VM_IP}:11434"
Write-Host "  API:    https://akura-ai-1008980279040.us-central1.run.app (GCP Cloud Run)" 
Write-Host ""
Write-Host "If the secondary model is missing, SSH in and run:" -ForegroundColor Yellow
Write-Host "  ssh ${USER}@${VM_IP}" -ForegroundColor Gray
Write-Host "  ollama signin google" -ForegroundColor Gray
Write-Host "  ollama pull gemini-3-flash-preview:latest" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan
