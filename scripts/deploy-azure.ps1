# Akura AI - Azure Container Apps Deployment Script (PowerShell)
# Run from project root: .\scripts\deploy-azure.ps1

$ErrorActionPreference = "Stop"

# Configuration - UPDATE THESE
$RESOURCE_GROUP = if ($env:RESOURCE_GROUP) { $env:RESOURCE_GROUP } else { "akura-ai-rg" }
$LOCATION = if ($env:LOCATION) { $env:LOCATION } else { "eastus" }
$ACR_NAME = if ($env:ACR_NAME) { $env:ACR_NAME } else { "akuraaiacr" }
$APP_NAME = if ($env:APP_NAME) { $env:APP_NAME } else { "akura-ai-api" }
$IMAGE_NAME = "akura-ai:latest"

# Check for HF token
if (-not $env:HF_API_TOKEN) {
    Write-Host "Error: HF_API_TOKEN environment variable is required" -ForegroundColor Red
    Write-Host "Get your token at: https://huggingface.co/settings/tokens"
    exit 1
}

Write-Host "Deploying Akura AI to Azure Container Apps..." -ForegroundColor Cyan
Write-Host "Resource Group: $RESOURCE_GROUP"
Write-Host "Location: $LOCATION"
Write-Host ""

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION --output none
Write-Host "Resource group created" -ForegroundColor Green

# Create ACR (if not exists)
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --output none 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host "ACR created" -ForegroundColor Green } else { Write-Host "ACR already exists" -ForegroundColor Yellow }

# Build and push - run from project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Push-Location $projectRoot

Write-Host "Building and pushing image..." -ForegroundColor Cyan
az acr build --registry $ACR_NAME --image $IMAGE_NAME .
if ($LASTEXITCODE -ne 0) { Pop-Location; exit 1 }
Write-Host "Image pushed" -ForegroundColor Green

Pop-Location

# Create environment (if not exists)
az containerapp env create `
  --name akura-ai-env `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --output none 2>$null
if ($LASTEXITCODE -eq 0) { Write-Host "Environment created" -ForegroundColor Green } else { Write-Host "Environment already exists" -ForegroundColor Yellow }

# Create Container App
Write-Host "Creating Container App..." -ForegroundColor Cyan
az containerapp create `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --environment akura-ai-env `
  --image "$ACR_NAME.azurecr.io/$IMAGE_NAME" `
  --registry-server "$ACR_NAME.azurecr.io" `
  --ingress external `
  --target-port 8000 `
  --min-replicas 0 `
  --max-replicas 10 `
  --cpu 0.5 `
  --memory 1Gi `
  --env-vars "LLM_PROVIDER=huggingface" "HF_API_TOKEN=secretref:hf-token" "HF_MODEL_ID=hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit" `
  --secrets "hf-token=$env:HF_API_TOKEN" `
  --output none 2>$null

if ($LASTEXITCODE -ne 0) {
    # Maybe app exists - update it
    Write-Host "Updating existing Container App..." -ForegroundColor Yellow
    az containerapp update `
      --name $APP_NAME `
      --resource-group $RESOURCE_GROUP `
      --image "$ACR_NAME.azurecr.io/$IMAGE_NAME" `
      --output none
}

Write-Host "Container App deployed" -ForegroundColor Green
Write-Host ""

# Get URL
$URL = az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "API URL: https://$URL"
Write-Host "API Docs: https://$URL/docs"
Write-Host "==========================================" -ForegroundColor Cyan
