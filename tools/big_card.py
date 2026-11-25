"""Minimaximal big-number cards: one vivid colour, one giant number, one short label.

Usage: python3 tools/big_card.py cards.json
cards.json: [{"out": "x.jpg", "bg": "#ffcc00", "fg": "#111111", "big": "35", "unit": "МЛН $",
              "label": "за одну добу", "photo": "optional.jpg"}]
With "photo", the photo sits in a tilted paper-cut frame above the number (collage touch).
Safe zones: nothing in the bottom 320 px or right 120 px.
"""
import json
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1920
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def fit(draw, text, path, size, max_w):
    while size > 40:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 8
    return font(path, size)


def grain(im, amount=10, seed=1):
    rnd = random.Random(seed)
    noise = Image.effect_noise((W, H), 40).convert("L")
    noise = ImageOps.autocontrast(noise)
    return Image.blend(im, Image.merge("RGB", (noise, noise, noise)), amount / 255 * 2.2)


def card(c):
    im = Image.new("RGB", (W, H), c.get("bg", "#ffcc00"))
    d = ImageDraw.Draw(im)
    fg = c.get("fg", "#111111")
    cx = (W - 120) // 2 + 30  # keep clear of the right UI rail
    top = 330
    if c.get("photo"):
        ph = Image.open(c["photo"]).convert("RGB")
        ph = ImageOps.fit(ph, (700, 520), Image.LANCZOS)
        frame = Image.new("RGB", (740, 560), "#fbf7ee")
        frame.paste(ph, (20, 20))
        frame = frame.rotate(c.get("tilt", -3), expand=True, resample=Image.BICUBIC, fillcolor=c.get("bg", "#ffcc00"))
        sh = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([25, 25, frame.width - 10, frame.height - 10], fill=(0, 0, 0, 90))
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        x = cx - frame.width // 2
        im.paste(sh, (x + 10, 250 + 16), sh)
        im.paste(frame, (x, 250))
        top = 250 + frame.height + 40
    big = c["big"]
    fb = fit(d, big, BOLD, 400 if not c.get("photo") else 300, W - 260)
    bb = d.textbbox((0, 0), big, font=fb)
    y = top if c.get("photo") else 560
    d.text((cx - (bb[2] - bb[0]) // 2 - bb[0], y - bb[1]), big, font=fb, fill=fg)
    y += bb[3] - bb[1] + 30
    if c.get("unit"):
        fu = fit(d, c["unit"], BOLD, 120, W - 260)
        ub = d.textbbox((0, 0), c["unit"], font=fu)
        d.text((cx - (ub[2] - ub[0]) // 2 - ub[0], y - ub[1]), c["unit"], font=fu, fill=c.get("accent", fg))
        y += ub[3] - ub[1] + 40
    if c.get("label"):
        fl = fit(d, c["label"], SEMI, 64, W - 260)
        lb = d.textbbox((0, 0), c["label"], font=fl)
        pad = 22
        bx0 = cx - (lb[2] - lb[0]) // 2 - pad
        d.rectangle([bx0, y - pad // 2, bx0 + (lb[2] - lb[0]) + 2 * pad, y + (lb[3] - lb[1]) + pad], fill=fg)
        d.text((bx0 + pad - lb[0], y - lb[1] + pad // 4), c["label"], font=fl, fill=c.get("bg", "#ffcc00"))
    assert y < H - 320, "card text runs into the bottom safe zone"
    im = grain(im, 6)
    im.save(c["out"], quality=93)


if __name__ == "__main__":
    for c in json.load(open(sys.argv[1])):
        card(c)
        print("ok", c["out"])
