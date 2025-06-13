#!/usr/bin/env python3
"""
matrix_screensaver.py

Idle-based video screensaver:
- Normal loop after first threshold
- Rainbow hue filter after second threshold

Usage:
  matrix_screensaver.py [options]

Dependencies:
  - ffplay (from ffmpeg)
  - xprintidle  # for reliable idle detection
"""

import argparse
import subprocess
import time
import signal
import sys

# Try to import Xlib only as a fallback
try:
    from Xlib import display
    from Xlib.ext import screensaver
    _have_xlib = True
except ImportError:
    _have_xlib = False

def get_idle_ms():
    """
    Return idle time in milliseconds.
    First try xprintidle; otherwise fallback to XScreenSaver.
    """
    # 1) Try xprintidle
    try:
        out = subprocess.check_output(['xprintidle'])
        return int(out)
    except Exception:
        pass

    # 2) Fallback to Xlib
    if not _have_xlib:
        sys.stderr.write("Error: need xprintidle or python-xlib\n")
        sys.exit(1)
    disp = display.Display()
    root = disp.screen().root
    info = screensaver.QueryInfo(disp, root)
    return info.idle

def start_player(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def kill_player(proc):
    if proc and proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()

def parse_args():
    p = argparse.ArgumentParser(
        description="Idle‐based video screensaver with optional rainbow effect.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  {0} --first-threshold 600 --second-threshold 1800\n"
            "  {0} --video demo.mp4\n"
        ).format(__file__)
    )
    p.add_argument("-v","--video",         default="capture2.mp4",
                   help="Path to video file")
    p.add_argument("--first-threshold",   type=int, default=300,
                   help="Idle seconds before normal loop (default:300)")
    p.add_argument("--second-threshold",  type=int, default=3600,
                   help="Idle seconds before rainbow loop (default:3600)")
    p.add_argument("--poll-interval",      type=float, default=1.0,
                   help="Seconds between idle checks")
    return p.parse_args()

def main():
    args = parse_args()

    normal_cmd = [
        "ffplay","-nodisp","-loop","0","-fs",
        "-hide_banner","-loglevel","quiet",
        args.video
    ]
    rainbow_cmd = normal_cmd + ["-vf","hue=h=2*t:s=2"]

    player = None
    mode = "off"

    try:
        while True:
            idle_s = get_idle_ms() / 1000.0

            if idle_s >= args.second_threshold and mode != "rainbow":
                kill_player(player)
                player = start_player(rainbow_cmd)
                mode = "rainbow"

            elif idle_s >= args.first_threshold and mode != "normal":
                kill_player(player)
                player = start_player(normal_cmd)
                mode = "normal"

            elif idle_s < args.first_threshold and mode != "off":
                kill_player(player)
                player = None
                mode = "off"

            time.sleep(args.poll_interval)

    except KeyboardInterrupt:
        kill_player(player)
        sys.exit(0)

if __name__=="__main__":
    main()
