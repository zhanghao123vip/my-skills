# -*- coding: utf-8 -*-
"""Step 10 - picture cut on the song timeline. Every singing clip sits exactly at its lip-sync window (from
work/clips.json, accepted take from work/picks.json); the silent cutaways in episode.json edit.cutaways
([clip, in-point, song time, length]) cover the seams; a leftover gap holds the last frame; the ending clip
is slowed down under the fade-out.

usage: python scripts/assemble.py <episode_dir>  ->  preview/成片_拼接.mp4 (1920x1080, 24 fps, with the song)
Prints every held gap: more than ~0.3 s shows as a freeze, so put a cutaway there.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402

EP = sys.argv[1]
E = _lib.episode(EP)
FPS, W, H = 24, 1920, 1080
clips = {c["id"]: c for c in _lib.jload(_lib.P(EP, "work", "clips.json"))}
picks = _lib.jload(_lib.P(EP, "work", "picks.json"))
SONG_END = _lib.duration(_lib.P(EP, "音乐_最终.wav"))
ed = E["edit"]
end = ed.get("end", {})


def src(cid):
    if cid not in picks:
        sys.exit("no accepted take for %s (work/picks.json)" % cid)
    return _lib.P(EP, "clips", "%s_t%d.mp4" % (cid, picks[cid]))


sing = sorted((clips[k]["audio"][0], k) for k in picks if k in clips and clips[k]["kind"] == "rap")
end_at = end.get("at", SONG_END)
tl = []
for i, (w0, k) in enumerate(sing):
    tl.append([w0, sing[i + 1][0] if i + 1 < len(sing) else end_at, src(k), 0.0, 1.0])
if end.get("clip"):
    tl.append([end_at, SONG_END, src(end["clip"]), 0.0, end.get("slow", 1.0)])


def overlay(tl, piece):
    t0, t1 = piece[0], piece[1]
    out = []
    for p in tl:
        a, b = p[0], p[1]
        if b <= t0 or a >= t1:
            out.append(p)
            continue
        if a < t0:
            out.append([a, t0, p[2], p[3], p[4]])
        if b > t1:
            out.append([t1, b, p[2], p[3] + (t1 - a) / p[4], p[4]])
    return sorted(out + [piece], key=lambda x: x[0])


for cid, inp, t, ln in ed.get("cutaways", []):
    tl = overlay(tl, [t, t + ln, src(cid), inp, 1.0])
if tl and tl[0][0] > 0.02:
    print("! nothing before %.2fs - add a cutaway at 0 (the title sits there)" % tl[0][0])

seg = _lib.P(EP, "work", "segs")
os.makedirs(seg, exist_ok=True)
for f in os.listdir(seg):
    os.remove(os.path.join(seg, f))
lst = []
for n, (t0, t1, path, inp, speed) in enumerate(tl):
    length = t1 - t0
    if length < 0.02:
        continue
    hold = max(0.0, length - (_lib.duration(path) - inp) * speed + 0.05)
    vf = "setpts=%.3f*(PTS-STARTPTS),scale=%d:%d:flags=lanczos,setsar=1,fps=%d" % (speed, W, H, FPS)
    if hold > 0:
        vf += ",tpad=stop_mode=clone:stop_duration=%.3f" % hold
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % inp, "-i", path, "-an", "-vf", vf,
                    "-frames:v", str(round(length * FPS)), "-c:v", "libx264", "-preset", "fast", "-crf", "14",
                    "-pix_fmt", "yuv420p", os.path.join(seg, "%03d.mp4" % n)], check=True)
    lst.append("file %03d.mp4" % n)
    if hold > 0.1:
        print("hold %.2fs at %.2f (%s)" % (hold, t1 - hold, os.path.basename(path)))
open(os.path.join(seg, "list.txt"), "w").write("\n".join(lst))
os.makedirs(_lib.P(EP, "preview"), exist_ok=True)
out = _lib.P(EP, "preview", "成片_拼接.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(seg, "list.txt"),
                "-i", _lib.P(EP, "音乐_最终.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                "-b:a", "256k", "-shortest", out], check=True)
print("wrote", out, "%.2fs, %d pieces" % (_lib.duration(out), len(lst)))
