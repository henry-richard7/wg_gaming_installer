#!/usr/bin/env bash
# Quick Setup script for WireGuard Gaming Manager (using uv)

set -e

echo "🎮 WireGuard Gaming Manager - Quick Setup"
echo "=========================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 'uv' package manager not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Ensure root/sudo can locate uv by symlinking to /usr/local/bin if needed
if [ -f "$HOME/.cargo/bin/uv" ] && [ ! -f "/usr/local/bin/uv" ]; then
    echo "🔗 Symlinking uv to /usr/local/bin for sudo access..."
    sudo ln -sf "$HOME/.cargo/bin/uv" /usr/local/bin/uv 2>/dev/null || true
fi

echo "⚡ Syncing Python environment and dependencies with uv..."
uv sync

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📌 Recommended Workflow:"
echo ""
echo "Step 1: Initialize server configuration (First time only):"
echo "  sudo $(which uv) run wg-gaming-installer"
echo ""
echo "Step 2: Launch the Web UI control panel:"
echo "  sudo $(which uv) run wg-gaming-web --host 0.0.0.0 --port 8000"
echo ""
