# -*- coding: utf-8 -*-
"""Step 5 - join the Suno files into one song on bar lines (episode.json song.cuts), with the SAME cuts for the
full mix (音乐_最终.wav) and the separated vocal (work/vocals_final.wav, what H3 lip-syncs to), and move every
line time onto the joined timeline (work/lines_final.json).

usage: python scripts/build_song.py <episode_dir>
cuts: [file id, start, end] in that file's own seconds; start one bar before the first sung line, end on the bar
after the last one. Every extra chorus or ad-lib Suno added is simply left outside the cut.
"""
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402

EP = sys.argv[1]
E = _lib.episode(EP)
SR, XF = 44100, 0.04
FADE_OUT = E["song"].get("fade_out", 4.0)
paths = {f["id"]: f["path"] for f in E["song"]["files"]}


def load(path):
    tmp = _lib.P(EP, "work", "_dec.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ar", str(SR), "-ac", "2", tmp], check=True)
    x, _ = sf.read(tmp, dtype="float32", always_2d=True)
    return x


def join(parts):
    n = int(XF * SR)
    ramp = np.linspace(0, 1, n, dtype=np.float32)[:, None]
    out = parts[0]
    for p in parts[1:]:
        out = np.concatenate([out[:-n], out[-n:] * (1 - ramp) + p[:n] * ramp, p[n:]])
    f = int(FADE_OUT * SR)
    out[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
    return out


mix, voc, offsets, t = [], [], {}, 0.0
for fid, a, b in E["song"]["cuts"]:
    stem = os.path.splitext(os.path.basename(paths[fid]))[0]
    m = load(_lib.P(EP, paths[fid]))
    v = load(_lib.P(EP, "work", "sep", "htdemucs", stem, "vocals.wav"))
    mix.append(m[int(a * SR):int(b * SR)])
    voc.append(v[int(a * SR):int(b * SR)])
    offsets[fid] = (a, t)
    print("file %s  %6.2f-%6.2f  ->  song %6.2f-%6.2f" % (fid, a, b, t, t + b - a))
    t += b - a - XF

sf.write(_lib.P(EP, "音乐_最终.wav"), join(mix), SR)
sf.write(_lib.P(EP, "work", "vocals_final.wav"), join(voc), SR)
lines = _lib.jload(_lib.P(EP, "work", "lines.json"))
for ln in lines:
    a, o = offsets[ln["file"]]
    for k in ("bar", "start", "end"):
        ln["t_" + k] = round(ln[k] - a + o, 3)
_lib.jsave(_lib.P(EP, "work", "lines_final.json"), lines)
_lib.jsave(_lib.P(EP, "work", "offsets.json"), offsets)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", _lib.P(EP, "音乐_最终.wav"), "-b:a", "192k",
                _lib.P(EP, "音乐_最终_试听.mp3")], check=True)
print("song %.2fs -> 音乐_最终.wav (+ 试听 mp3), work/vocals_final.wav, work/lines_final.json" % (t + XF))
