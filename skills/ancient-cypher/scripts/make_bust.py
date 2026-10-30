# -*- coding: utf-8 -*-
"""Optional - half-body references for singers who only have a turnaround sheet. The sheet's front view (left third,
head to waist) becomes a MiniMax image-01 character reference; two candidates per singer land in 定妆图/
(<id>_bust_1.png, <id>_bust_2.png). Look at both, copy the better one to refs/<id>_bust.png.
Cropping the sheet instead does not work: each face is only ~60 px wide there.

usage: python scripts/make_bust.py <episode_dir> sha tao liu ...
Costs a few cents per image on the MiniMax API; the key comes only from MINIMAX_API_KEY.
"""
import base64
import io
import json
import os
import sys
import urllib.request

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402

EP, WHO = sys.argv[1], sys.argv[2:]
E = _lib.episode(EP)
API = os.environ.get("MINIMAX_API_BASE", "https://api.minimax.io").rstrip("/")
PROMPT = ("cinematic photoreal waist-up portrait, facing the camera three-quarters, plain grey studio background, "
          "soft even studio light. {d}. Singing into a vintage silver microphone on a black stand, the microphone set "
          "low at chin height so the whole mouth stays visible. Same face, hair and costume as the reference. "
          "Original face, not resembling any real actor. realistic skin texture, ultra detailed, 35mm film still")


def front_crop(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    c = im.crop((0, 0, w // 3, int(h * 0.62)))
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    buf = io.BytesIO()
    c.save(buf, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


for k in WHO:
    body = {"model": "image-01", "prompt": PROMPT.format(d=E["singers"][k]["desc_en"]), "aspect_ratio": "16:9", "n": 2,
            "response_format": "base64", "prompt_optimizer": False,
            "subject_reference": [{"type": "character", "image_file": front_crop(_lib.ref(EP, k + "_sheet"))}]}
    req = urllib.request.Request(API + "/v1/image_generation", json.dumps(body).encode(),
                                 {"Authorization": "Bearer " + os.environ["MINIMAX_API_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.loads(r.read().decode())
    if (resp.get("base_resp") or {}).get("status_code", 0) != 0:
        sys.exit("%s: %s" % (k, resp.get("base_resp")))
    os.makedirs(_lib.P(EP, "定妆图"), exist_ok=True)
    for i, b in enumerate(resp["data"]["image_base64"], 1):
        out = _lib.P(EP, "定妆图", "%s_bust_%d.png" % (k, i))
        Image.open(io.BytesIO(base64.b64decode(b))).save(out)
        print("saved", out)
