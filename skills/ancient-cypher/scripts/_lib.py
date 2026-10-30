# -*- coding: utf-8 -*-
"""Shared helpers: load episode.json, paths, json, durations, line timings."""
import json
import os
import subprocess
import sys


def die(msg):
    sys.exit("ERROR: " + msg)


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
