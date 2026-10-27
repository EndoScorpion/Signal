#!/bin/bash
# ubuntu_claude.sh - Boot Ubuntu and launch Claude CLI
# Run as your user (sudo for apt steps)

set -e

echo "[claude_boot] Ubuntu - Claude CLI setup"

# Install Node.js if not present
if ! command -v node &>/dev/null; then
  echo "[claude_boot] Installing Node.js..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
  sudo apt-get install -y nodejs
fi

# Install Claude Code CLI
echo "[claude_boot] Installing Claude Code CLI..."
npm install -g @anthropic-ai/claude-code

echo "[claude_boot] Launching Claude..."
cd ~
claude
