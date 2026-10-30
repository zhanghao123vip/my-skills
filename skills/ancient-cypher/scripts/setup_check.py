# -*- coding: utf-8 -*-
"""Step 0 - check everything the cypher pipeline needs and print exactly what is missing.

usage: python scripts/setup_check.py                 # check
       python scripts/setup_check.py --install-arb   # also clone the ancient-rap-battle skill (MIT) next to this one
In mainland China git needs a proxy for github.com, e.g. set HTTPS_PROXY=http://127.0.0.1:<port> first.
"""
import importlib.util
import os
import shutil
import subprocess
import sys

ARB_REPO = "https://github.com/10291124jcjc-dotcom/ancient-rap-battle.git"
here = os.path.dirname(os.path.abspath(__file__))
skills_dir = os.path.dirname(os.path.dirname(here))       # .../skills/ancient-cypher/scripts -> .../skills

if "--install-arb" in sys.argv:
    dst = os.path.join(skills_dir, "ancient-rap-battle")
    if os.path.exists(os.path.join(dst, "scripts", "h3run.py")):
        print("ancient-rap-battle already installed:", dst)
    elif not shutil.which("git"):
        sys.exit("git not found - download %s and unzip it to %s" % (ARB_REPO[:-4], dst))
    else:
        print("cloning", ARB_REPO, "->", dst)
        if subprocess.run(["git", "clone", "--depth", "1", ARB_REPO, dst]).returncode != 0:
            sys.exit("clone failed (network? in China set HTTPS_PROXY first)")

ok = True
sys.path.insert(0, here)
try:
    import _lib
    print("ancient-rap-battle skill:", _lib.ARB)
except SystemExit as ex:
    print("  !", ex, "\n    or run: python %s --install-arb" % os.path.relpath(__file__))
    ok = False

print("python", sys.version.split()[0], "->", sys.executable)
if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
    print("  ! ffmpeg / ffprobe not on PATH (Windows: winget install Gyan.FFmpeg | macOS: brew install ffmpeg)")
    ok = False
else:
    ver = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.split("\n")[0]
    flt = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    print(ver)
    if "tpad" not in flt:
        print("  ! this ffmpeg has no tpad filter - install a full build")
        ok = False
need = {"numpy": "numpy", "scipy": "scipy", "soundfile": "soundfile", "PIL": "pillow",
        "demucs": "demucs", "faster_whisper": "faster-whisper"}
miss = [p for m, p in need.items() if importlib.util.find_spec(m) is None]
if miss:
    ok = False
    print("  ! missing:", " ".join(miss), "->", sys.executable, "-m pip install", " ".join(miss))
print("MINIMAX_API_KEY:", "set" if os.environ.get("MINIMAX_API_KEY") else "NOT set (needed for H3 and image-01)")
print("MINIMAX_API_BASE:", os.environ.get("MINIMAX_API_BASE", "(default https://api.minimax.io; China keys need https://api.minimaxi.com)"))
print("\nREADY" if ok else "\nNOT READY - fix the lines marked !")
