# -*- coding: utf-8 -*-
"""Step 11 - packaging with the battle skill's text styles: grade B, opening title (+ feat. list + AI notice),
a name card on each singer's first line (lifted 150 px so long lyric lines never run into it), every lyric line in
gold with the last two characters on a red brush stroke, end question card, 2.5 s fade-out.

usage: python scripts/package_film.py <episode_dir> [--test from:to] [--phone]
writes final/<title>_成片.mp4 (CRF 21, ~1 MB/s); --phone also writes a 720p copy under 80 MB.
"""
import argparse
import os
import subprocess
import sys

from PIL import ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402
from common import font  # noqa: E402  (ancient-rap-battle)
from cover import CREAM, GOLD as GOLD_GRAD, fancy  # noqa: E402
from package import GRADE, Sheet  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("ep")
ap.add_argument("--test", default=None)
ap.add_argument("--phone", action="store_true")
a = ap.parse_args()
EP, E = a.ep, _lib.episode(a.ep)
W, H, FPS = 1920, 1080, 24
SRC = _lib.P(EP, "preview", "成片_拼接.mp4")
END = _lib.duration(SRC)
tmp = _lib.P(EP, "work", "package")
os.makedirs(tmp, exist_ok=True)
sh = Sheet(W, H)
ed = E.get("edit", {})
lines = _lib.final_lines(EP, E)


def title():
    img = sh.canvas()
    fancy(img, (W // 2, int(H * 0.40)), E["title"], ImageFont.truetype(font("brush"), int(210 * sh.S)), GOLD_GRAD, stroke=9, shadow=16)
    if E.get("title_en"):
        fancy(img, (W // 2, int(H * 0.53)), E["title_en"], ImageFont.truetype(font("serif_en_bold"), int(70 * sh.S)),
              GOLD_GRAD, stroke=4, shadow=8)
    feat = "feat.  " + " · ".join(s["name"] for s in E["singers"].values())
    fancy(img, (W // 2, int(H * 0.615)), feat, sh.f(34, "Bold"), CREAM, stroke=3, shadow=6)
    fancy(img, (W // 2, int(H * 0.68)), E.get("disclaimer", "AI生成  仅供娱乐"), sh.f(30, "Bold"), CREAM, stroke=3, shadow=6)
    return img


def end_card():
    img = sh.canvas()
    l1, l2, l3 = E.get("end_card") or ["这一关", "你卡在哪儿了？", "评论区说说"]
    br = ImageFont.truetype(font("brush"), int(140 * sh.S))
    fancy(img, (W // 2, int(H * 0.38)), l1, br, GOLD_GRAD, stroke=8)
    fancy(img, (W // 2, int(H * 0.53)), l2, br, GOLD_GRAD, stroke=8)
    fancy(img, (W // 2, int(H * 0.65)), l3, sh.f(40, "Bold"), CREAM, stroke=3, shadow=6)
    fancy(img, (W // 2, int(H * 0.72)), "%s %s  ·  %s" % (E["title"], E.get("title_en", ""), E.get("disclaimer", "AI生成 仅供娱乐")),
          sh.f(28, "Bold"), CREAM, stroke=3, shadow=6)
    return img


layers = []            # (png, start, end, fade, y offset)
title().save(os.path.join(tmp, "title.png"))
layers.append(("title.png", 0.25, ed.get("title_until", 6.2), 0.4, 0))
seen = set()
for i, ln in enumerate(lines):
    who = ln["who"]
    if who in E["singers"] and who not in seen:
        seen.add(who)
        sh.name(E["singers"][who]["name"], E["singers"][who].get("aka", ""), False).save(os.path.join(tmp, "name_%s.png" % who))
        layers.append(("name_%s.png" % who, ln["t_start"] - 0.08, ln["t_start"] + 3.6, 0.25, -150))
    sh.lyric(ln["lyric"], "", i).save(os.path.join(tmp, "line_%03d.png" % i))
    nxt = lines[i + 1]["t_start"] if i + 1 < len(lines) else None
    stop = nxt - 0.07 if nxt is not None and nxt - ln["t_end"] < 1.0 else ln["t_end"] + 0.4
    layers.append(("line_%03d.png" % i, ln["t_start"] - 0.05, stop, 0.0, 0))
end_card().save(os.path.join(tmp, "end.png"))
layers.append(("end.png", ed.get("end_card_from", END - 11), END, 0.6, 0))

t_from, t_to = (0.0, END) if not a.test else [float(x) for x in a.test.split(":")]
inputs = ["-ss", "%.3f" % t_from, "-t", "%.3f" % (t_to - t_from), "-i", SRC]
fc = ["[0:v]%s,fade=t=out:st=%.3f:d=2.5,format=yuv420p,setpts=PTS-STARTPTS[base]" % (GRADE, END - t_from - 2.5)]
last, k = "base", 1
for idx, (png, st, en, fade, dy) in enumerate(layers):
    st, en = max(st, t_from) - t_from, min(en, t_to) - t_from
    if en - st < 0.05:
        continue
    d = en - st
    inputs += ["-loop", "1", "-framerate", str(FPS), "-t", "%.3f" % d, "-i", os.path.join(tmp, png)]
    ch = "[%d:v]format=rgba" % k
    if fade:
        ch += ",fade=t=in:st=0:d=%.2f:alpha=1,fade=t=out:st=%.3f:d=%.2f:alpha=1" % (fade, max(0, d - fade), fade)
    fc += [ch + ",setpts=PTS-STARTPTS+%.3f/TB[l%d]" % (st, idx), "[%s][l%d]overlay=0:%d:eof_action=pass[o%d]" % (last, idx, dy, idx)]
    last, k = "o%d" % idx, k + 1
fc.append("[0:a]afade=t=in:d=0.05[aout]")
script = os.path.join(tmp, "fc.txt")
open(script, "w", encoding="utf-8").write(";".join(fc))
os.makedirs(_lib.P(EP, "final"), exist_ok=True)
out = _lib.P(EP, "final", "%s_成片%s.mp4" % (E["title"], "_测试" if a.test else ""))
# "-/filter_complex <file>" reads the graph from a file (ffmpeg 7+; older builds: -filter_complex_script)
subprocess.run(["ffmpeg", "-y", "-v", "error"] + inputs + ["-/filter_complex", script, "-map", "[%s]" % last,
                "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS),
                "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out], check=True)
print("wrote", out)
if a.phone and not a.test:
    phone = out.replace("_成片.mp4", "_手机预览.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "slow",
                    "-b:v", "2200k", "-maxrate", "2600k", "-bufsize", "4400k", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-b:a", "160k", "-movflags", "+faststart", phone], check=True)
    print("wrote", phone)
