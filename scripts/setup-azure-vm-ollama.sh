#!/bin/bash
# Akura AI - Setup Ollama with Dual Models on Azure VM
# Run ON the Azure VM: bash setup-azure-vm-ollama.sh
# Prerequisites: Ollama already installed, Google account for secondary model

set -e

echo "=== Akura AI - Azure VM Ollama Setup (Dual Model) ==="
echo ""

# 1. Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "[1/5] Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "[1/5] Ollama already installed: $(ollama --version)"
fi

# 2. Configure Ollama to listen on all interfaces
echo "[2/5] Configuring Ollama to listen on 0.0.0.0..."
sudo mkdir -p /etc/systemd/system/ollama.service.d
cat <<EOF | sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"
EOF
sudo systemctl daemon-reload
sudo systemctl restart ollama

# 3. Wait for Ollama to be ready
echo "[3/5] Waiting for Ollama to start..."
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
echo "[4/5] Pulling Akura model..."
if ollama list | grep -q "akura_ai_sinhala_dyslexic_word_corrector_4bit"; then
    echo "  Akura model already present."
else
    ollama pull hf.co/hasinduOnline/akura_ai_sinhala_dyslexic_word_corrector_4bit:Q4_K_M
    echo "  Akura model pulled."
fi

# 5. Pull secondary model (requires Google sign-in)
echo "[5/5] Pulling secondary model (gemini-3-flash-preview)..."
if ollama list | grep -q "gemini-3-flash-preview"; then
    echo "  Secondary model already present."
else
    echo "  > You need to authenticate with Google first."
    echo "  > Running: ollama signin google"
    echo "  > Follow the browser/URL instructions to authenticate."
    echo ""
    ollama signin google
    echo ""
    ollama pull gemini-3-flash-preview:latest
    echo "  Secondary model pulled."
fi

sudo systemctl enable ollama

echo ""
echo "=== Setup Complete (Models Only) ==="
echo ""
echo "This VM only hosts Ollama models."
echo "The FastAPI backend runs on GCP Cloud Run."
echo ""
echo "Models available:"
ollama list
echo ""
echo "Service:"
echo "  Ollama:  sudo systemctl status ollama"
echo ""
echo "Endpoint:"
echo "  Ollama API: http://$(hostname -I | awk '{print $1}'):11434"
echo ""
echo "IMPORTANT: Make sure Azure NSG allows inbound on port 11434 only."
echo "  az network nsg rule create --resource-group AKURA-AI-RG --nsg-name akura-ai-vmNSG \\"
echo "    --name AllowOllama --priority 1010 --destination-port-ranges 11434 \\"
echo "    --access Allow --protocol Tcp --direction Inbound"
echo ""
