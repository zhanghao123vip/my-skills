# -*- coding: utf-8 -*-
"""Step 4 - line timings. Each Suno file holds a few sections in order (episode.json song.files); separate the vocal
(demucs), get word times (faster-whisper), and place every section with the battle skill's find_verse
(one lyric line = one bar). Sections whisper cannot hear take "manual_starts" (seconds in that file).

usage: python scripts/align.py <episode_dir> [--model medium]
writes work/lines.json and prints recognised text next to each lyric line - read it, a wrong anchor shows at once.
"""
import argparse
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402
import analyze_song as az  # noqa: E402  (from ancient-rap-battle)

ap = argparse.ArgumentParser()
ap.add_argument("ep")
ap.add_argument("--model", default="medium")
a = ap.parse_args()
EP, E = a.ep, _lib.episode(a.ep)


def separate(fid, path):
    d = _lib.P(EP, "work", "sep", "htdemucs", os.path.splitext(os.path.basename(path))[0])
    if not os.path.exists(os.path.join(d, "vocals.wav")):
        print("separating", path, "(demucs, a few minutes on CPU)")
        subprocess.run([sys.executable, "-m", "demucs", "--two-stems=vocals", "-o", _lib.P(EP, "work", "sep"),
                        _lib.P(EP, path)], check=True)
    return d


def words_of(fid, sep, prompt):
    cache = _lib.P(EP, "work", "asr_%s.json" % fid)
    if os.path.exists(cache):
        return _lib.jload(cache)
    from faster_whisper import WhisperModel
    x, sr = sf.read(os.path.join(sep, "vocals.wav"))
    x = x.mean(1) if x.ndim > 1 else x
    x = resample_poly(x, 16000, sr).astype(np.float32)
    m = WhisperModel(a.model, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(x, language="zh", word_timestamps=True, initial_prompt=prompt[:200],
                           condition_on_previous_text=False, beam_size=5)
    words = [{"s": w.start, "e": w.end, "w": w.word} for s in segs for w in s.words]
    _lib.jsave(cache, words)
    return words


out = []
for f in E["song"]["files"]:
    fid = f["id"]
    sep = separate(fid, f["path"])
    lyr_of = {s["name"]: E["lyrics"][s["lyrics"]] for s in f["sections"]}
    words = words_of(fid, sep, " ".join(l for s in f["sections"] for l in lyr_of[s["name"]]))
    bpm, b0 = az.beat_grid(os.path.join(sep, "no_vocals.wav"))
    beat, bar = 60 / bpm, 240 / bpm
    print("file %s: %.2f BPM, bar %.2fs" % (fid, bpm, bar))
    t = 0.0
    for s in f["sections"]:
        lyr = lyr_of[s["name"]]
        who = s.get("singers") or [s.get("singer", "all")] * len(lyr)
        if s.get("manual_starts"):
            st = s["manual_starts"]
            step = (st[-1] - st[0]) / max(1, len(st) - 1)
            lines = [{"bar": x, "start": x, "heard": "(manual)"} for x in st]
            ends = st[1:] + [st[-1] + step]
            anchor = st[-1] + step - len(lyr) * bar
        else:
            anchor, lines = az.find_verse(words, t, lyr, beat, b0, bar)
            ends = [anchor + (i + 1) * bar for i in range(len(lyr))]
        for i, (ln, lyric) in enumerate(zip(lines, lyr)):
            out.append({"file": fid, "section": s["name"], "i": i, "who": who[i], "lyric": lyric,
                        "bar": ln["bar"], "start": ln["start"], "end": round(ends[i], 3), "heard": ln["heard"]})
            print("  %-13s %2d %7.2f  %-24s | %s" % (s["name"], i, ln["start"], lyric, ln["heard"]))
        t = anchor + len(lyr) * bar - 0.5
_lib.jsave(_lib.P(EP, "work", "lines.json"), out)
print("lines:", len(out), "-> work/lines.json")
