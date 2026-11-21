"""Кадр-карта України 1080x1920 для трендових шортів.

Межі областей беремо з tools/ua.js (geoBoundaries ADM1, уже спроєктовані в координати
приблизно 980x659). Виділяємо потрібні області кольором; "view" наближає частину карти (координати ua.js).
Точок міст навмисно немає: проєкція ua.js невідома, а неточна точка гірша за її відсутність.
Уміст тримаємо в смузі y 300-1180 і x 90-960, як і в tools/info_card.py.

Опис картки (JSON, список або одна):
  {"out": "map.jpg", "bg": "#0b1020", "bg2": "#22304f", "accent": "#ffd84a",
   "title": "СПИСОК НА ЕВАКУАЦІЮ", "subtitle": "...",
   "view": [470, 290, 880, 570],
   "highlight": {"Херсонська область": "#ffd84a", "Запорізька область": "#ff9f43"},
   "legend": [["Херсонщина", "9", "#ffd84a"], ["Запоріжжя", "6", "#ff9f43"]]}

Запуск: python3 tools/ua_map_card.py cards.json
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from info_card import INTER_B, INTER_SB, OSW, W, X0, X1, background, font, hexrgb, shadow_text, wrap  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

def load_regions():
    t = (ROOT / "tools/ua.js").read_text(encoding="utf-8")
    return json.loads(re.search(r"const UA=(\[.*?\]);", t, re.S).group(1))


def card(c):
    im = background(c["bg"], c["bg2"])
    d = ImageDraw.Draw(im)
    acc = hexrgb(c["accent"])
    y = 330
    ft = font(OSW, 96)
    for line in wrap(d, c["title"], ft, X1 - X0):
        shadow_text(im, (X0, y), line, ft, (255, 255, 255))
        y += 136
    if c.get("subtitle"):
        fs = font(INTER_SB, 40)
        for line in wrap(d, c["subtitle"], fs, X1 - X0):
            shadow_text(im, (X0, y), line, fs, acc)
            y += 54
    y += 30

    regions = load_regions()
    legend_h = 70 * len(c.get("legend", [])) + (20 if c.get("legend") else 0)
    box_w, box_h = X1 - X0, 1180 - y - legend_h
    vx0, vy0, vx1, vy1 = c.get("view", [0, 0, 980, 660])  # частина карти в координатах ua.js
    s = min(box_w / (vx1 - vx0), box_h / (vy1 - vy0))
    mw, mh = (vx1 - vx0) * s, (vy1 - vy0) * s
    ox = X0 + (box_w - mw) / 2 - vx0 * s
    oy = y - vy0 * s

    def tr(p):
        return (ox + p[0] * s, oy + p[1] * s)

    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    hl = c.get("highlight", {})
    for r in regions:
        col = hl.get(r["n"])
        fill = hexrgb(col) + (235,) if col else (255, 255, 255, 38)
        for poly in r["r"]:
            pts = [tr(p) for p in poly]
            if len(pts) > 2:
                ld.polygon(pts, fill=fill, outline=(255, 255, 255, 150))
    bx0 = int(X0 + (box_w - mw) / 2)
    clip = Image.new("L", im.size, 0)
    ImageDraw.Draw(clip).rounded_rectangle([bx0, y, bx0 + int(mw), y + int(mh)], 28, fill=255)
    from PIL import ImageChops
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), clip))
    if "view" in c:
        ImageDraw.Draw(im).rounded_rectangle([bx0, y, bx0 + int(mw), y + int(mh)], 28, outline=(255, 255, 255, 90), width=3)
    im.paste(layer, (0, 0), layer)

    y = y + mh + 26
    fl, fv = font(INTER_B, 46), font(OSW, 64)
    for label, value, col in c.get("legend", []):
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([X0, y + 8, X0 + 40, y + 48], 8, fill=hexrgb(col))
        shadow_text(im, (X0 + 60, y + 4), label, fl, (255, 255, 255))
        shadow_text(im, (X1 - 30, y + 28), value, fv, hexrgb(col), "rm")
        y += 70
    return im


def main(path):
    cards = json.load(open(path))
    for c in cards if isinstance(cards, list) else [cards]:
        card(c).save(c["out"], quality=93)
        print("ok", c["out"])


if __name__ == "__main__":
    main(sys.argv[1])
