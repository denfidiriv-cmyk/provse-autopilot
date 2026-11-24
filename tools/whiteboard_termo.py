# Whiteboard explainer: pencil draws line-art scenes, radiator colour fills, overlays, word captions.
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = '/tmp/claude-0/-home-claude/1aa8b6ad-0ff9-5c05-a29e-50e8238d6250/scratchpad/osbb'
W, H, FPS = 1080, 1920, 30
PAPER = np.array([250, 249, 246], float)
RED = (226, 38, 44); PINK = (240, 120, 130); BLUE = (70, 130, 230); INKC = (22, 22, 26)
FB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
F = lambda s: ImageFont.truetype(FB, s)
words = json.load(open(f'{S}/src/words.json'))
words = [[w[0], w[1], (words[i+1][1] if i+1 < len(words) else w[1]+0.6)] for i, w in enumerate(words)]
DUR = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{S}/src/voice.wav']))
def wt(i): return words[i][1]

# ---------- assets ----------
BOX = (120, 70, 841, 1250)  # x, y, w, h of drawing area
def load_art(name):
    im = Image.open(f'{S}/img/{name}').convert('L')
    c = Image.new('L', (572, 850), 255); c.paste(im.crop((0, 0, 572, min(850, im.height))), (0, 0))
    c = c.resize((BOX[2], BOX[3]), Image.LANCZOS)
    a = 255 - np.asarray(c, float)
    a = np.clip((a - 25) * 1.35, 0, 255) / 255.0  # ink alpha, clean paper
    full = np.zeros((H, W)); full[BOX[1]:BOX[1] + BOX[3], BOX[0]:BOX[0] + BOX[2]] = a
    return full
def art_xy(x, y):  # 572x850 coords -> frame coords
    s = BOX[2] / 572; return BOX[0] + x * s, BOX[1] + y * s

ART = {n: load_art(n) for n in ['sc1.png', 'sc2.png', 'sc4.png', 'sc5.png', 'sc6.png', 'sc7.png']}

# pencil sprite (code-drawn): tip at lower-left, body going up-right
def make_pencil(L=420, Wd=46):
    big = Image.new('RGBA', (L + 40, Wd + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
    y0, y1, cy = 20, 20 + Wd, 20 + Wd / 2
    tipx, cone, ferr = 20, 95, 40
    d.polygon([(tipx, cy), (tipx + cone, y0), (tipx + cone, y1)], fill=(236, 200, 150), outline=INKC)  # wood cone
    d.polygon([(tipx, cy), (tipx + 30, cy - 7), (tipx + 30, cy + 7)], fill=(40, 40, 45))  # graphite
    bx0, bx1 = tipx + cone, L - ferr - 30
    d.rectangle([bx0, y0, bx1, y1], fill=(250, 196, 40), outline=INKC, width=3)  # yellow body
    d.line([(bx0, cy - 8), (bx1, cy - 8)], fill=(255, 220, 110), width=4); d.line([(bx0, cy + 9), (bx1, cy + 9)], fill=(215, 160, 20), width=4)
    d.rectangle([bx1, y0 - 2, bx1 + ferr, y1 + 2], fill=(190, 190, 198), outline=INKC, width=3)  # ferrule
    for k in range(3): d.line([(bx1 + 10 + k * 10, y0), (bx1 + 10 + k * 10, y1)], fill=(140, 140, 150), width=2)
    d.rounded_rectangle([bx1 + ferr, y0, bx1 + ferr + 30, y1], 10, fill=(240, 130, 150), outline=INKC, width=3)  # eraser
    rot = big.rotate(35, expand=True, resample=Image.BICUBIC)  # tilt: tip lower-left
    # find tip position after rotation
    a = np.asarray(rot)[..., 3]; ys, xs = np.nonzero(a > 10)
    i = np.argmin(xs - ys * 0.0 + (-ys) * -1.0 * 0 + xs * 0)  # leftmost point
    k = np.argmax(ys - xs)  # bottom-left extreme
    return rot, (xs[k], ys[k])
hand, TIP = make_pencil()

# ---------- helpers ----------
def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
def reveal_mask(p, band=150):
    """zig-zag sweep over the drawing box; returns mask and pen tip."""
    x0, y0, bw, bh = BOX; nb = math.ceil(bh / band); L = p * nb
    k = int(L); f = L - k
    m = np.zeros((H, W))
    m[y0:y0 + min(k * band, bh), x0:x0 + bw] = 1
    tip = None
    if k < nb:
        ya, yb = y0 + k * band, min(y0 + (k + 1) * band, y0 + bh)
        xs = np.arange(bw); front = f * bw
        ramp = np.clip((front - xs) / 40 + 0.5, 0, 1) if k % 2 == 0 else np.clip((xs - (bw - front)) / 40 + 0.5, 0, 1)
        m[ya:yb, x0:x0 + bw] = ramp[None, :]
        tx = x0 + (front if k % 2 == 0 else bw - front)
        tip = (tx, (ya + yb) / 2 + 10 * math.sin(L * 25))
    return m, tip

def compose(ink, fills=None):
    """fills: list of (mask HxW 0..1, rgb). returns uint8 image."""
    base = np.tile(PAPER, (H, W, 1))
    for m, col in (fills or []):
        base = base * (1 - m[..., None]) + np.array(col, float) * m[..., None]
    out = base * (1 - ink[..., None]) + np.array(INKC, float) * ink[..., None]
    return out

def rect_mask(art_box, soft=6):
    x0, y0 = art_xy(art_box[0], art_box[1]); x1, y1 = art_xy(art_box[2], art_box[3])
    im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).rounded_rectangle([x0, y0, x1, y1], 14, fill=255)
    return np.asarray(im.filter(ImageFilter.GaussianBlur(soft)), float) / 255

def overlay(frame, fn):
    im = Image.fromarray(frame.clip(0, 255).astype('uint8')); d = ImageDraw.Draw(im); fn(im, d); return im

def heat(d, art_box, t, amp=1.0, col=RED):
    x0, y0 = art_xy(art_box[0], art_box[1]); x1, _ = art_xy(art_box[2], art_box[3])
    n = 5
    for k in range(n):
        cx = x0 + 30 + k * (x1 - x0 - 60) / (n - 1)
        pts = [(cx + 12 * math.sin(j / 4 + t * 7 + k), y0 - 20 - j * 6) for j in range(int(16 * amp))]
        if len(pts) > 1: d.line(pts, fill=col, width=6)

def thermo(d, x, y, temp, col, tmin=10, tmax=30):
    d.rounded_rectangle([x, y, x + 50, y + 330], 25, outline=INKC, width=6, fill=(255, 255, 255))
    d.ellipse([x - 20, y + 305, x + 70, y + 395], outline=INKC, width=6, fill=col)
    f = (temp - tmin) / (tmax - tmin); top = y + 315 - int(285 * f)
    d.rounded_rectangle([x + 13, top, x + 37, y + 320], 12, fill=col)
    for k in range(6): d.line([(x + 50, y + 30 + k * 50), (x + 72, y + 30 + k * 50)], fill=INKC, width=4)
    d.text((x + 25, y + 440), f'{temp:.0f}°C', font=F(64), fill=col, anchor='mm')

# ---------- captions ----------
KEY = {"п'ятірку,", 'не', 'працює.', 'трійка', 'двадцять', 'четвірка', 'двадцяти', 'чотирьох.', 'гріє.', 'закривається,', 'холоне.',
       'вікно.', 'холодно,', 'лічильник', 'будинку.', 'коротко,', 'цифру.', 'економіку.'}
groups, cur = [], []
for i, (w, a, b) in enumerate(words):
    cur.append(i)
    if len(cur) >= 3 or w.endswith(('.', ',', '?', ':', '!')): groups.append(cur); cur = []
if cur: groups.append(cur)
def caption(d, t):
    g = next((g for g in groups if wt(g[0]) - 0.05 <= t < (words[g[-1]][2] + 0.25)), None)
    if not g: return
    shown = [i for i in g if wt(i) - 0.05 <= t]
    if not shown: return
    fnt = F(72); parts = [(words[i][0], RED if words[i][0].lower() in KEY else INKC) for i in shown]
    tw = sum(d.textlength(p + ' ', font=fnt) for p, _ in parts); x = (W - tw) / 2; y = 1430
    for p, c in parts:
        d.text((x, y), p, font=fnt, fill=c, stroke_width=8, stroke_fill=(255, 255, 255), anchor='lm'); x += d.textlength(p + ' ', font=fnt)

def paste_hand(im, tip):
    if tip: im.paste(hand, (int(tip[0] - TIP[0]), int(tip[1] - TIP[1])), hand)

# ---------- scenes ----------
RAD4 = (84, 480, 320, 640); RAD1 = (70, 455, 200, 602)
def scene_draw(art, t, t0, dur):  # draw-on of an art scene
    p = ease((t - t0) / dur) if dur > 0 else 1
    if p >= 1: return ART[art], None
    m, tip = reveal_mask(p); return ART[art] * m, tip

def frame(t):
    tip = None; fills = []; ov = []
    if t < wt(10) - 0.05:  # A: dial close-up, «5» не працює
        ink, tip = scene_draw('sc2.png', t, 0, 1.6)
        def o(im, d):
            if True:
                a = ease((t - 0.3) / 0.5)
                d.text((540, 190), '«5» ≠ ШВИДШЕ', font=F(104), fill=RED, anchor='mm')
                d.line([(250, 270), (250 + 580 * a, 270)], fill=RED, width=10)
        ov.append(o)
    elif t < wt(25) - 0.05:  # B: code dial with temperatures
        ink = np.zeros((H, W)); t0 = wt(10)
        def o(im, d):
            cx, cy, R = 540, 700, 330; p = ease((t - t0) / 1.0)
            n = int(120 * p)
            pts = [(cx + R * math.cos(math.radians(90 - 360 * i / 120)), cy - R * math.sin(math.radians(90 - 360 * i / 120))) for i in range(n + 1)]
            if len(pts) > 1: d.line(pts, fill=INKC, width=9)
            if p >= 1: d.ellipse([cx - R + 60, cy - R + 60, cx + R - 60, cy + R - 60], outline=INKC, width=4)
            marks = ['*', '1', '2', '3', '4', '5']; temps = ['7°', '12°', '16°', '20°', '24°', '28°']
            for i, mk in enumerate(marks):
                if t < t0 + 0.9 + i * 0.12: break
                ang = math.radians(225 - i * 54)
                hi = (i == 3 and wt(17) - .05 <= t < wt(21) - .05) or (i == 4 and t >= wt(21) - .05)
                px, py = cx + math.cos(ang) * (R - 125), cy - math.sin(ang) * (R - 125)
                d.text((px, py), mk, font=F(96), fill=RED if hi else INKC, anchor='mm')
                d.text((cx + math.cos(ang) * (R + 70), cy - math.sin(ang) * (R + 70)), '≈' + temps[i], font=F(48), fill=RED if hi else (120, 120, 125), anchor='mm')
                if hi: d.ellipse([px - 75, py - 75, px + 75, py + 75], outline=RED, width=8)
            if t >= wt(17) - .05:
                d.text((540, 1200), '3 ≈ 20°C' if t < wt(21) - .05 else '4 ≈ 24°C', font=F(120), fill=RED, anchor='mm')
            d.text((540, 230), 'ЦИФРА = ТЕМПЕРАТУРА', font=F(70), fill=INKC, anchor='mm')
        ov.append(o)
        tip = None
    elif t < wt(44) - 0.05:  # C: warm room, valve cycle
        t0 = wt(25); ink, tip = scene_draw('sc4.png', t, t0, 1.4)
        m = rect_mask(RAD4)
        if t < wt(29): hot, temp = 0.0, 17
        elif t < wt(37): hot, temp = ease((t - wt(29)) / 0.6), 17 + 3 * ease((t - wt(29)) / (wt(37) - wt(29)))
        elif t < wt(41): hot, temp = 1 - ease((t - wt(37)) / 1.0), 20 - 1.5 * ease((t - wt(37)) / 2.0)
        else: hot, temp = ease((t - wt(41)) / 0.8), 18.5 + 0.5 * ease((t - wt(41)) / 1.5)
        col = tuple(int(BLUE[i] + (RED[i] - BLUE[i]) * hot) for i in range(3)) if t >= wt(37) else RED
        a = (hot if t < wt(37) else 1.0) * 0.85
        if t >= wt(29) or t >= wt(37): fills.append((m * a, col))
        def o(im, d):
            if t > t0 + 1.4:
                if hot > 0.3: heat(d, RAD4, t, hot)
                thermo(d, 160, 235, temp, RED if temp >= 19.5 else BLUE)
                lab = 'КЛАПАН ЗАКРИТО' if wt(37) <= t < wt(41) else 'КЛАПАН ВІДКРИТО'
                d.text((540, 130), lab, font=F(64), fill=RED if 'ЗАКР' in lab else (40, 140, 70), anchor='mm')
        ov.append(o)
    elif t < wt(58) - 0.05:  # D: window open, radiator always hot
        t0 = wt(44); ink, tip = scene_draw('sc5.png', t, t0, 1.0)
        fills.append((rect_mask(RAD4) * 0.85 * ease((t - t0 - 0.8) / 0.4), RED))
        def o(im, d):
            if t > t0 + 1.0:
                heat(d, RAD4, t, 1.0)
                for j in range(5):
                    ox = ((t * 320 + j * 140) % 520); y = 430 + j * 60
                    d.line([(860 - ox, y), (760 - ox, y + 14)], fill=BLUE, width=9)
                    d.polygon([(750 - ox, y + 16), (772 - ox, y - 2), (780 - ox, y + 32)], fill=BLUE)
                thermo(d, 160, 235, 15, BLUE)
                d.text((540, 130), 'ГРІЄ ВУЛИЦЮ', font=F(80), fill=BLUE, anchor='mm')
        ov.append(o)
    elif t < wt(64) - 0.05:  # E1: meter + bill
        t0 = wt(58); ink, tip = scene_draw('sc6.png', t, t0, 0.9)
        def o(im, d):
            if t > t0 + 0.6:
                v = 4500 + int(((t - t0) ** 1.8) * 9000)
                d.rounded_rectangle([170, 180, 610, 300], 18, fill=(255, 255, 255), outline=RED, width=7)
                d.text((390, 240), f'{v:06d}', font=F(84), fill=RED, anchor='mm')
        ov.append(o)
    elif t < wt(68) - 0.05:  # E2: building
        t0 = wt(64); ink, tip = scene_draw('sc7.png', t, t0, 0.9)
    elif t < wt(77) - 0.05:  # F: family warm, correct setting
        t0 = wt(68); ink, tip = scene_draw('sc1.png', t, t0, 1.2)
        fills.append((rect_mask(RAD1) * 0.8 * ease((t - t0 - 1.0) / 0.5), PINK))
        def o(im, d):
            if t > t0 + 1.2:
                heat(d, RAD1, t, 0.6, RED)
                d.text((540, 190), 'ТЕПЛО І БЕЗ ПЕРЕПЛАТ', font=F(66), fill=RED, anchor='mm')
        ov.append(o)
    else:  # G: end card
        ink = np.zeros((H, W)); t0 = wt(77)
        def o(im, d):
            p = ease((t - t0) / 0.8)
            d.text((540, 650), 'ПІДПИСУЙСЯ', font=F(110), fill=INKC, anchor='mm')
            d.text((540, 800), 'УСЕ ПРО', font=F(120), fill=INKC, anchor='mm')
            d.text((540, 950), 'ЕКОНОМІКУ', font=F(130), fill=RED, anchor='mm')
            if p < 1: d.rectangle([60 + 960 * p, 560, 1020, 1030], fill=tuple(PAPER.astype(int)))
        ov.append(o)
        tip = (60 + 960 * ease((t - t0) / 0.8), 1000) if t - t0 < 0.8 else None
    img = overlay(compose(ink, fills), lambda im, d: [f(im, d) for f in ov])
    d = ImageDraw.Draw(img); caption(d, t); paste_hand(img, tip)
    return img

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        for t in [0.8, 2.5, 5, 8.6, 10.8, 13, 15.8, 18, 21, 24.5, 26, 28, 31.5]:
            frame(t).resize((360, 640)).save(f'{S}/st_{t:05.1f}.jpg')
        sys.exit()
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'veryfast', f'{S}/visual.mp4'], stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)): p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close(); p.wait(); print('ok')
