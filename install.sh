#!/usr/bin/env bash
#set -euo pipefail

usage() {
  cat << EOF
install.sh — install Matrix-Screensaver

Usage: ./install.sh [--help]

Options:
  -h, --help    Show this message

This will:
  • pacman -S xprintidle ffmpeg
  • Copy matrix_screensaver.py → ~/.local/bin & /usr/local/bin/matrix-screensave
  • Fix ownership & perms on /usr/local/bin
  • Install a corrected systemd --user unit
EOF
  exit 0
}
[[ "${1-}" =~ ^(-h|--help)$ ]] && usage

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_BIN="$HOME/.local/bin"
USR_BIN="/usr/local/bin"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE="$SERVICE_DIR/matrix-screensaver.service"

echo "1) Installing dependencies…"
sudo pacman -Syu --noconfirm --needed xprintidle ffmpeg

echo "2) Installing python script…"
install -d "$LOCAL_BIN"
install -m 755 "$SCRIPT_DIR/matrix_screensaver.py" \
               "$LOCAL_BIN/matrix_screensaver.py"

echo "3) Installing CLI wrapper…"
sudo install -m 755 "$SCRIPT_DIR/matrix_screensaver.py" \
                  "$USR_BIN/matrix-screensave"
echo "   Fixing ownership & perms on $USR_BIN…"
sudo chown "$USER": "$USR_BIN" -R
sudo chmod 777  "$USR_BIN" -R

echo "4) Writing systemd --user service…"
mkdir -p "$SERVICE_DIR"
cat > "$SERVICE" << EOF
[Unit]
Description=Matrix Screensaver

[Service]
Type=simple
ExecStart=%h/.local/bin/matrix_screensaver.py
Restart=always
# Ensure the script sees your X display
Environment=DISPLAY=$DISPLAY
Environment=XAUTHORITY=%h/.Xauthority

[Install]
WantedBy=default.target
EOF

echo "5) Enabling service…"
systemctl --user daemon-reload
systemctl --user enable --now matrix-screensaver.service

echo "✅ Done. You can check its status with:"
echo "   systemctl --user status matrix-screensaver.service"
