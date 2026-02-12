# 🧠 Akura AI - Intelligent Dyslexia Correction Engine

<div align="center">

![Akura AI](https://img.shields.io/badge/Akura%20AI-Dyslexia%20Correction-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?style=for-the-badge&logo=react)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange?style=for-the-badge)
![Supabase](https://img.shields.io/badge/Supabase-Database-green?style=for-the-badge&logo=supabase)

**A specialized, privacy-focused tool for detecting and correcting Sinhala writing errors specific to dyslexic students.**

**© 2025 SLIIT Research Project (25-26J-433-RP)**

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Frontend Features](#-frontend-features)
- [API Reference](#-api-reference)
- [Database Integration](#-database-integration)
- [Development](#-development)
- [Configuration](#-configuration)

---

## ✨ Features

### Core Capabilities

- **🤖 AI-Powered Correction**: Uses fine-tuned LLaMA 8B model via Ollama
- **📊 Pattern Detection**: Identifies 4 specific dyslexia patterns:
  - **Visual Scrambling**: Letter reordering (e.g., ගෙරද → ගෙදර)
  - **Phonetic Confusion**: Dental/Retroflex swaps (e.g., න/ණ, ල/ළ)
  - **Visual Reversal**: Shape confusion (e.g., බ/ඩ)
  - **Grammar Issues**: Colloquial to written form (e.g., යනව → යනවා)

### Technical Features

- **🔄 Hybrid Approach**: Combines AI with rule-based fallback for 100% reliability
- **🔒 Privacy-First**: Runs fully offline, zero data leakage
- **💾 Teacher Feedback Storage**: Save corrections to Supabase for model training
- **✏️ Re-correction Support**: Teachers can change their decisions
- **📝 All Words Editable**: Double-click any word to edit (not just errors)
- **📤 Training Data Export**: Export corrections as JSONL for fine-tuning

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Akura AI System                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   React     │───▶│   FastAPI   │───▶│  Ollama (LLaMA 8B)  │  │
│  │   Frontend  │    │   Backend   │    │    Fine-tuned       │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│         │                  │                                      │
│         ▼                  ▼                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │  Teacher    │───▶│  Supabase   │───▶│   Training Data     │  │
│  │  Feedback   │    │  Database   │    │   Export (JSONL)    │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai/) installed and running
- Supabase account (optional, for feedback storage)

### 1. Backend Setup

```bash
# Clone and enter directory
git clone https://github.com/25-26J-433-RP/ai-recorrection-workbench.git
cd ai-recorrection-workbench

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Pull the fine-tuned model
ollama pull hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M

# Copy and configure environment
copy .env.example .env  # Edit with your settings

# Start backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
# Enter frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 3. Verify Installation

- **Backend**: http://localhost:8000/docs (Swagger UI)
- **Frontend**: http://localhost:3000

---

## 🎨 Frontend Features

### Teacher's Cockpit

The React frontend provides an interactive workbench for teachers:

| Feature | Description |
|---------|-------------|
| **Text Input** | Enter or paste student essays |
| **OCR Upload** | Extract text from handwritten images |
| **Error Highlighting** | Color-coded error patterns |
| **Click to Review** | Click error words to accept/reject/edit |
| **Re-correction** | Click corrected words to change decision |
| **Double-click Edit** | Edit ANY word (not just errors) |
| **Save to Cloud** | Save corrections to Supabase database |
| **Copy Result** | Copy final corrected text |
| **Export Report** | Generate analysis report |

### Sample Texts Included

The frontend includes sample Sinhala texts with various dyslexia patterns for testing.

---

## 📡 API Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check with LLM status |
| `POST` | `/analyze` | Analyze text for errors |
| `GET` | `/patterns` | List detectable patterns |
| `POST` | `/ocr` | Extract text from image |

### Session Endpoints (Teacher Feedback)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sessions` | Create correction session |
| `GET` | `/sessions` | List all sessions |
| `GET` | `/sessions/{id}` | Get session with corrections |
| `PUT` | `/sessions/{id}` | Update session |
| `PATCH` | `/sessions/{id}/corrections/{id}` | Update word correction |
| `GET` | `/sessions/export/training-data` | Export as JSONL |

### Example: Analyze Text

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "මම ඉස්කොලෙට යනව. මකෙ පසල ලොකුඉ."}'
```

---

## 💾 Database Integration

### Setting up Supabase

1. Create a [Supabase](https://supabase.com) project
2. Run the migration script:

```sql
-- Run this in Supabase SQL Editor
-- Located at: migrations/feedback_tables.sql
```

3. Add connection string to `.env`:

```env
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
```

### Database Tables

| Table | Purpose |
|-------|---------|
| `correction_sessions` | Essay correction sessions |
| `word_corrections` | Individual word decisions |

---

## ☁️ Cloud Deployment (Azure / Request-Based)

For **cheap, request-based** deployment (Azure Container Apps, Google Cloud Run):

1. Set `LLM_PROVIDER=huggingface` in your `.env`
2. Add your [Hugging Face token](https://huggingface.co/settings/tokens):
   ```env
   HF_API_TOKEN=your_token_here
   HF_MODEL_ID=hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit
   ```
3. Deploy to Azure:
   - **Guide**: [docs/AZURE_DEPLOYMENT.md](docs/AZURE_DEPLOYMENT.md)
   - **PowerShell**: `$env:HF_API_TOKEN="your_token"; .\scripts\deploy-azure.ps1`
4. You pay **per request** for Hugging Face inference, no idle cost

**For local development** with Ollama:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `huggingface` | `huggingface` (request-based), `ollama` (local) |
| `HF_API_TOKEN` | - | Hugging Face token (required for `huggingface` provider) |
| `HF_MODEL_ID` | `hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit` | HF model ID |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL (local) |
| `OLLAMA_MODEL` | `hf.co/.../4bit:Q4_K_M` | Fine-tuned Ollama model |
| `OLLAMA_TIMEOUT` | `300` | Request timeout (seconds) |
| `DATABASE_URL` | - | Supabase PostgreSQL URL |
| `GEMINI_API_KEY` | - | For OCR feature (optional) |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |

---

## 📊 Dyslexia Pattern Types

| Pattern | % of Errors | Example |
|---------|-------------|---------|
| Visual Scrambling | 30% | ගෙරද → ගෙදර |
| Phonetic Confusion | 30% | න ↔ ණ, ල ↔ ළ |
| Grammar Issues | 20% | යනව → යනවා |
| Visual Reversal | 20% | බ ↔ ඩ |

---

## 📄 License

This project is part of the SLIIT Research Project (25-26J-433-RP).

---

<div align="center">

**Made with ❤️ for dyslexic students in Sri Lanka**

**© 2025**

</div>
