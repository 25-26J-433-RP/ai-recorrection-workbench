#!/bin/bash
# Akura AI - Azure Container Apps Deployment Script
# Run from project root: ./scripts/deploy-azure.sh

set -e

# Configuration - UPDATE THESE
RESOURCE_GROUP="${RESOURCE_GROUP:-akura-ai-rg}"
LOCATION="${LOCATION:-eastus}"
ACR_NAME="${ACR_NAME:-akuraaiacr}"
APP_NAME="${APP_NAME:-akura-ai-api}"
IMAGE_NAME="akura-ai:latest"

# Check for HF token
if [ -z "$HF_API_TOKEN" ]; then
  echo "Error: HF_API_TOKEN environment variable is required"
  echo "Get your token at: https://huggingface.co/settings/tokens"
  exit 1
fi

echo "Deploying Akura AI to Azure Container Apps..."
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo ""

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION --output none
echo "✓ Resource group created"

# Create ACR (if not exists)
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --output none 2>/dev/null || echo "✓ ACR already exists"

# Build and push
echo "Building and pushing image..."
az acr build --registry $ACR_NAME --image $IMAGE_NAME . --output none
echo "✓ Image pushed"

# Create environment (if not exists)
az containerapp env create \
  --name akura-ai-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --output none 2>/dev/null || echo "✓ Environment already exists"

# Add secret
az containerapp secret set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --secrets hf-token=$HF_API_TOKEN \
  --output none 2>/dev/null || true

# Create or update Container App
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment akura-ai-env \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME \
  --registry-server $ACR_NAME.azurecr.io \
  --ingress external \
  --target-port 8000 \
  --min-replicas 0 \
  --max-replicas 10 \
  --cpu 0.5 \
  --memory 1Gi \
  --env-vars "LLM_PROVIDER=huggingface" "HF_API_TOKEN=secretref:hf-token" "HF_MODEL_ID=hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit" \
  --output none 2>/dev/null || \
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME \
  --output none

echo "✓ Container App deployed"
echo ""
echo "Getting URL..."
URL=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo ""
echo "=========================================="
echo "Deployment complete!"
echo "API URL: https://$URL"
echo "API Docs: https://$URL/docs"
echo "=========================================="
