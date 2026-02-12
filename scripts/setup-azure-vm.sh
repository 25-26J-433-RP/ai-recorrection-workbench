#!/bin/bash
# ===========================================================
# Akura AI - Azure VM Setup Script
# Run this ON THE VM after SSH-ing in
# ===========================================================
set -e

echo "=== Akura AI Azure VM Setup ==="
echo ""

# 1. Update system
echo "[1/6] Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker
echo "[2/6] Installing Docker..."
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 3. Install Ollama
echo "[3/6] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# 4. Pull the fine-tuned model
echo "[4/6] Pulling Akura AI model (this may take 5-10 min)..."
ollama pull hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M

# 5. Clone and setup the app
echo "[5/6] Setting up the application..."
if [ ! -d "/home/$USER/akura-ai" ]; then
    git clone https://github.com/YOUR_GITHUB_USERNAME/ai-recorrection-workbench.git /home/$USER/akura-ai
fi
cd /home/$USER/akura-ai

# Create .env for production (Ollama mode)
cat > .env << 'ENVEOF'
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
ENVIRONMENT=production

# Use Ollama (running on same VM)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M
OLLAMA_TIMEOUT=300

# Model
MODEL_TEMPERATURE=0.3
MODEL_MAX_TOKENS=2048
AI_CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS - update with your frontend URL
ALLOWED_ORIGINS=*
ENVEOF

# 6. Build and run with Docker
echo "[6/6] Building and starting the app..."
sudo docker build -t akura-ai .
sudo docker run -d \
    --name akura-ai \
    --restart unless-stopped \
    --network host \
    --env-file .env \
    -p 8000:8000 \
    akura-ai

echo ""
echo "=========================================="
echo "Setup complete!"
echo ""
echo "Ollama: http://localhost:11434"
echo "API:    http://$(curl -s ifconfig.me):8000"
echo "Docs:   http://$(curl -s ifconfig.me):8000/docs"
echo "=========================================="
