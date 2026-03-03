#!/bin/bash
# Kytin Swarm: Princess Node (Jetson AGX Orin) Resource Fencing
# Purpose: Locks Ollama into a strict memory footprint to protect kytinOS and the Sting daemon.

echo "[*] Initiating Kytin Resource Fencing for Ollama..."

# 1. Ensure jetson-stats (jtop) is installed for hardware monitoring
if ! command -v jtop &> /dev/null
then
    echo "[*] Installing jetson-stats (jtop) for telemetry..."
    apt-get update
    apt-get install -y python3-pip
    pip3 install -U jetson-stats
    systemctl restart jetson_stats
fi

# 2. Define the Systemd Override Directory for Ollama
OLLAMA_SERVICE_DIR="/etc/systemd/system/ollama.service.d"
OVERRIDE_FILE="$OLLAMA_SERVICE_DIR/override.conf"

echo "[*] Configuring cgroup limits and environment variables..."
mkdir -p $OLLAMA_SERVICE_DIR

# 3. Write the strict Fencing Rules
# - MemoryMax: Hard caps the container/service RAM+VRAM usage (Adjust based on your Orin's total RAM)
# - OLLAMA_MAX_LOADED_MODELS: Prevents multiple models from stacking in VRAM.
# - OLLAMA_NUM_PARALLEL: Restricts concurrent batch processing to maintain low latency.
# - OLLAMA_FLASH_ATTENTION: Enables flash attention to drastically reduce KV cache memory.

cat <<EOF > $OVERRIDE_FILE
[Service]
# Hard Memory Fence (Set to 8GB to leave room for kytinOS and n8n on a 32GB/64GB Orin)
MemoryHigh=7G
MemoryMax=8G
MemorySwapMax=0B

# Environment Variable Fencing
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_QUEUE=5"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KEEP_ALIVE=5m" 
Environment="CUDA_VISIBLE_DEVICES=0"
EOF

# 4. Apply the configuration and restart the engine
echo "[*] Reloading systemd daemons..."
systemctl daemon-reload

echo "[*] Restarting Ollama with Kytin guardrails..."
systemctl restart ollama

# 5. Verify the service is running
if systemctl is-active --quiet ollama; then
    echo "[+] SUCCESS: The Princess node is fenced. Ollama is running safely."
else
    echo "[-] ERROR: Ollama failed to start. Check systemctl status ollama."
fi
