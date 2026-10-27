#!/bin/bash
# kali_claude.sh - Boot Kali Linux and launch Claude CLI
# Run as root or with sudo

set -e

echo "[claude_boot] Kali Linux - Claude CLI setup"

# Update and install Node.js if not present
if ! command -v node &>/dev/null; then
  echo "[claude_boot] Installing Node.js..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
fi

# Install Claude Code CLI
echo "[claude_boot] Installing Claude Code CLI..."
npm install -g @anthropic-ai/claude-code

echo "[claude_boot] Launching Claude..."
cd ~
claude
