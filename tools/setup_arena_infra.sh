#!/bin/bash
# setup_arena_infra.sh

echo "🏟️  Setting up Scrinium Liber Code Arena (SandboxFusion)..."

# 1. Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker could not be found. Please install Docker first."
    exit 1
fi

TOOLS_DIR="tools"
SANDBOX_DIR="$TOOLS_DIR/SandboxFusion"

# 2. Clone SandboxFusion if not exists
if [ ! -d "$SANDBOX_DIR" ]; then
    echo "📦 Cloning SandboxFusion from ByteDance..."
    git clone https://github.com/bytedance/SandboxFusion.git "$SANDBOX_DIR"
else
    echo "✅ SandboxFusion already cloned."
fi

# 3. Launch Docker Compose
echo "🚀 Launching Sandbox Server via Docker Compose..."
cd "$SANDBOX_DIR"

# Ensure we are using the right setup (they usually have a simple docker-compose or run script)
if [ -f "docker-compose.yml" ]; then
    docker-compose up -d
    echo "✅ SandboxFusion should be running on http://localhost:8000"
else
    echo "⚠️  docker-compose.yml not found in $SANDBOX_DIR. Please check the repository structure."
fi

cd ../..
echo "✅ Arena Infrastructure Setup Complete."
