#!/bin/bash
# Akura AI - Setup Ollama with Dual Models on Azure VM
# Run ON the Azure VM: bash setup-azure-vm-ollama.sh
# Prerequisites: Ollama already installed, Google account for secondary model

set -e

echo "=== Akura AI - Azure VM Ollama Setup (Dual Model) ==="
echo ""

# 1. Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "[1/6] Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "[1/6] Ollama already installed: $(ollama --version)"
fi

# 2. Configure Ollama to listen on all interfaces
echo "[2/6] Configuring Ollama to listen on 0.0.0.0..."
sudo mkdir -p /etc/systemd/system/ollama.service.d
cat <<EOF | sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"
EOF
sudo systemctl daemon-reload
sudo systemctl restart ollama

# 3. Wait for Ollama to be ready
echo "[3/6] Waiting for Ollama to start..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "  Ollama is ready."
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "  ERROR: Ollama failed to start after 60s"
        exit 1
    fi
    sleep 2
done

# 4. Pull Akura model
echo "[4/6] Pulling Akura model..."
if ollama list | grep -q "akura_ai_sinhala_dyslexic_word_corrector_4bit"; then
    echo "  Akura model already present."
else
    ollama pull hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M
    echo "  Akura model pulled."
fi

# 5. Pull secondary model (requires Google login)
echo "[5/6] Pulling secondary model (gemini-3-flash-preview)..."
if ollama list | grep -q "gemini-3-flash-preview"; then
    echo "  Secondary model already present."
else
    echo "  > You need to authenticate with Google first."
    echo "  > Running: ollama login google"
    echo "  > Follow the browser/URL instructions to authenticate."
    echo ""
    ollama login google
    echo ""
    ollama pull gemini-3-flash-preview:latest
    echo "  Secondary model pulled."
fi

# 6. Set up the Python app environment
echo "[6/6] Setting up Python app environment..."
APP_DIR="/home/$(whoami)/akura-ai"
mkdir -p "$APP_DIR"

if [ ! -d "$APP_DIR/venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv "$APP_DIR/venv"
fi

if [ -f "$APP_DIR/requirements.txt" ]; then
    echo "  Installing Python dependencies..."
    source "$APP_DIR/venv/bin/activate"
    pip install -r "$APP_DIR/requirements.txt" -q
    deactivate
fi

# Create/update systemd service for the API
echo "  Setting up akura-ai systemd service..."
cat <<EOF | sudo tee /etc/systemd/system/akura-ai.service > /dev/null
[Unit]
Description=Akura AI Recorrection API
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable akura-ai
sudo systemctl enable ollama

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Models available:"
ollama list
echo ""
echo "Services:"
echo "  Ollama:    sudo systemctl status ollama"
echo "  Akura AI:  sudo systemctl status akura-ai"
echo ""
echo "Endpoints:"
echo "  Ollama API: http://$(hostname -I | awk '{print $1}'):11434"
echo "  Akura API:  http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "IMPORTANT: Make sure Azure NSG allows inbound on ports 8000 and 11434."
echo "  az network nsg rule create --resource-group <RG> --nsg-name <NSG> \\"
echo "    --name AllowOllama --priority 1010 --destination-port-ranges 11434 \\"
echo "    --access Allow --protocol Tcp --direction Inbound"
echo ""
