# -*- coding: utf-8 -*-
"""Shared helpers: find the ancient-rap-battle skill (its H3 runner, lip check, beat grid and text styles are reused),
load episode.json, paths."""
import json
import os
import subprocess
import sys

CANDIDATES = [os.environ.get("ARB_SKILL_DIR", ""),
              os.path.expanduser("~/.claude/skills/ancient-rap-battle"),
              os.path.expanduser("~/.codex/skills/ancient-rap-battle")]


def arb_dir():
    for d in CANDIDATES:
        if d and os.path.exists(os.path.join(d, "scripts", "h3run.py")):
            return d
    sys.exit("ancient-rap-battle skill not found: install it from "
             "https://github.com/10291124jcjc-dotcom/ancient-rap-battle or set ARB_SKILL_DIR")


ARB = arb_dir()
ARB_SCRIPTS = os.path.join(ARB, "scripts")
if ARB_SCRIPTS not in sys.path:
    sys.path.insert(0, ARB_SCRIPTS)


def P(ep, *parts):
    return os.path.join(ep, *parts)


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def jsave(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def episode(ep):
    p = P(ep, "episode.json")
    if not os.path.exists(p):
        sys.exit("no episode.json in %s - copy examples/wo-ye-ka-guo/episode.json and edit it" % ep)
    return jload(p)


def ref(ep, key):
    """reference image by key: refs/<key>.png (or .jpg)"""
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = P(ep, "refs", key + ext)
        if os.path.exists(p):
            return p.replace("\\", "/")
    return P(ep, "refs", key + ".png").replace("\\", "/")


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)


def final_lines(ep, e):
    """line timings on the joined song, with the manual overrides from episode.json applied"""
    lines = jload(P(ep, "work", "lines_final.json"))
    for o in e["song"].get("line_overrides", []):
        for ln in lines:
            if ln["section"] == o["section"] and ln["i"] == o["i"]:
                ln["t_start"], ln["t_end"] = o["t_start"], o["t_end"]
    return lines
