# -*- coding: utf-8 -*-
"""Step 0 - check everything the cypher pipeline needs and print exactly what is missing.

usage: python scripts/setup_check.py
"""
import importlib.util
import os
import shutil
import subprocess
import sys

ok = True
print("python", sys.version.split()[0], "->", sys.executable)
if sys.version_info < (3, 9):
    print("  ! Python 3.9+ needed")
    ok = False
if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
    print("  ! ffmpeg / ffprobe not on PATH (Windows: winget install Gyan.FFmpeg | macOS: brew install ffmpeg)")
    ok = False
else:
    print(subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.split("\n")[0])
    if "tpad" not in subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout:
        print("  ! this ffmpeg has no tpad filter - install a full build")
        ok = False
need = {"numpy": "numpy", "scipy": "scipy", "soundfile": "soundfile", "PIL": "pillow",
        "demucs": "demucs", "faster_whisper": "faster-whisper"}
miss = [p for m, p in need.items() if importlib.util.find_spec(m) is None]
if miss:
    ok = False
    print("  ! missing:", " ".join(miss), "->", sys.executable, "-m pip install", " ".join(miss),
          "(first run also downloads ~2 GB of models)")
print("MINIMAX_API_KEY:", "set" if os.environ.get("MINIMAX_API_KEY") else "NOT set (needed for H3 and image-01)")
print("MINIMAX_API_BASE:", os.environ.get("MINIMAX_API_BASE", "(default https://api.minimax.io; China keys need https://api.minimaxi.com)"))
print("\nREADY" if ok else "\nNOT READY - fix the lines marked !")
print("Also needed: a Suno account and a Midjourney account. The brush font is downloaded from GitHub on first use "
      "(set HTTPS_PROXY in mainland China).")
