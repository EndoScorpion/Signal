#!/bin/bash
# Claude Rescue USB First-Boot Setup
# Xubuntu 22.04 LTS — installs Node 20, Claude CLI, Firefox + Tampermonkey + Claude Field Colors
# Run: bash /cdrom/ubuntu_claude_setup.sh

set -e
echo "=== Claude Rescue USB Setup ==="

echo "[1/7] Updating apt..."
sudo apt-get update -qq

echo "[2/7] Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - -q
sudo apt-get install -y nodejs -qq
node --version && npm --version

echo "[3/7] Installing @anthropic-ai/claude-code..."
sudo npm install -g @anthropic-ai/claude-code

echo "[4/7] Installing git, python3, pip..."
sudo apt-get install -y git python3-pip -qq
pip3 install --quiet numpy scipy pandas yfinance

echo "[5/7] Installing Firefox..."
if command -v snap >/dev/null 2>&1; then
    sudo snap install firefox 2>/dev/null || sudo apt-get install -y firefox -qq
else
    sudo apt-get install -y firefox -qq
fi

echo "[6/7] Installing Tampermonkey for Firefox..."
sudo apt-get install -y wget -qq
FF_PROFILE_DIR="$HOME/.mozilla/firefox"
mkdir -p "$FF_PROFILE_DIR"
timeout 5 firefox --headless --no-remote --profile "$FF_PROFILE_DIR/rescue" about:blank 2>/dev/null || true
PROFILE=$(find "$FF_PROFILE_DIR" -maxdepth 1 -type d | grep -v "^$FF_PROFILE_DIR$" | head -1)
if [ -z "$PROFILE" ]; then PROFILE="$FF_PROFILE_DIR/rescue"; mkdir -p "$PROFILE"; fi
EXTENSIONS_DIR="$PROFILE/extensions"
mkdir -p "$EXTENSIONS_DIR"
TM_XPI="$EXTENSIONS_DIR/{137e907a-fe48-4952-9cf6-8ca0de5965c8}.xpi"
wget -q -O "$TM_XPI" "https://addons.mozilla.org/firefox/downloads/latest/tampermonkey/latest.xpi" || \
    echo "WARNING: Tampermonkey XPI download failed — install manually from addons.mozilla.org"

echo "[7/7] Installing Claude Field Colors userscript..."
SCRIPTS_DIR="$HOME/.tampermonkey_scripts"
mkdir -p "$SCRIPTS_DIR"
SCRIPT_SRC="/cdrom/claude_field_colors.user.js"
SCRIPT_DEST="$SCRIPTS_DIR/claude_field_colors.user.js"
if [ -f "$SCRIPT_SRC" ]; then
    cp "$SCRIPT_SRC" "$SCRIPT_DEST"
else
    cat > "$SCRIPT_DEST" << 'USERSCRIPT'
// ==UserScript==
// @name         Claude Field Colors
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Color-codes Claude input fields
// @author       EndoScorpion
// @match        https://claude.ai/*
// @grant        none
// ==/UserScript==
(function() {
    'use strict';
    const style = document.createElement('style');
    style.textContent = `
        [contenteditable="true"], textarea {
            background: #0d1117 !important;
            color: #39ff14 !important;
            border: 1px solid #39ff14 !important;
            caret-color: #39ff14 !important;
        }
        button[type="submit"], button[aria-label*="Send"] {
            background: #39ff14 !important;
            color: #000 !important;
        }
    `;
    document.head.appendChild(style);
})();
USERSCRIPT
fi

echo ""
echo "=== SETUP COMPLETE ==="
echo "Run: claude"
echo "Firefox + Tampermonkey installed."
echo "Field Colors script: $SCRIPT_DEST"
echo "Drag-drop the .user.js into Firefox to install via Tampermonkey."
