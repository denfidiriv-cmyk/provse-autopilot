"""Довге горизонтальне відео 1920x1080 (канал Attic Files): біти -> кадри (Playwright) -> кліпи (ffmpeg) -> склейка.

  python tools/longform.py <beats.json> <out_dir>

beats.json: {"parts": [{"job": "<dir з voice.wav і words.json>", "beats": [[anchor, type, {params}], ...]}], "img": "<dir з фото>"}
anchor: слово (або початок слова), з якого починається біт; шукається після попереднього якоря.
type: photo | file | big | chapter | intro
Кожен кліп: повільний наїзд (zoompan) + поява тексту через 0,35 с. Склейки жорсткі, як у відео-есеях.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "templates" / "kit" / "assets" / "fonts"
FPS = 25

CSS = """
@font-face{font-family:Osw;src:url(FONTS/Oswald-700.woff)}
@font-face{font-family:UI;src:url(FONTS/inter-cyrillic-800-normal.woff2);unicode-range:U+0400-045F,U+0490-0491,U+2116}
@font-face{font-family:UI;src:url(FONTS/inter-latin-800-normal.woff2)}
@font-face{font-family:Mono;src:url(FONTS/JBMono-700.woff)}
*{margin:0;box-sizing:border-box}
body{width:1920px;height:1080px;overflow:hidden;background:#15130f;font-family:UI;color:#f3ead7;position:relative}
.desk{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,#3a2f22 0,#211b14 60%,#100d09 100%)}
.grain{position:absolute;inset:0;opacity:.16;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2'/></filter><rect width='400' height='400' filter='url(%23n)'/></svg>")}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,transparent 50%,rgba(0,0,0,.7) 100%)}
.bgp{position:absolute;inset:0;background-size:cover;background-position:center}
.dim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.15),rgba(0,0,0,.25) 55%,rgba(0,0,0,.75))}
.tag{position:absolute;left:90px;bottom:90px;background:#e3b341;color:#15130f;font:700 54px/1 Osw;padding:16px 28px;letter-spacing:2px;transform:rotate(-1.5deg);box-shadow:0 10px 30px rgba(0,0,0,.5)}
.pol{position:absolute;background:#f4efe3;padding:22px 22px 70px;box-shadow:0 30px 70px rgba(0,0,0,.7)}
.pol img{display:block;object-fit:cover}
.tape{position:absolute;width:190px;height:52px;background:rgba(230,220,180,.75);top:-24px;left:50%;margin-left:-95px;transform:rotate(-4deg)}
.stamp{position:absolute;border:10px solid #c62828;color:#c62828;font:700 84px/1 Osw;padding:14px 34px;letter-spacing:3px;transform:rotate(-8deg);background:rgba(244,239,227,.08);text-transform:uppercase}
.big{position:absolute;left:0;right:0;text-align:center;font:700 200px/1 Osw;color:#e3b341;text-shadow:0 16px 50px rgba(0,0,0,.6)}
.sub{position:absolute;left:160px;right:160px;text-align:center;font:800 54px/1.25 UI;color:#f3ead7;text-shadow:0 6px 24px rgba(0,0,0,.7)}
.chap{position:absolute;left:0;right:0;top:330px;text-align:center}
.chap .no{font:700 50px/1 Mono;color:#e3b341;letter-spacing:10px}
.chap .t{font:700 170px/1.05 Osw;color:#f3ead7;margin-top:30px;letter-spacing:4px}
.folder{position:absolute;left:560px;top:230px;width:800px;height:560px;background:#c9962a;border-radius:20px;box-shadow:0 40px 80px rgba(0,0,0,.6)}
.folder:before{content:"";position:absolute;left:0;top:-50px;width:280px;height:70px;background:#c9962a;border-radius:20px 20px 0 0}
"""


def html(body, extra=""):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS.replace('FONTS', FONTS.as_uri())}{extra}</style></head><body>{body}<div class='grain'></div><div class='vig'></div></body></html>"


def layers(t, p, img):
    """Повертає (base_html, full_html): base без тексту, full з текстом."""
    if t == "photo":
        src = (img / p["img"]).as_uri()
        base = f"<div class='bgp' style=\"background-image:url('{src}');background-position:{p.get('pos','center')}\"></div><div class='dim'></div>"
        txt = f"<div class='tag'>{p['tag']}</div>" if p.get("tag") else ""
        return html(base), html(base + txt)
    if t == "file":
        src = (img / p["img"]).as_uri()
        rot = p.get("rot", -3)
        w, h = p.get("w", 980), p.get("h", 680)
        base = (f"<div class='desk'></div><div class='pol' style='left:{(1920-w)//2-60}px;top:{(1080-h)//2-40}px;transform:rotate({rot}deg)'>"
                f"<div class='tape'></div><img src='{src}' style='width:{w}px;height:{h}px;object-position:{p.get('pos','center')}'></div>")
        txt = f"<div class='stamp' style='right:150px;bottom:140px'>{p['stamp']}</div>" if p.get("stamp") else ""
        return html(base), html(base + txt)
    if t == "big":
        bg = ""
        if p.get("img"):
            bg = f"<div class='bgp' style=\"background-image:url('{(img / p['img']).as_uri()}');filter:blur(6px) brightness(.35)\"></div>"
        else:
            bg = "<div class='desk'></div>"
        size = p.get("size", 200)
        top = 380 if p.get("sub") else 430
        txt = f"<div class='big' style='top:{top - size // 3}px;font-size:{size}px'>{p['text']}</div>"
        if p.get("sub"):
            txt += f"<div class='sub' style='top:{top + size * 2 // 3 + 20}px'>{p['sub']}</div>"
        return html(bg), html(bg + txt)
    if t == "chapter":
        base = "<div class='desk'></div><div class='folder'></div>"
        txt = f"<div class='chap'><div class='no'>{p.get('no','СПРАВА')}</div><div class='t'>{p['text']}</div></div>"
        return html(base), html(base + txt)
    if t == "intro":
        av = (img / p["img"]).as_uri()
        base = f"<div class='desk'></div><img src='{av}' style='position:absolute;left:660px;top:120px;width:600px;height:600px;border-radius:50%;box-shadow:0 30px 80px rgba(0,0,0,.7)'>"
        txt = "<div class='big' style='top:760px;font-size:150px;color:#f3ead7'>ATTIC <span style='color:#e3b341'>FILES</span></div>"
        return html(base), html(base + txt)
    raise ValueError(t)


def norm(w):
    return re.sub(r"[^\wʼ'’-]", "", w.lower())


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    img = Path(cfg["img"])
    from playwright.sync_api import sync_playwright
    clips, audio, offset = [], [], 0.0
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(viewport={"width": 1920, "height": 1080})
        n = 0
        for part in cfg["parts"]:
            job = Path(part["job"])
            words = json.loads((job / "words.json").read_text(encoding="utf-8"))
            dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(job / "voice.wav")]))
            dur += part.get("tail", 0.6)
            starts, pos = [], 0
            for anchor, _, _ in part["beats"]:
                a = norm(anchor)
                k = next((i for i in range(pos, len(words)) if norm(words[i][0]).startswith(a)), None)
                if k is None:
                    raise SystemExit(f"не знайшов якір '{anchor}' після слова {pos} у {job}")
                starts.append(0.0 if not starts else max(0.0, words[k][1] - .12)); pos = k + 1
            starts.append(dur)
            for i, (_, t, p) in enumerate(part["beats"]):
                d = round(starts[i + 1] - starts[i], 3)
                b, f = layers(t, p, img)
                for nm, h in (("b", b), ("f", f)):
                    hp = out / f"{n:03d}{nm}.html"; hp.write_text(h, encoding="utf-8")
                    pg.goto(hp.as_uri()); pg.wait_for_timeout(250)
                    pg.screenshot(path=str(out / f"{n:03d}{nm}.png"))
                z = p.get("zoom", .06)
                frames = max(1, int(d * FPS))
                clip = out / f"{n:03d}.mp4"
                flt = (f"[1:v]format=rgba,fade=in:st=0.35:d=0.3:alpha=1[t];[0:v][t]overlay,scale=2880:1620,"
                       f"zoompan=z='1+{z}*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},format=yuv420p")
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-t", str(d), "-i", str(out / f"{n:03d}b.png"),
                                "-loop", "1", "-framerate", str(FPS), "-t", str(d), "-i", str(out / f"{n:03d}f.png"),
                                "-filter_complex", flt, "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(clip)], check=True)
                clips.append(clip); n += 1
            audio.append((job / "voice.wav", offset, dur)); offset += dur
        br.close()
    (out / "list.txt").write_text("".join(f"file '{c}'\n" for c in clips))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(out / "list.txt"), "-c", "copy", str(out / "video.mp4")], check=True)
    # голос: частини одна за одною з паузами-хвостами
    inputs, fl = [], []
    for i, (wav, off, d) in enumerate(audio):
        inputs += ["-i", str(wav)]
        fl.append(f"[{i}:a]aresample=48000,apad=whole_dur={d:.3f}[a{i}]")
    fl.append("".join(f"[a{i}]" for i in range(len(audio))) + f"concat=n={len(audio)}:v=0:a=1[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fl), "-map", "[v]", str(out / "voice_all.wav")], check=True)
    print("готово:", out / "video.mp4", "тривалість", round(offset, 1), "с")


if __name__ == "__main__":
    main()
