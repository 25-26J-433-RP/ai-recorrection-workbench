# Akura AI - Google Cloud Run Deployment Script (PowerShell)
# Architecture: GCP Cloud Run (API) → Azure VM (Ollama + Models)
# Run from project root: .\scripts\deploy-gcp-cloudrun.ps1
#
# Required env vars:
#   AZURE_VM_IP          - Azure VM IP running Ollama (default: 20.212.24.114)
#   GCP_PROJECT_ID       - GCP project (default: akura-dyslexic)
#   GCP_REGION           - GCP region  (default: us-central1)
#   GEMINI_API_KEY       - For OCR feature (optional)

$ErrorActionPreference = "Stop"

$PROJECT_ID   = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { "akura-dyslexic" }
$REGION       = if ($env:GCP_REGION)     { $env:GCP_REGION }     else { "us-central1" }
$AZURE_VM_IP  = if ($env:AZURE_VM_IP)    { $env:AZURE_VM_IP }    else { "20.212.24.114" }
$SERVICE_NAME = "akura-ai"
$REPO_NAME    = "akura-ai"
$IMAGE_NAME   = "akura-ai:latest"

if (-not $PROJECT_ID) {
    Write-Host "Error: GCP project not set. Set GCP_PROJECT_ID or run: gcloud config set project YOUR_PROJECT_ID" -ForegroundColor Red
    exit 1
}

Write-Host "=== Akura AI - GCP Cloud Run Deployment ===" -ForegroundColor Cyan
Write-Host "Project:       $PROJECT_ID"
Write-Host "Region:        $REGION"
Write-Host "Azure VM:      $AZURE_VM_IP (Ollama models)"
Write-Host "Architecture:  Cloud Run (API) -> Azure VM (Ollama)"
Write-Host ""

# Verify Azure VM Ollama is reachable
Write-Host "[0/4] Verifying Azure VM Ollama is reachable..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://${AZURE_VM_IP}:11434/api/tags" -UseBasicParsing -TimeoutSec 10
    $models = ($ollamaCheck.Content | ConvertFrom-Json).models | Select-Object -ExpandProperty name
    Write-Host "  Ollama OK - Models: $($models -join ', ')" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Cannot reach Ollama at http://${AZURE_VM_IP}:11434" -ForegroundColor Red
    Write-Host "  Make sure port 11434 is open on Azure NSG and Ollama is listening on 0.0.0.0" -ForegroundColor Red
    Write-Host "  Continuing deployment anyway..." -ForegroundColor Yellow
}

# Image: Artifact Registry
$IMAGE = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}"

# Ensure Artifact Registry repo exists
Write-Host "[1/4] Ensuring Artifact Registry repository exists..." -ForegroundColor Yellow
$prevEAP = $ErrorActionPreference; $ErrorActionPreference = "Continue"
$null = gcloud artifacts repositories describe $REPO_NAME --location=$REGION --project=$PROJECT_ID 2>&1
$ErrorActionPreference = $prevEAP
if ($LASTEXITCODE -ne 0) {
    gcloud artifacts repositories create $REPO_NAME --repository-format=docker --location=$REGION --project=$PROJECT_ID
}
Write-Host "OK" -ForegroundColor Green

# Build and push
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Push-Location $projectRoot

Write-Host "[2/4] Building and pushing image (this may take a few minutes)..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE --timeout=1200 --project=$PROJECT_ID .
if ($LASTEXITCODE -ne 0) { Pop-Location; exit 1 }
Write-Host "OK" -ForegroundColor Green

Pop-Location

# Store secrets in GCP Secret Manager (idempotent)
Write-Host "[3/4] Configuring secrets..." -ForegroundColor Yellow
if ($env:GEMINI_API_KEY) {
    $SECRET_NAME = "akura-gemini-key"
    $secretExists = gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID 2>$null
    if (-not $secretExists) {
        echo -n $env:GEMINI_API_KEY | gcloud secrets create $SECRET_NAME --data-file=- --project=$PROJECT_ID
    } else {
        echo -n $env:GEMINI_API_KEY | gcloud secrets versions add $SECRET_NAME --data-file=- --project=$PROJECT_ID
    }
    Write-Host "  GEMINI_API_KEY stored in Secret Manager" -ForegroundColor Green
    $SECRETS_FLAG = "--set-secrets=GEMINI_API_KEY=${SECRET_NAME}:latest"
} else {
    Write-Host "  No GEMINI_API_KEY provided (OCR will be unavailable)" -ForegroundColor Gray
    $SECRETS_FLAG = ""
}
Write-Host "OK" -ForegroundColor Green

# Deploy to Cloud Run — API connects to Azure VM Ollama for LLM inference
Write-Host "[4/4] Deploying to Cloud Run..." -ForegroundColor Yellow

$envVars = @(
    "LLM_PROVIDER=ollama",
    "OLLAMA_BASE_URL=http://${AZURE_VM_IP}:11434",
    "OLLAMA_MODEL=hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M",
    "OLLAMA_TIMEOUT=300",
    "ENABLE_DUAL_MODEL=true",
    "SECONDARY_OLLAMA_MODEL=gemini-3-flash-preview:latest",
    "SECONDARY_OLLAMA_TIMEOUT=300",
    "SECONDARY_OLLAMA_TEMPERATURE=0.3",
    "MODEL_TEMPERATURE=0.3",
    "MODEL_MAX_TOKENS=2048",
    "AI_CONFIDENCE_THRESHOLD=0.7",
    "ENVIRONMENT=production",
    "LOG_LEVEL=INFO",
    "ALLOWED_ORIGINS=*"
) -join ","

$deployArgs = @(
    "run", "deploy", $SERVICE_NAME,
    "--image", $IMAGE,
    "--region", $REGION,
    "--project", $PROJECT_ID,
    "--platform", "managed",
    "--allow-unauthenticated",
    "--port", "8080",
    "--memory", "1Gi",
    "--cpu", "1",
    "--min-instances", "0",
    "--max-instances", "10",
    "--timeout", "900",
    "--set-env-vars", $envVars
)

if ($SECRETS_FLAG) {
    $deployArgs += $SECRETS_FLAG
}

& gcloud @deployArgs

if ($LASTEXITCODE -ne 0) { exit 1 }
Write-Host "OK" -ForegroundColor Green

$URL = gcloud run services describe $SERVICE_NAME --region $REGION --project=$PROJECT_ID --format="value(status.url)"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Cloud Run API:  $URL"
Write-Host "Health:         $URL/api/v1/health"
Write-Host "Swagger:        $URL/docs"
Write-Host ""
Write-Host "Azure VM Ollama: http://${AZURE_VM_IP}:11434"
Write-Host "==========================================" -ForegroundColor Cyan
