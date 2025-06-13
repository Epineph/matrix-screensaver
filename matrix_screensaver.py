#!/usr/bin/env python3
"""
matrix_screensaver.py

A simple X11‐idle‐based “screensaver” that loops your captured video.
– After FIRST_THRESHOLD seconds of idle, play normal.
– After SECOND_THRESHOLD seconds of continual idle, restart with a rainbow hue filter.

Dependencies:
  - python3
  - python3-xlib   (for XScreenSaverQueryInfo)
  - ffmpeg         (provides ffplay)
"""

import argparse
import subprocess
import time
import signal
import sys

from Xlib import display
from Xlib.ext import screensaver

def get_idle_ms(disp, root):
    """
    Query the X server for the current idle time in milliseconds.
    Uses the XScreenSaver extension.
    """
    info = screensaver.QueryInfo(disp, root)
    return info.idle

def start_player(cmd):
    """
    Launches ffplay with the given command list.
    Returns the Popen object so we can terminate it later.
    """
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def kill_player(proc):
    """
    Gracefully terminate the ffplay process.
    """
    if proc and proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()

def main():
    parser = argparse.ArgumentParser(
        description="Idle‐based video screensaver with optional rainbow effect."
    )
    parser.add_argument(
        "-v", "--video",
        default="capture2.mp4",
        help="Path to your captured video file."
    )
    parser.add_argument(
        "--first-threshold",
        type=int,
        default=300,
        help="Seconds of idle before starting the normal loop (default: 300s)."
    )
    parser.add_argument(
        "--second-threshold",
        type=int,
        default=3600,
        help="Seconds of idle before restarting with rainbow filter (default: 3600s)."
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="How often (in seconds) to poll X idle time."
    )
    args = parser.parse_args()

    # ffplay command lines
    normal_cmd = [
        "ffplay", "-nodisp",    # no window decorations
        "-loop", "0",           # infinite loop
        "-fs",                  # full-screen
        "-hide_banner", "-loglevel", "quiet",
        args.video
    ]
    rainbow_cmd = [
        "ffplay", "-nodisp",
        "-loop", "0",
        "-fs",
        "-hide_banner", "-loglevel", "quiet",
        "-vf", "hue=h=2*t:s=2", # hue shift & saturation boost
        args.video
    ]

    # Connect to X11
    disp = display.Display()
    root = disp.screen().root

    player_proc = None
    mode = "off"  # off → normal → rainbow

    try:
        while True:
            idle_ms = get_idle_ms(disp, root)
            idle_s = idle_ms / 1000.0

            if idle_s >= args.second_threshold:
                if mode != "rainbow":
                    kill_player(player_proc)
                    player_proc = start_player(rainbow_cmd)
                    mode = "rainbow"
            elif idle_s >= args.first_threshold:
                if mode != "normal":
                    kill_player(player_proc)
                    player_proc = start_player(normal_cmd)
                    mode = "normal"
            else:
                if mode != "off":
                    kill_player(player_proc)
                    player_proc = None
                    mode = "off"

            time.sleep(args.poll_interval)

    except KeyboardInterrupt:
        kill_player(player_proc)
        sys.exit(0)

if __name__ == "__main__":
    main()
