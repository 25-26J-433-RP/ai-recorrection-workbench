#!/usr/bin/env bash
# Akura AI - Google Cloud Run Deployment Script (Bash)
# Run from project root: ./scripts/deploy-gcp-cloudrun.sh
# Requires: HF_API_TOKEN set (and optionally GCP_PROJECT_ID, GCP_REGION)

set -e

PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="akura-ai"
REPO_NAME="akura-ai"
IMAGE_NAME="akura-ai:latest"

if [ -z "$PROJECT_ID" ]; then
  echo "Error: GCP project not set. Set GCP_PROJECT_ID or run: gcloud config set project YOUR_PROJECT_ID"
  exit 1
fi

if [ -z "$HF_API_TOKEN" ]; then
  echo "Error: HF_API_TOKEN environment variable is required"
  echo "Get your token at: https://huggingface.co/settings/tokens"
  exit 1
fi

IMAGE="us-central1-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}"
SECRET_NAME="akura-hf-token"

echo "=== Akura AI - GCP Cloud Run Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "[1/4] Ensuring Artifact Registry repository exists..."
gcloud artifacts repositories describe "$REPO_NAME" --location=us-central1 2>/dev/null || \
  gcloud artifacts repositories create "$REPO_NAME" --repository-format=docker --location=us-central1
echo "OK"

echo "[2/4] Building and pushing image..."
gcloud builds submit --tag "$IMAGE" --timeout=1200 .
echo "OK"

echo "[3/4] Ensuring secret $SECRET_NAME exists..."
if ! gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" &>/dev/null; then
  echo -n "$HF_API_TOKEN" | gcloud secrets create "$SECRET_NAME" --data-file=- --project="$PROJECT_ID"
else
  echo -n "$HF_API_TOKEN" | gcloud secrets versions add "$SECRET_NAME" --data-file=- --project="$PROJECT_ID"
fi
echo "OK"

echo "[4/4] Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars "LLM_PROVIDER=huggingface" \
  --set-env-vars "HF_MODEL_ID=hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit" \
  --set-env-vars "ENVIRONMENT=production" \
  --set-env-vars "LOG_LEVEL=INFO" \
  --set-env-vars "ALLOWED_ORIGINS=*" \
  --set-secrets "HF_API_TOKEN=${SECRET_NAME}:latest"
echo "OK"

URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')
echo ""
echo "=========================================="
echo "Deployment complete!"
echo "API URL:  $URL"
echo "Health:   $URL/api/v1/health"
echo "Docs:     $URL/docs"
echo "=========================================="
