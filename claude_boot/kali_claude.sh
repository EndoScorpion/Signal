#!/bin/bash
# Claude CLI autostart for Kali Linux (Ventoy live boot)
# Place this file on the Ventoy USB at D:\claude_boot\kali_claude.sh
# Run after booting: bash /cdrom/claude_boot/kali_claude.sh
#   (Ventoy mounts the USB at /cdrom in Kali live)

set -e

echo "=== Claude CLI Setup for Kali Live ==="

# Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    apt-get update -qq
    apt-get install -y -qq nodejs npm
fi

# Install claude CLI
if ! command -v claude &> /dev/null; then
    echo "Installing Claude CLI..."
    npm install -g @anthropic-ai/claude-code
fi

# Load API key from key.txt on USB (Ventoy mounts at /cdrom)
KEY_FILE="/cdrom/claude_boot/key.txt"
if [ -f "$KEY_FILE" ]; then
    export ANTHROPIC_API_KEY=$(cat "$KEY_FILE" | tr -d '[:space:]')
    echo "API key loaded from key.txt"
else
    echo "ERROR: No key.txt found at $KEY_FILE"
    echo "Create D:\\claude_boot\\key.txt on the USB with your ANTHROPIC_API_KEY"
    read -p "Or enter ANTHROPIC_API_KEY manually: " ANTHROPIC_API_KEY
    export ANTHROPIC_API_KEY
fi

echo "Launching Claude CLI..."
claude
