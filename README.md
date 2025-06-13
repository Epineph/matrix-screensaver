# Matrix Screensaver

A simple X11‐idle‐based screensaver that loops a captured video.
- After a short idle: normal loop.
- After a longer idle: rainbow hue filter.

## Installation

Run:

./install.sh

## Usage

- Place your `capture2.mp4` (or other file) next to `matrix_screensaver.py`
- Adjust thresholds via flags:  
  ```bash
  matrix_screensaver.py --first-threshold 600 --second-threshold 1800
