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

echo "⚡ Syncing Python environment and dependencies with uv..."
uv sync

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📌 Usage (Note: WireGuard network & firewall actions require root/sudo):"
echo ""
echo "To run the interactive CLI installer:"
echo "  sudo uv run wg-gaming-installer"
echo ""
echo "To launch the Web UI control panel:"
echo "  sudo uv run wg-gaming-web --host 0.0.0.0 --port 8000"
echo ""
