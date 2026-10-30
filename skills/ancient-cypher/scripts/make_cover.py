# -*- coding: utf-8 -*-
"""Step 12 - covers from one film frame: cover-3x4.jpg (1080x1440) and cover-4x3.jpg (1440x1080), gold brush title,
English subtitle, red hook + cream line from episode.json "cover". Pick a frame where the front row smiles at the
camera (the last chorus usually has one).

usage: python scripts/make_cover.py <episode_dir> --clip CHFB --t 9   |   --frame some.png
"""
import argparse
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402
from common import font  # noqa: E402  (ancient-rap-battle)
from cover import CREAM, GOLD, RED, fancy, small  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("ep")
ap.add_argument("--clip")
ap.add_argument("--t", type=float, default=5.0)
ap.add_argument("--frame")
a = ap.parse_args()
EP, E = a.ep, _lib.episode(a.ep)
frame = a.frame
if not frame:
    picks = _lib.jload(_lib.P(EP, "work", "picks.json"))
    frame = _lib.P(EP, "work", "cover_frame.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.t), "-i",
                    _lib.P(EP, "clips", "%s_t%d.mp4" % (a.clip, picks[a.clip])), "-frames:v", "1", frame], check=True)
f = ImageEnhance.Contrast(ImageEnhance.Color(Image.open(frame).convert("RGB")).enhance(1.05)).enhance(1.08)


def sans(size):
    x = ImageFont.truetype(font("serif_sc"), size)
    x.set_variation_by_name("Black")
    return x


def shade(img, top, bottom):
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    for y in range(h):
        v = 200 * (1 - y / top) ** 1.2 if y < top else 0
        if y > h - bottom:
            v = max(v, 225 * ((y - (h - bottom)) / bottom) ** 1.1)
        d.line([(0, y), (w, y)], fill=int(v))
    img.paste(Image.new("RGB", (w, h)), (0, 0), m)


cv = E.get("cover", {})
for name, (W, H) in (("cover-3x4.jpg", (1080, 1440)), ("cover-4x3.jpg", (1440, 1080))):
    img = ImageOps.fit(f, (W, H), Image.LANCZOS, centering=(0.5, 0.45))
    shade(img, int(H * 0.30), int(H * 0.36))
    big = int(W * (0.21 if W < H else 0.15))
    fancy(img, (W // 2, int(H * 0.15)), E["title"], ImageFont.truetype(font("brush"), big), GOLD, stroke=8, shadow=14)
    if E.get("title_en"):
        fancy(img, (W // 2, int(H * 0.15) + int(big * 0.72)), E["title_en"],
              ImageFont.truetype(font("serif_en_bold"), int(big * 0.3)), GOLD, stroke=3, shadow=6)
    if cv.get("hook"):
        fancy(img, (W // 2, int(H * 0.80)), cv["hook"], sans(int(W * 0.075)), RED, stroke=4, shadow=8)
    if cv.get("line"):
        fancy(img, (W // 2, int(H * 0.80) + int(W * 0.085)), cv["line"], sans(int(W * 0.052)), CREAM, stroke=3, shadow=6)
    small(img, (36, 46), "AI 生成", "lm", (230, 230, 230))
    img.save(_lib.P(EP, name), quality=95)
    print("wrote", name)
