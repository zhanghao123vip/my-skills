# -*- coding: utf-8 -*-
"""Step 8 - write work/clips.json for h3run.py from episode.json "shots".

Singing shots: the lip-sync window starts 0.15 s before the first line; every half line (split at the space) is
timed to 0.01 s from the whisper word times and can carry an action ("line.half" -> what the singer does).
The mic is always written LOW at chin height - a mic in front of the mouth hides the lips and fails the check.
Group shots ("who": "group") describe the front row left / center / right from their own reference images.
Stills (audience, DJ, ending) are silent clips.

usage: python scripts/make_shots.py <episode_dir> [ID ...]   (no ids = all shots; ids = rewrite only those)
then:  python scripts/h3run.py <episode_dir> --all --estimate
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402

EP, ONLY = sys.argv[1], set(sys.argv[2:])
E = _lib.episode(EP)
S = E["singers"]
lines = _lib.final_lines(EP, E)
offsets = _lib.jload(_lib.P(EP, "work", "offsets.json"))
words = []
for fid, (a, o) in offsets.items():
    p = _lib.P(EP, "work", "asr_%s.json" % fid)
    if os.path.exists(p):
        words += [{"s": w["s"] - a + o, "w": w["w"]} for w in _lib.jload(p)]

SCENE = E["scene_en"]
MIC = "a vintage silver microphone on a black stand set LOW at chin height so the whole mouth stays clearly visible"
TAIL = "Mouths move only when singing. No subtitles, no text, no watermark."


def han(s):
    return "".join(ch for ch in s if "一" <= ch <= "鿿")


def halves(ln):
    parts = ln["lyric"].split(" ")
    first, second = parts[0], " ".join(parts[1:])
    t0, t1 = ln["t_start"], ln["t_end"]
    if not second:
        return [(t0, t1, first)]
    n, mid, cnt = len(han(first)), None, 0
    for w in (w for w in words if t0 - 0.2 <= w["s"] < t1 - 0.1):
        if cnt >= n:
            mid = w["s"]
            break
        cnt += len(han(w["w"]))
    if mid is None or not t0 + 0.3 < mid < t1 - 0.3:
        mid = t0 + (t1 - t0) * n / max(1, len(han(ln["lyric"])))
    return [(t0, mid, first), (mid, t1, second)]


def group_text():
    g = E["group"]
    l, c, r = g["front_row"]
    return ("Three singers stand side by side in the front row, each behind their own %s: in the CENTER the %s from "
            "reference image 3 (%s); on the LEFT the %s from reference image 2 (%s); on the RIGHT the %s from reference "
            "image 4 (%s). Behind them more singers in ancient costume: %s. %s The setting matches reference image 1. "
            "Keep each face exactly as its own reference, never mix faces.") % (
        MIC, S[c]["gender"], S[c]["desc_en"], S[l]["gender"], S[l]["desc_en"], S[r]["gender"], S[r]["desc_en"],
        g.get("back_row_en", ""), g.get("rule_en", ""))


def sing(cid, sp):
    dur = sp.get("dur", 10)
    i0, i1 = sp["lines"]
    ls = [l for l in lines if l["section"] == sp["section"] and i0 <= l["i"] <= i1]
    w0 = ls[0]["t_start"] - 0.15
    acts = sp.get("actions", {})
    tm = []
    for k, ln in enumerate(ls):
        for h, (a, b, txt) in enumerate(halves(ln)):
            a, b = max(0.0, a - w0), min(float(dur), b - w0)
            if a >= dur:
                continue
            s = "%.2f-%.2fs sings '%s'" % (a, b, txt.replace(" ", ""))
            if "%d.%d" % (k, h) in acts:
                s += ", " + acts["%d.%d" % (k, h)]
            tm.append(s)
    who = sp.get("who") or ls[0]["who"]
    if who == "group":
        head = "16:9 cinematic photoreal %s, %s. %s All of them sing the reference audio together in unison in Mandarin with precise lip sync, %s." % (
            sp["framing"], SCENE, group_text(), sp["mood"])
        g = E["group"]["front_row"]
        imgs = sp.get("images") or ["venue", g[0] + "_bust", g[1] + "_bust", g[2] + "_bust"]
    else:
        pr = "He" if S[who]["gender"] == "man" else "She"
        head = ("16:9 cinematic photoreal %s, %s. The same %s as the reference images: %s. %s faces the camera three-quarters, %s. "
                "%s raps the reference audio in Mandarin with precise lip sync, %s.") % (
            sp["framing"], SCENE, S[who]["gender"], S[who]["desc_en"], pr, MIC, pr, sp["mood"])
        # a waist-up shot plus the expression sheet (main singers) or the turnaround (quick verses) keeps the face
        second = who + "_face" if os.path.exists(_lib.ref(EP, who + "_face")) else who + "_sheet"
        imgs = sp.get("images") or [who + "_bust", second]
    return {"id": cid, "kind": "rap", "audio": [round(w0, 3), round(w0 + dur, 3)], "lead": 0, "dur": dur,
            "images": [_lib.ref(EP, k) for k in imgs],
            "prompt": "%s Timing: %s. Camera %s. %s" % (head, "; ".join(tm), sp["camera"], TAIL)}


def still(cid, sp):
    return {"id": cid, "kind": "still", "dur": sp.get("dur", 5), "images": [_lib.ref(EP, k) for k in sp["images"]],
            "prompt": "16:9 cinematic photoreal, %s. %s. Camera %s. Realistic faces, natural skin, 35mm film grain. "
                      "No subtitles, no text." % (sp["what"], SCENE, sp["camera"])}


new = [sing(k, v) for k, v in E["shots"]["sing"].items()] + [still(k, v) for k, v in E["shots"].get("stills", {}).items()]
path = _lib.P(EP, "work", "clips.json")
old = {c["id"]: c for c in _lib.jload(path)} if os.path.exists(path) else {}
for c in new:
    if not ONLY or c["id"] in ONLY:
        old[c["id"]] = c
missing = sorted({i for c in old.values() for i in c["images"] if not os.path.exists(i)})
_lib.jsave(path, list(old.values()))
print("%d shots, %d s -> work/clips.json" % (len(old), sum(c["dur"] for c in old.values())))
if missing:
    print("missing reference images:\n  " + "\n  ".join(missing))
