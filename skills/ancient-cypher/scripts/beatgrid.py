# -*- coding: utf-8 -*-
# Vendored from ancient-rap-battle (https://github.com/10291124jcjc-dotcom/ancient-rap-battle),
# Copyright (c) 2026 硅基废话 (10291124jcjc-dotcom), MIT License - see LICENSE-ancient-rap-battle.
"""Beat grid of the instrumental and the verse finder (one lyric line = one bar). From analyze_song.py, unchanged."""
import difflib

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

from _lib import die


def beat_grid(inst):
    print("[3/7] beat grid...")
    x, sr = sf.read(inst)
    x = x.mean(1) if x.ndim > 1 else x
    x = resample_poly(x, 1, 4)
    sr //= 4
    hop, n = int(sr / 200), 1024
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
    sp = np.log1p(np.abs(np.fft.rfft(fr, axis=1)))
    on = np.maximum(np.diff(sp, axis=0), 0).sum(1)
    on = np.maximum(on - np.convolve(on, np.ones(40) / 40, "same"), 0)
    fps = sr / hop

    def best(bpms):
        b = (-1, 0, 0)
        for bpm in bpms:
            p = 60 / bpm * fps
            k = np.arange(0, len(on) / p - 1)
            for ph in range(int(p)):
                s = on[(ph + k * p).astype(int)].sum()
                if s > b[0]:
                    b = (s, bpm, ph / fps)
        return b
    _, bpm, _ = best(np.arange(70, 120, 0.1))
    _, bpm, b0 = best(np.arange(bpm - 0.15, bpm + 0.15, 0.01))
    return float(bpm), float(b0)


def han(s):
    return "".join(ch for ch in s if "一" <= ch <= "鿿")


def find_verse(words, t_from, lyrics, beat, b0, bar):
    """where the verse starts = where the recognized text best matches its first 4 lyric lines
    (the recognizer writes homophones and hallucinates in instrumental parts, but many characters still match),
    then one bar per lyric line from that anchor"""
    n_lines = len(lyrics)
    target = han("".join(lyrics[:4]))
    ws = [w for w in words if w["s"] >= t_from]
    best = (0.0, None)
    for i, w in enumerate(ws):
        window = han("".join(x["w"] for x in ws[i:] if x["s"] < w["s"] + 4 * bar))
        if len(window) < len(target) * 0.4:
            continue
        sm = difflib.SequenceMatcher(None, window, target)
        score = sum(b.size for b in sm.get_matching_blocks()) / len(target)
        if score > best[0]:
            best = (score, w["s"])
    t0 = best[1]
    if t0 is None or best[0] < 0.25:
        die("could not find the verse starting with '%s' after %.1fs - check the song sings the lyrics" % (lyrics[0], t_from))
    print("      verse '%s...' found at %.2fs (text match %.0f%%)" % (lyrics[0][:6], t0, best[0] * 100))
    k = np.ceil((t0 - 0.25 - b0) / beat)
    anchor = b0 + k * beat
    lines = []
    for i in range(n_lines):
        bt = anchor + i * bar
        ws = [w for w in words if bt - 0.13 <= w["s"] < bt + bar - 0.13]
        # Suno lets the previous line's last syllable spill up to ~0.15 s past the bar line: skip words up to
        # and including the last one (among the first three, starting before bar + 0.15) that is that syllable
        prev_tail = han(lyrics[i - 1])[-1:] if i else ""
        k = 0
        for j, w in enumerate(ws[:3]):
            if prev_tail and w["s"] < bt + 0.15 and han(w["w"])[-1:] == prev_tail:
                k = j + 1
        ws = ws[k:] if k < len(ws) else ws
        lines.append({"bar": round(bt, 3), "start": round(min((w["s"] for w in ws), default=bt), 3),
                      "heard": "".join(w["w"] for w in ws).strip()})
    return anchor, lines
