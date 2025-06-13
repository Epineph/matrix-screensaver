#!/usr/bin/env bash
set -euo pipefail

# Directory of this script
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Install dependencies (Arch Linux)
echo "Installing dependencies..."
sudo pacman -Syu --noconfirm python-xlib ffmpeg

# 2. Install the Python script
echo "Installing screensaver script to ~/.local/bin..."
install -d ~/.local/bin
install -m 755 "$dir/matrix_screensaver.py" ~/.local/bin/matrix_screensaver.py

# 3. Create systemd user service
echo "Setting up systemd user service..."
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/matrix-screensaver.service << 'SERVICE'
[Unit]
Description=Matrix Screensaver

[Service]
Type=simple
ExecStart=%h/.local/bin/matrix_screensaver.py
Restart=always

[Install]
WantedBy=default.target
SERVICE

# 4. Enable & start service
systemctl --user daemon-reload
systemctl --user enable --now matrix-screensaver.service

echo "✅ Installation complete. The Matrix Screensaver will start on login."

