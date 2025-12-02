# 🧠 Akura AI - Intelligent Dyslexia Correction Engine

<div align="center">

![Akura AI](https://img.shields.io/badge/Akura%20AI-Dyslexia%20Correction-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal?style=for-the-badge&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-Enabled-purple?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange?style=for-the-badge)

**A specialized, privacy-focused API for detecting and correcting Sinhala writing errors specific to dyslexic students.**

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Configuration](#-configuration)

---

## ✨ Features

### Core Capabilities

- **🤖 AI-Powered Correction**: Uses LangChain with Ollama (llama3.2:1b) for context-aware corrections
- **📊 Pattern Detection**: Identifies 4 specific dyslexia patterns:
  - **Visual Scrambling**: Letter reordering (e.g., ගෙරද → ගෙදර)
  - **Phonetic Confusion**: Dental/Retroflex swaps (e.g., න/ණ, ල/ළ)
  - **Visual Reversal**: Shape confusion (e.g., බ/ඩ)
  - **Grammar Issues**: Colloquial to written form (e.g., යනව → යනවා)

### Technical Features

- **🔄 Hybrid Approach**: Combines AI with rule-based fallback for 100% reliability
- **📡 Intelligent Diff**: Custom SequenceMatcher algorithm for detailed error analysis
- **🔒 Privacy-First**: Runs fully offline, zero data leakage
- **⚡ High Performance**: Async processing with FastAPI
- **🐳 Container-Ready**: Docker and Docker Compose support
- **📝 Full API Documentation**: OpenAPI/Swagger docs included

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Akura AI Backend                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   FastAPI   │───▶│  LangChain  │───▶│  Ollama (llama3.2)  │  │
│  │   Server    │    │   Service   │    │    Local LLM        │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │  Analysis   │───▶│   Pattern   │───▶│   Rule-Based        │  │
│  │  Service    │    │  Detector   │    │   Corrector         │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) installed and running
- Docker (optional, for containerized deployment)

### Option 1: Local Development

```bash
# Clone the repository
git clone https://github.com/25-26J-433-RP/ai-recorrection-workbench.git
cd ai-recorrection-workbench

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Pull the Ollama model
ollama pull llama3.2:1b

# Copy environment file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker Compose

```bash
# Start all services (API + Ollama)
docker-compose up -d

# Initialize the model (run once)
docker-compose run model-init

# View logs
docker-compose logs -f akura-api
```

### Verify Installation

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Test analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "මම ගෙරද යනව"}'
```

---

## 📡 API Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### `POST /analyze`
Analyze Sinhala text for dyslexic writing errors.

**Request:**
```json
{
  "text": "මම ගෙරද යනව",
  "include_correct_words": false
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "word": "ගෙරද",
      "type": "error",
      "dyslexiaPattern": "Visual Sequencing (Scrambled)",
      "suggestion": "ගෙදර",
      "explanation": "Letters appear scrambled. Common visual sequencing error.",
      "confidence": 0.95,
      "source": "hybrid"
    },
    {
      "word": "යනව",
      "type": "error",
      "dyslexiaPattern": "Grammar (Spoken vs Written)",
      "suggestion": "යනවා",
      "explanation": "Incomplete verb ending.",
      "confidence": 0.90,
      "source": "rule-based"
    }
  ],
  "correctedText": "මම ගෙදර යනවා",
  "originalText": "මම ගෙරද යනව",
  "processingTimeMs": 245.5,
  "modelUsed": "llama3.2:1b"
}
```

#### `POST /analyze/batch`
Analyze multiple texts in a single request.

**Request:**
```json
{
  "texts": [
    "මම ගෙරද යනව",
    "මම පාසැල යනවා"
  ]
}
```

#### `POST /check`
Quick check if text contains any errors.

**Response:**
```json
{
  "success": true,
  "has_errors": true,
  "text": "මම ගෙරද යනව"
}
```

#### `GET /health`
Check API and LLM health status.

#### `GET /patterns`
List all detectable dyslexia patterns.

#### `GET /corrections`
List all known word corrections.

#### `GET /config`
Get current API configuration.

---

## 💻 Development

### Project Structure

```
ai-recorrection-workbench/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoint definitions
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Application configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic data models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py # Main orchestration service
│   │   ├── llm_service.py      # LangChain + Ollama integration
│   │   ├── pattern_detector.py # Dyslexia pattern detection
│   │   └── rule_corrector.py   # Rule-based fallback system
│   └── utils/
│       ├── __init__.py
│       └── sinhala_mappings.py # Character mappings & dictionaries
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_pattern_detector.py
│   └── test_rule_corrector.py
├── Dockerfile
├── Dockerfile.dev
├── docker-compose.yml
├── docker-compose.dev.yml
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

### Running in Development Mode

```bash
# With hot-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with Docker
docker-compose -f docker-compose.dev.yml up
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_pattern_detector.py -v

# Run specific test
pytest tests/test_api.py::TestAnalyzeEndpoint::test_analyze_simple_text -v
```

---

## 🚢 Deployment

### Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Select "Docker" as the SDK
3. Push the repository to the Space
4. The API will be available at `https://<space-name>.hf.space`

### Production Docker

```bash
# Build production image
docker build -t akura-ai:latest .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e ENVIRONMENT=production \
  akura-ai:latest
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Enable debug mode |
| `ENVIRONMENT` | `production` | Environment name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2:1b` | Model to use |
| `OLLAMA_TIMEOUT` | `120` | Request timeout (seconds) |
| `MODEL_TEMPERATURE` | `0.3` | Model temperature |
| `MODEL_MAX_TOKENS` | `512` | Max tokens to generate |
| `AI_CONFIDENCE_THRESHOLD` | `0.7` | Threshold for AI corrections |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |

---

## 📊 Dyslexia Pattern Types

### 1. Visual Scrambling (30% of errors)
Letters appear in wrong order due to visual sequencing difficulties.
```
ගෙරද → ගෙදර
```

### 2. Phonetic Confusion (30% of errors)
Confusion between similar-sounding consonants.
```
Dental vs Retroflex:
- න ↔ ණ
- ල ↔ ළ
- ද ↔ ඩ
- ත ↔ ට
```

### 3. Grammar/Colloquialisms (20% of errors)
Spoken forms used instead of written forms.
```
යනව → යනවා
මං → මම
```

### 4. Visual Reversal (Shape Confusion)
Confusion between visually similar characters.
```
බ ↔ ඩ
```

---

## 🔮 Future Enhancements

- [ ] **Federated Learning**: Anonymous data collection for model improvement
- [ ] **Multi-Language Support**: Tamil and English dyslexia correction
- [ ] **Fine-Tuned Model**: Custom SLM trained on dyslexia-specific data
- [ ] **Teacher Dashboard**: Web interface for correction review
- [ ] **Student Analytics**: Progress tracking over time

---

## 📄 License

This project is part of the SLIIT Research Project (25-26J-433-RP).

---

<div align="center">

**Made with ❤️ for dyslexic students in Sri Lanka**

</div>