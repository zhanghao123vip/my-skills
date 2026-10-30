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
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
try:
    import _lib
    print("ancient-rap-battle skill:", _lib.ARB)
except SystemExit as ex:
    print("  !", ex)
    ok = False

print("python", sys.version.split()[0], "->", sys.executable)
if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
    print("  ! ffmpeg / ffprobe not on PATH")
    ok = False
else:
    flt = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    print("ffmpeg OK" + ("" if "tpad" in flt else "  (! no tpad filter - update ffmpeg)"))
need = {"numpy": "numpy", "scipy": "scipy", "soundfile": "soundfile", "PIL": "pillow",
        "demucs": "demucs", "faster_whisper": "faster-whisper"}
miss = [p for m, p in need.items() if importlib.util.find_spec(m) is None]
if miss:
    ok = False
    print("  ! missing:", " ".join(miss), "->", sys.executable, "-m pip install", " ".join(miss))
print("MINIMAX_API_KEY:", "set" if os.environ.get("MINIMAX_API_KEY") else "NOT set (needed for H3 and image-01)")
print("MINIMAX_API_BASE:", os.environ.get("MINIMAX_API_BASE", "(default https://api.minimax.io; China keys need https://api.minimaxi.com)"))
print("\nREADY" if ok else "\nNOT READY - fix the lines marked !")
