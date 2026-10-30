# -*- coding: utf-8 -*-
# Vendored from ancient-rap-battle (https://github.com/10291124jcjc-dotcom/ancient-rap-battle),
# Copyright (c) 2026 硅基废话 (10291124jcjc-dotcom), MIT License - see LICENSE-ancient-rap-battle.
"""Fonts, gold / red gradient titles, the lyric line and name card sheets and grade "B".
From common.py, cover.py and package.py; names merged: GOLD/RED = title gradients, GOLD_TEXT/INK_TEXT = lyric colours."""
import os
import random
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from _lib import die

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "ancient-cypher")

FONT_URLS = {
    # all SIL Open Font License, from the official Google Fonts repository
    "brush": ("MaShanZheng-Regular.ttf",
              "https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf"),
    "serif_sc": ("NotoSerifSC[wght].ttf",
                 "https://github.com/google/fonts/raw/main/ofl/notoserifsc/NotoSerifSC%5Bwght%5D.ttf"),
}
LOCAL_FONTS = {
    "serif_sc": ["C:/Windows/Fonts/NotoSerifSC-VF.ttf", "/Library/Fonts/NotoSerifSC-VF.ttf",
                 "/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc"],
    "serif_en_bold": ["C:/Windows/Fonts/georgiab.ttf", "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
                      "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
    "serif_en_bolditalic": ["C:/Windows/Fonts/georgiaz.ttf", "/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf",
                            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"],
}


def font(kind):
    """local font if present, otherwise download the OFL font once into the cache"""
    for p in LOCAL_FONTS.get(kind, []):
        if os.path.exists(p):
            return p
    if kind in FONT_URLS:
        name, url = FONT_URLS[kind]
        dst = os.path.join(CACHE, "fonts", name)
        if not os.path.exists(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            print("downloading font", name)
            urllib.request.urlretrieve(url, dst)
        return dst
    if kind.startswith("serif_en"):
        return font("serif_sc")
    die("no font for " + kind)


GOLD = [(255, 244, 190), (246, 200, 72), (196, 132, 24)]
RED = [(255, 96, 70), (214, 30, 30), (140, 10, 16)]
CREAM = [(255, 248, 225), (250, 232, 180), (232, 200, 130)]
INK = (34, 16, 0)


def gradient(size, stops):
    w, h = size
    g = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        a, b, u = (stops[0], stops[1], t / 0.5) if t < 0.5 else (stops[1], stops[2], (t - 0.5) / 0.5)
        g.putpixel((0, y), tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3)))
    return g.resize((w, h))


def fancy(img, xy, text, f, stops, stroke=6, shadow=14):
    W, H = img.size
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text(xy, text, font=f, fill=255, anchor="mm")
    outline = Image.new("L", (W, H), 0)
    ImageDraw.Draw(outline).text(xy, text, font=f, fill=255, anchor="mm", stroke_width=stroke, stroke_fill=255)
    img.paste(Image.new("RGB", (W, H), (0, 0, 0)), (6, 10), outline.filter(ImageFilter.GaussianBlur(shadow)).point(lambda v: int(v * .85)))
    img.paste(Image.new("RGB", (W, H), INK), (0, 0), outline)
    bb = mask.getbbox()
    if bb:
        grad = Image.new("RGB", (W, H), stops[1])
        grad.paste(gradient((bb[2] - bb[0], bb[3] - bb[1]), stops), bb[:2])
        img.paste(grad, (0, 0), mask)


def row(img, cx, y, items, gap=20):
    """items = [(text, font, stops, stroke)] laid out by MEASURED width (brush glyph widths are irregular)"""
    d = ImageDraw.Draw(img)
    ws = [d.textlength(t, font=f) for t, f, _, _ in items]
    x = cx - (sum(ws) + gap * (len(items) - 1)) / 2
    for (t, f, st, sk), w in zip(items, ws):
        fancy(img, (x + w / 2, y), t, f, st, stroke=sk)
        x += w + gap


def small(img, xy, text, anchor, fill):
    f = ImageFont.truetype(font("serif_sc"), 30 if img.size[0] < 1500 else 34)
    try:
        f.set_variation_by_name("Bold")
    except Exception:
        pass
    ImageDraw.Draw(img).text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=2, stroke_fill=INK)


GOLD_TEXT = (255, 228, 92, 255)       # bright: the darker (255, 210, 64) read dull on phones
INK_TEXT = (40, 22, 0, 255)
GRADE = ("eq=contrast=1.04:saturation=0.92:brightness=0.01,colorbalance=rs=0.01:bs=-0.01,"
         "curves=all='0/0 0.25/0.24 0.6/0.6 0.85/0.8 1/0.92',cas=0.35,vignette=angle=PI/12,noise=alls=9:allf=t+u")


class Sheet:
    def __init__(self, w, h):
        self.W, self.H, self.S = w, h, w / 1920

    def canvas(self):
        return Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))

    def f(self, size, weight="Black"):
        f = ImageFont.truetype(font("serif_sc"), int(size * self.S))
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
        return f

    def shadowed(self, layer):
        sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        sh.putalpha(layer.split()[3].point(lambda v: int(v * 0.7)))
        out = self.canvas()
        out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5 * self.S)), (int(3 * self.S), int(4 * self.S)))
        out.alpha_composite(layer)
        return out

    def brush(self, w, h, seed):
        rnd = random.Random(seed)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for i in range(int(h * 0.9)):
            x0 = int(rnd.uniform(0, 0.06) * w + (0.05 * w if i > h * 0.7 else 0))
            x1 = int(w - rnd.uniform(0, 0.12) * w - 0.18 * w * (i / h) ** 2)
            a = int(rnd.uniform(150, 235) * (0.55 if rnd.random() < 0.12 else 1))
            d.line([(x0, int(h * 0.05) + i), (x1, int(h * 0.05) + i)], fill=(190, 18, 24, a))
        return im.filter(ImageFilter.GaussianBlur(1.2))

    def lyric(self, text, note, seed):
        S, W, H = self.S, self.W, self.H
        img, layer = self.canvas(), self.canvas()
        d = ImageDraw.Draw(layer)
        han = [i for i, c in enumerate(text) if "一" <= c <= "鿿"]
        cut = han[-2] if len(han) >= 2 else 0
        head, tail = text[:cut].replace(" ", "  "), text[cut:]
        fh, ft = self.f(60), self.f(84)
        wh, wt = d.textlength(head, font=fh), d.textlength(tail, font=ft)
        base = int(H * 0.896)
        x = (W - wh - wt) / 2
        img.alpha_composite(self.brush(int(wt + 46 * S), int(52 * S), seed), (int(x + wh - 20 * S), int(base - 34 * S)))
        d.text((x, base), head, font=fh, fill=GOLD_TEXT, anchor="ls", stroke_width=int(3 * S), stroke_fill=INK_TEXT)
        d.text((x + wh, base), tail, font=ft, fill=GOLD_TEXT, anchor="ls", stroke_width=int(4 * S), stroke_fill=INK_TEXT)
        if note:
            fn = self.f(36)
            while d.textlength(note, font=fn) > W - 120 * S:
                fn = ImageFont.truetype(font("serif_sc"), fn.size - 2)
                fn.set_variation_by_name("Black")
            y = int(H * 0.971)
            glow = self.canvas()               # a soft white halo makes the white read brighter
            ImageDraw.Draw(glow).text((W / 2, y), note, font=fn, fill=(255, 255, 255, 110), anchor="ms",
                                      stroke_width=int(5 * S), stroke_fill=(255, 255, 255, 70))
            layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6 * S)))
            d.text((W / 2, y), note, font=fn, fill=(255, 255, 255, 255), anchor="ms",
                   stroke_width=int(2.5 * S), stroke_fill=(0, 0, 0, 235))
            bh = int(H * 0.18)
            band = Image.new("L", (1, bh))
            for yy in range(bh):
                band.putpixel((0, yy), int(165 * min(1, yy / (bh * 0.58))))
            img.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, bh), 0)] * 3 + [band.resize((W, bh))]), (0, H - bh))
        img.alpha_composite(self.shadowed(layer))
        return img

    def name(self, name, aka, right):
        S, W, H = self.S, self.W, self.H
        img, layer = self.canvas(), self.canvas()
        d = ImageDraw.Draw(layer)
        x = W - int(150 * S) if right else int(150 * S)
        anc = "rs" if right else "ls"          # B's card sits on the right, where B stands
        d.text((x, int(H * 0.8125)), "“%s”" % name, font=self.f(92), fill=GOLD_TEXT, anchor=anc,
               stroke_width=int(3 * S), stroke_fill=INK_TEXT)
        if aka:
            d.text((x, int(H * 0.849)), "aka %s" % aka, font=self.f(36, "Bold"), fill=(250, 232, 180, 255), anchor=anc,
                   stroke_width=int(2 * S), stroke_fill=INK_TEXT)
        img.alpha_composite(self.shadowed(layer))
        return img

    def title(self, a, b):
        S, W, H = self.S, self.W, self.H
        img = self.canvas()
        br = ImageFont.truetype(font("brush"), int(172 * S))
        en = ImageFont.truetype(font("serif_en_bolditalic"), int(150 * S))
        row(img, W // 2, int(H * 0.44), [(a, br, GOLD, 8), ("VS", en, RED, 8), (b, br, GOLD, 8)], gap=30)
        fancy(img, (W // 2, int(H * 0.58)), "FREESTYLE BATTLE", ImageFont.truetype(font("serif_en_bold"), int(64 * S)),
              GOLD, stroke=4, shadow=8)
        fancy(img, (W // 2, int(H * 0.655)), "AI生成  仅供娱乐", self.f(40, "Bold"), CREAM, stroke=3, shadow=6)
        return img

    def end(self, l1, l2):
        S, W, H = self.S, self.W, self.H
        img = self.canvas()
        br = ImageFont.truetype(font("brush"), int(150 * S))
        fancy(img, (W // 2, int(H * 0.40)), l1, br, GOLD, stroke=8)
        fancy(img, (W // 2, int(H * 0.56)), l2, br, GOLD, stroke=8)
        fancy(img, (W // 2, int(H * 0.68)), "FREESTYLE BATTLE  ·  AI生成 仅供娱乐", self.f(36, "Bold"), CREAM, stroke=3, shadow=6)
        return img

    def watermark(self, text):
        S, W = self.S, self.W
        img, layer = self.canvas(), self.canvas()
        ImageDraw.Draw(layer).text((W - int(56 * S), int(80 * S)), text, font=self.f(38, "Bold"), fill=(255, 228, 92, 215),
                                   anchor="rs", stroke_width=int(2 * S), stroke_fill=INK_TEXT)
        img.alpha_composite(self.shadowed(layer))
        return img
