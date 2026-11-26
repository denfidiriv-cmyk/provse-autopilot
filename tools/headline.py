"""Постійний заголовок-плашка вгорі шортса (формат, який зараз масово заходить у Shorts):
біла заокруглена плашка з чорним жирним текстом, 1-2 рядки, видно весь ролик.

  python3 tools/headline.py "ТЕКСТ ЗАГОЛОВКА" out.png
  ffmpeg -i final.mp4 -i out.png -filter_complex overlay=0:0 ...

Плашка стоїть між 170 і ~370 px від верху: нижче за верхні іконки YouTube і вище за великі цифри карток.
Ширина до 840 px по центру, тож права смуга 120 px (кнопки YouTube) лишається вільною.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
MAXW = 840


def wrap(d, text, f):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= MAXW - 70 or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def make(text, out):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for size in range(66, 38, -2):
        f = ImageFont.truetype(FONT, size)
        lines = wrap(d, text, f)
        if len(lines) <= 2 and all(d.textlength(l, font=f) <= MAXW - 70 for l in lines):
            break
    lh = int(size * 1.22)
    bw = max(d.textlength(l, font=f) for l in lines) + 70
    bh = lh * len(lines) + 44
    x0, y0 = (W - bw) / 2, 180
    d.rounded_rectangle((x0 + 6, y0 + 8, x0 + bw + 6, y0 + bh + 8), 26, fill=(0, 0, 0, 90))
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 26, fill=(255, 255, 255, 255))
    for i, l in enumerate(lines):
        d.text((W / 2, y0 + 22 + i * lh + lh / 2), l, font=f, fill=(12, 12, 12), anchor='mm')
    assert y0 + bh < 420, 'заголовок задовгий'
    im.save(out)


if __name__ == '__main__':
    make(sys.argv[1], sys.argv[2])
