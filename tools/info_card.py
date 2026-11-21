"""Кадри-картки 1080x1920 для трендових шортів (без фото людей).

Два типи:
  person: хто ця людина (прапор, посада, ім'я, 1-2 факти). Фото публічних осіб з інтернету
          самі не беремо; поле "photo" лише для фото, яке надав власник каналу з правом
          використання (тоді прапор стає маленьким значком у куті фото).
  rows:   таблиця/порівняння (заголовок і рядки «назва | значення | підпис»), зі смужками.

Уміст тримаємо в смузі y 300-1180, щоб не заважати субтитрам і інтерфейсу YouTube
(низ 320 px, правий край 120 px, верх порожній).

Запуск: python3 tools/info_card.py cards.json   (список карток або одна картка)
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OSW = ROOT / "work/hf/assets/fonts/Oswald-700.woff"
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
INTER_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
W, H = 1080, 1920
X0, X1 = 90, 960  # праві 120 px вільні


def font(path, size):
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def background(bg, bg2):
    a, b = hexrgb(bg), hexrgb(bg2)
    im = Image.new("RGB", (W, H), a)
    px = im.load()
    for y in range(H):
        for x in range(0, W, 4):
            t = min(1, max(0, (0.55 * y / H + 0.45 * (1 - x / W))))
            c = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
            for k in range(4):
                if x + k < W:
                    px[x + k, y] = c
    d = ImageDraw.Draw(im, "RGBA")
    for i in range(-H, W, 46):  # тонкі діагоналі, щоб фон не був пласким
        d.line([(i, H), (i + H, 0)], fill=(255, 255, 255, 9), width=2)
    return im


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def shadow_text(im, xy, text, f, fill, anchor="la"):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0], xy[1] + 6), text, font=f, fill=(0, 0, 0, 170), anchor=anchor)
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    im.paste(sh, (0, 0), sh)
    ImageDraw.Draw(im).text(xy, text, font=f, fill=fill, anchor=anchor)


def flag_badge(im, path, cx, cy, w=360):
    fl = Image.open(path).convert("RGB")
    h = int(w * fl.height / fl.width)
    if h > 260:
        h = 260
        w = int(h * fl.width / fl.height)
    fl = fl.resize((w, h), Image.LANCZOS)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=255)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([cx - w // 2, cy - h // 2 + 14, cx + w // 2, cy + h // 2 + 14], 26, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    im.paste(sh, (0, 0), sh)
    im.paste(fl, (cx - w // 2, cy - h // 2), m)
    ImageDraw.Draw(im).rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], 26, outline=(255, 255, 255), width=5)
    return cy + h // 2


CX = W // 2 - 60          # центр картки людини (праві 120 px вільні)
MAXW = 2 * (CX - X0)      # 780: текст у смузі x 90-870, телефон не обрізає краї


def fit(d, text, path, size, maxw, min_size):
    """Найбільший шрифт від size до min_size, з яким text вміщається в maxw."""
    while size > min_size and d.textlength(text, font=font(path, size)) > maxw:
        size -= 2
    return font(path, size)


def photo_badge(im, path, cx, top, w=380, h=460, flag=None):
    """Фото людини (надав власник каналу, з правом використання) у рамці; прапор у куті."""
    ph = Image.open(path).convert("RGB")
    s = max(w / ph.width, h / ph.height)
    ph = ph.resize((int(ph.width * s + 1), int(ph.height * s + 1)), Image.LANCZOS)
    x0 = (ph.width - w) // 2
    y0 = min(int(ph.height * 0.08), ph.height - h)  # обличчя зазвичай угорі кадру
    ph = ph.crop((x0, y0, x0 + w, y0 + h))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 34, fill=255)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([cx - w // 2, top + 16, cx + w // 2, top + h + 16], 34, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    im.paste(sh, (0, 0), sh)
    im.paste(ph, (cx - w // 2, top), m)
    ImageDraw.Draw(im).rounded_rectangle([cx - w // 2, top, cx + w // 2, top + h], 34, outline=(255, 255, 255), width=6)
    if flag:
        fl = Image.open(flag).convert("RGB")
        fw = 130
        fh = int(fw * fl.height / fl.width)
        fl = fl.resize((fw, fh), Image.LANCZOS)
        fx, fy = cx + w // 2 - fw + 30, top + h - fh + 24
        im.paste(fl, (fx, fy))
        ImageDraw.Draw(im).rectangle([fx, fy, fx + fw, fy + fh], outline=(255, 255, 255), width=5)
    return top + h


def person(c):
    im = background(c["bg"], c["bg2"])
    d = ImageDraw.Draw(im)
    acc = hexrgb(c["accent"])
    has_photo = bool(c.get("photo"))
    if has_photo:
        y = photo_badge(im, c["photo"], CX, 300, flag=c.get("flag")) + 50
    else:
        y = flag_badge(im, c["flag"], CX, 380) + 60
    fr = fit(d, c["role"], INTER_SB, 46, MAXW, 36)
    for line in wrap(d, c["role"], fr, MAXW):
        shadow_text(im, (CX, y), line, fr, acc, "ma")
        y += 58
    y += 22
    if has_photo:  # з фото ім'я в один рядок, щоб усе вмістилося до y 1180
        fn = fit(d, c["name"], OSW, 116, MAXW, 76)
        shadow_text(im, (CX, y), c["name"], fn, (255, 255, 255), "ma")
        y = d.textbbox((CX, y), c["name"], font=fn, anchor="ma")[3] + 34
    else:
        fn = fit(d, c["name"], OSW, 150, MAXW, 120)  # коротке ім'я лишаємо в один рядок
        if d.textlength(c["name"], font=fn) > MAXW:
            fn = font(OSW, 150)
        for line in wrap(d, c["name"], fn, MAXW):
            shadow_text(im, (CX, y), line, fn, (255, 255, 255), "ma")
            y += 180
        y += 45
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([CX - 70, y, CX + 70, y + 10], 5, fill=acc)
    y += 50 if not has_photo else 40
    ff = font(INTER_B, 46 if not has_photo else 40)
    for fact in c.get("facts", []):
        for line in wrap(d, fact, ff, MAXW):
            shadow_text(im, (CX, y), line, ff, (235, 238, 245), "ma")
            bottom = d.textbbox((CX, y), line, font=ff, anchor="ma")[3]
            y += 66 if not has_photo else 56
        y += 10
    bottom = locals().get("bottom", y)
    if bottom > 1225:  # субтитри починаються приблизно з y 1240
        print(f"УВАГА: картка {c['out']} заходить на субтитри (низ тексту y={bottom}), скороти факти", file=sys.stderr)
    return im


def rows(c):
    im = background(c["bg"], c["bg2"])
    d = ImageDraw.Draw(im)
    acc = hexrgb(c["accent"])
    y = 340
    ft = font(OSW, 104)
    for line in wrap(d, c["title"], ft, X1 - X0):
        shadow_text(im, (X0, y), line, ft, (255, 255, 255))
        y += 150
    if c.get("subtitle"):
        shadow_text(im, (X0, y), c["subtitle"], font(INTER_SB, 42), acc)
        y += 70
    y += 40
    fl, fv, fs = font(INTER_B, 52), font(OSW, 92), font(INTER_SB, 36)
    vals = [abs(r.get("bar", 0)) for r in c["rows"]]
    vmax = max(vals) if vals and max(vals) else 1
    rh = min(175, int((1180 - y) / max(1, len(c["rows"]))))
    for r in c["rows"]:
        col = hexrgb(r.get("color", c["accent"]))
        d = ImageDraw.Draw(im, "RGBA")
        d.rounded_rectangle([X0 - 20, y - 8, X1, y + rh - 22], 22, fill=(0, 0, 0, 95))
        if r.get("bar"):
            bw = int((X1 - X0 - 40) * abs(r["bar"]) / vmax)
            d.rounded_rectangle([X0 - 20, y + rh - 36, X0 - 20 + bw, y + rh - 22], 7, fill=col + (255,))
        shadow_text(im, (X0 + 6, y + 10), r["label"], fl, (255, 255, 255))
        if r.get("sub"):
            shadow_text(im, (X0 + 8, y + 76), r["sub"], fs, (200, 205, 215))
        shadow_text(im, (X1 - 24, y + rh // 2 - 18), r["value"], fv, col, "rm")
        y += rh
    if c.get("note"):
        shadow_text(im, (X0, y + 20), c["note"], font(INTER_SB, 34), (200, 205, 215))
    return im


def main(path):
    cards = json.load(open(path))
    for c in cards if isinstance(cards, list) else [cards]:
        im = person(c) if c["type"] == "person" else rows(c)
        im.save(c["out"], quality=93)
        print("ok", c["out"])


if __name__ == "__main__":
    main(sys.argv[1])
