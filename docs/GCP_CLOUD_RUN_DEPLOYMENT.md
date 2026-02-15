# Akura AI — Google Cloud Run Deployment

This guide covers hosting the **Akura AI** backend on **Google Cloud Run** for serverless, request-based deployment. Cloud Run scales to zero when idle and uses the **Hugging Face Inference API** for LLM (no Ollama in the container).

---

## 1. Architecture

```
  [Frontend / Mobile] ──►  Cloud Run (Akura API)  ──►  Hugging Face Inference API
                                │
                                └── (optional) Supabase / Gemini for DB & OCR
```

- **Cloud Run**: Runs the FastAPI app only (no local LLM).
- **LLM**: `LLM_PROVIDER=huggingface` — pay per request via Hugging Face.
- **Port**: Cloud Run injects `PORT=8080`; the app listens on that port.

---

## 2. Prerequisites

- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install) installed and logged in.
- A GCP project with **Cloud Run** and **Artifact Registry** (or Container Registry) enabled.
- [Hugging Face token](https://huggingface.co/settings/tokens) for the inference API.

```powershell
# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## 3. One-Time Setup

### 3.1 Enable APIs

```powershell
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3.2 Create Artifact Registry repository (if needed)

```powershell
gcloud artifacts repositories create akura-ai --repository-format=docker --location=us-central1
```

---

## 4. Deploy to Cloud Run

### Option A: Deploy with PowerShell script (recommended)

From the project root (`ai-recorrection-workbench`):

```powershell
$env:HF_API_TOKEN = "your_huggingface_token"
$env:GCP_PROJECT_ID = "your-gcp-project-id"   # optional, uses gcloud config
.\scripts\deploy-gcp-cloudrun.ps1
```

### Option B: Manual deploy

```powershell
# From ai-recorrection-workbench/
$PROJECT_ID = "your-gcp-project-id"
$REGION = "us-central1"
$IMAGE = "us-central1-docker.pkg.dev/$PROJECT_ID/akura-ai/akura-ai:latest"

# Build and push
gcloud builds submit --tag $IMAGE --timeout=1200

# Deploy (create or update)
gcloud run deploy akura-ai `
  --image $IMAGE `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --port 8080 `
  --memory 1Gi `
  --cpu 1 `
  --min-instances 0 `
  --max-instances 10 `
  --timeout 300 `
  --set-env-vars "LLM_PROVIDER=huggingface" `
  --set-env-vars "HF_MODEL_ID=hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit" `
  --set-env-vars "ENVIRONMENT=production" `
  --set-env-vars "LOG_LEVEL=INFO" `
  --set-env-vars "ALLOWED_ORIGINS=*" `
  --set-secrets "HF_API_TOKEN=hf-token:latest"
```

Create the secret and grant Cloud Run access:

```powershell
# Create secret
echo -n "your_hf_token" | gcloud secrets create akura-hf-token --data-file=- --project=$PROJECT_ID

# Grant the default Cloud Run service account access to the secret (replace PROJECT_NUMBER)
$PROJECT_NUMBER = (gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding akura-hf-token `
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor" `
  --project=$PROJECT_ID
```

The deploy script creates/updates the secret `akura-hf-token` for you; ensure the Cloud Run service account has `roles/secretmanager.secretAccessor` on that secret (script may require you to run the `add-iam-policy-binding` once).

---

## 5. Environment Variables (Cloud Run)

| Variable | Value | Notes |
|----------|--------|--------|
| `PORT` | 8080 | Set by Cloud Run (do not override) |
| `LLM_PROVIDER` | huggingface | Required for request-based inference |
| `HF_API_TOKEN` | (secret) | Hugging Face token |
| `HF_MODEL_ID` | hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit | Model ID |
| `ENVIRONMENT` | production | |
| `LOG_LEVEL` | INFO | |
| `ALLOWED_ORIGINS` | * or your frontend URLs | CORS |
| `DATABASE_URL` | (optional) | Supabase PostgreSQL for sessions |
| `GEMINI_API_KEY` | (optional) | For OCR feature |

---

## 6. After Deployment

- **Service URL**: Shown in script output or:
  ```powershell
  gcloud run services describe akura-ai --region=us-central1 --format='value(status.url)'
  ```
- **Health check**: `https://YOUR_SERVICE_URL/api/v1/health`
- **API docs**: `https://YOUR_SERVICE_URL/docs`

---

## 7. Update / Redeploy

To push a new version (e.g. after code changes):

```powershell
.\scripts\deploy-gcp-cloudrun.ps1
```

Or manually: run the same `gcloud builds submit` and `gcloud run deploy` commands; Cloud Run will roll out the new revision.

---

## 8. Cost Notes

- **Cloud Run**: Pay per request and CPU/memory time; scales to zero when idle.
- **Hugging Face**: Pay per inference request (see Hugging Face pricing).
- No cost when there are no requests (unlike a 24/7 VM).

---

## 9. Comparison: Cloud Run vs Azure VM

| | Cloud Run | Azure VM |
|--|-----------|----------|
| **LLM** | Hugging Face API (per request) | Ollama + fine-tuned model on VM |
| **Idle cost** | ~$0 | ~\$6–68/month (disk + optional compute) |
| **Cold start** | Few seconds (no model load) | First request ~80s (model load) |
| **Latency** | Network call to HF | Local inference (~30–80s CPU) |
| **Best for** | Low traffic, demos, cost-sensitive | Full control, no HF dependency, higher traffic |

For **Azure VM** deployment (Ollama on VM), see [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md).
