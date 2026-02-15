# Akura AI -- Azure VM Deployment Report

> **Deployment Date**: 2026-02-08
> **Status**: Deployed and Verified
> **VM IP**: `20.212.24.114`
> **API Base URL**: `http://20.212.24.114:8000`

---

## 1. Architecture Overview

```
                        ┌─────────────────────────────────────────┐
                        │          Azure VM (Standard_B2ms)       │
                        │          Southeast Asia Region          │
                        │                                         │
  [Frontend App] ──────►│  ┌─────────────┐    ┌───────────────┐  │
  [Mobile App]   ──────►│  │  FastAPI     │───►│   Ollama      │  │
  [Postman]      ──────►│  │  (port 8000) │    │  (port 11434) │  │
                        │  │              │◄───│               │  │
                        │  └─────────────┘    └───────────────┘  │
                        │                           │             │
                        │                     ┌─────┴─────┐      │
                        │                     │ Akura AI  │      │
                        │                     │ GGUF 4-bit│      │
                        │                     │ (4.9 GB)  │      │
                        │                     └───────────┘      │
                        └─────────────────────────────────────────┘
```

Both the **FastAPI backend** and **Ollama LLM server** run on the same VM. The fine-tuned Akura AI GGUF model (4-bit quantized, 4.9 GB) is loaded by Ollama and served locally.

---

## 2. Azure Resources Created

| Resource | Name | Details |
|----------|------|---------|
| **Resource Group** | `akura-ai-rg` | Southeast Asia region |
| **Virtual Machine** | `akura-ai-vm` | Standard_B2ms (2 vCPU, 8 GB RAM) |
| **OS Disk** | Managed SSD | 64 GB, Ubuntu 24.04 LTS |
| **Public IP** | `20.212.24.114` | Standard SKU, static |
| **NSG Rules** | SSH (22), API (8000) | Open to all inbound |
| **Subscription** | Azure for Students | `it22178336@my.sliit.lk` |

---

## 3. Software Stack on VM

| Component | Version | Purpose |
|-----------|---------|---------|
| **Ubuntu** | 24.04 LTS | Operating system |
| **Python** | 3.12 | Runtime |
| **Ollama** | Latest | LLM serving engine |
| **FastAPI** | 0.109.0 | API framework |
| **Uvicorn** | 0.27.0 | ASGI server |
| **LangChain** | 0.1.0 | LLM integration |

---

## 4. Model Details

| Property | Value |
|----------|-------|
| **Model Name** | `hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M` |
| **Format** | GGUF (4-bit quantized, Q4_K_M) |
| **Size on Disk** | 4.9 GB |
| **Base Model** | Meta Llama 3.1 8B Instruct |
| **Fine-tuned For** | Sinhala dyslexia word correction |
| **RAM Usage** | ~5 GB at runtime |
| **Source** | [HuggingFace](https://huggingface.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit) |

---

## 5. API Endpoints Available

All endpoints are prefixed with `/api/v1`.

### Core Analysis (uses LLM)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze` | Analyze Sinhala text for dyslexic errors |
| `POST` | `/api/v1/analyze/batch` | Batch analyze multiple texts |
| `POST` | `/api/v1/check` | Quick error check (returns boolean) |

### OCR

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/ocr` | Extract Sinhala text from image (Gemini Vision) |
| `GET` | `/api/v1/ocr/status` | OCR service status |

### Child Essays

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/children/{child_id}/essays` | Submit essay for correction |
| `GET` | `/api/v1/children/{child_id}/essays` | List child's essays |
| `GET` | `/api/v1/children/{child_id}/essays/latest` | Latest essay |
| `GET` | `/api/v1/children/{child_id}/essays/{essay_id}` | Specific essay |
| `DELETE` | `/api/v1/children/{child_id}/essays/{essay_id}` | Delete essay |
| `GET` | `/api/v1/children` | List all children |

### Sessions & Feedback

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/sessions` | Save correction session |
| `GET` | `/api/v1/sessions` | List sessions |
| `GET` | `/api/v1/sessions/{id}` | Session details |
| `PUT` | `/api/v1/sessions/{id}` | Update session |
| `PATCH` | `/api/v1/sessions/{id}/corrections/{id}` | Teacher action on correction |
| `DELETE` | `/api/v1/sessions/{id}` | Delete session |
| `GET` | `/api/v1/sessions/export/training-data` | Export for fine-tuning |

### Student Tracking

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/students` | List all students |
| `GET` | `/api/v1/students/{id}/sessions` | Student sessions |
| `GET` | `/api/v1/students/{id}/progress` | Progress metrics |
| `GET` | `/api/v1/students/{id}/profile` | Dyslexia error fingerprint |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/config` | Current config |
| `GET` | `/api/v1/patterns` | Dyslexia pattern list |
| `GET` | `/api/v1/corrections` | Known corrections |
| `GET` | `/docs` | Swagger UI |

---

## 6. Test Results

### Health Check
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "modelStatus": "Ollama (hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M) connected",
  "ollamaConnected": true
}
```

### Analyze Endpoint Test
**Input:**
```json
{
  "text": "මම ගෙරද යනව",
  "include_correct_words": true
}
```

**Output:**
```json
{
  "success": true,
  "data": [
    {
      "word": "මම",
      "type": "correct",
      "dyslexiaPattern": null,
      "suggestion": null,
      "confidence": 1.0,
      "source": null
    },
    {
      "word": "ගෙරද",
      "type": "error",
      "dyslexiaPattern": "Visual Scrambling",
      "suggestion": "ගෙදර",
      "confidence": 0.9,
      "source": "ai"
    },
    {
      "word": "යනව",
      "type": "error",
      "dyslexiaPattern": "Spelling",
      "suggestion": "යනවා",
      "confidence": 0.9,
      "source": "ai"
    }
  ],
  "correctedText": "මම ගෙදර යනවා",
  "originalText": "මම ගෙරද යනව",
  "processingTimeMs": 83099.84,
  "modelUsed": "hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M"
}
```

**Result**: Model correctly identified 2 out of 3 words as errors and provided accurate corrections.

---

## 7. Configuration (.env on VM)

```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
ENVIRONMENT=production
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M
OLLAMA_TIMEOUT=300
MODEL_TEMPERATURE=0.3
MODEL_MAX_TOKENS=2048
AI_CONFIDENCE_THRESHOLD=0.7
LOG_LEVEL=INFO
LOG_FORMAT=json
ALLOWED_ORIGINS=*
```

---

## 8. Services (systemd)

Two services run on the VM, both set to auto-restart:

| Service | Description | Status |
|---------|-------------|--------|
| `ollama.service` | Ollama LLM server (port 11434) | enabled, active |
| `akura-ai.service` | FastAPI backend (port 8000) | enabled, active |

Both services start automatically on VM boot.

---

## 9. Cost Estimate

| Resource | Monthly Cost | Notes |
|----------|-------------|-------|
| VM (Standard_B2ms) | ~$60.74 | 2 vCPU, 8 GB RAM |
| OS Disk (64 GB SSD) | ~$3.00 | P6 managed disk |
| Public IP (Static) | ~$3.65 | Standard SKU |
| Network (outbound) | ~$0.50 | Estimated ~5 GB |
| **Total (24/7)** | **~$67.89/month** | |
| **Total (stopped)** | **~$6.65/month** | Disk + IP only |

### Cost with Student Credits ($100)
- Running 24/7: lasts ~1.5 months
- Running 4 hrs/day: lasts ~6 months
- Stopped when not needed: stretches credits significantly

---

## 10. VM Management Commands

### Start / Stop

```powershell
# Stop VM (deallocate = stop billing for compute)
az vm deallocate --resource-group akura-ai-rg --name akura-ai-vm

# Start VM
az vm start --resource-group akura-ai-rg --name akura-ai-vm
```

### SSH Access

```powershell
# Connect to VM
ssh azureuser@20.212.24.114

# Check API service status
ssh azureuser@20.212.24.114 "sudo systemctl status akura-ai"

# Check Ollama status
ssh azureuser@20.212.24.114 "sudo systemctl status ollama"

# View API logs
ssh azureuser@20.212.24.114 "sudo journalctl -u akura-ai -f"

# Restart API
ssh azureuser@20.212.24.114 "sudo systemctl restart akura-ai"
```

### Update Code on VM

**Option 1 – Use the update script (recommended)**

From project root (`ai-recorrection-workbench`):

```powershell
# Uses default VM IP 20.212.24.114 and user azureuser
.\scripts\update-azure-vm.ps1

# Or set custom IP/user:
$env:AZURE_VM_IP = "20.212.24.114"
$env:AZURE_USER = "azureuser"
.\scripts\update-azure-vm.ps1
```

**Option 2 – Manual SCP + restart**

```powershell
# From project root (c:\Github\sliit\ai-recorrection-workbench)
scp -r app/ azureuser@20.212.24.114:/home/azureuser/akura-ai/
scp requirements.txt azureuser@20.212.24.114:/home/azureuser/akura-ai/
ssh azureuser@20.212.24.114 "sudo systemctl restart akura-ai"
```

If you changed `requirements.txt`, SSH in and reinstall deps then restart:

```powershell
ssh azureuser@20.212.24.114
cd /home/azureuser/akura-ai && source venv/bin/activate && pip install -r requirements.txt
sudo systemctl restart akura-ai
```

### Delete Everything (cleanup)

```powershell
# WARNING: This deletes all Azure resources for this project
az group delete --name akura-ai-rg --yes --no-wait
```

---

## 11. Deployment Steps Summary

| Step | Action | Status |
|------|--------|--------|
| 1 | Install Azure CLI | Done |
| 2 | Login to Azure (`az login`) | Done |
| 3 | Register providers (Microsoft.Compute, Microsoft.Network) | Done |
| 4 | Create Resource Group (`akura-ai-rg`, Southeast Asia) | Done |
| 5 | Create VM (Standard_B2ms, Ubuntu 24.04, 64 GB disk) | Done |
| 6 | Open ports (22 for SSH, 8000 for API) | Done |
| 7 | Install Ollama on VM | Done |
| 8 | Pull Akura AI GGUF model (4.9 GB) | Done |
| 9 | Install Python, pip, venv on VM | Done |
| 10 | Copy app files via SCP | Done |
| 11 | Create Python virtual environment + install dependencies | Done |
| 12 | Create `.env` for production (Ollama mode) | Done |
| 13 | Create systemd service (`akura-ai.service`) | Done |
| 14 | Start service and verify | Done |
| 15 | Test health check | Passed |
| 16 | Test `/analyze` with Sinhala text | Passed |

---

## 12. Known Issues

1. **First request latency**: The first inference request after VM boot takes ~80 seconds (model loading into RAM). Subsequent requests are faster.

2. **CPU-only inference**: The B2ms VM has no GPU. Inference runs on CPU, so each request takes ~30-80 seconds depending on text length. This is acceptable for a correction workbench but not for real-time applications.

3. **University network firewall**: SLIIT university network blocks direct HTTP access to the VM IP (web filter on unrated URLs). The API works from other networks (home WiFi, mobile data, deployed frontends).

4. **No database configured**: The `DATABASE_URL` is not set. Session and feedback endpoints that require a database will return an error. Add a Supabase PostgreSQL URL to `.env` if needed.

---

## 13. Future Improvements

- [ ] Add HTTPS with a domain name (e.g., via Nginx + Let's Encrypt)
- [ ] Configure a database (Supabase) for session/feedback storage
- [ ] Set up auto-shutdown schedule to save credits
- [ ] Add monitoring/alerting for VM health
- [ ] Consider GPU VM (e.g., NC4as_T4_v3) for faster inference if budget allows
