"""Вертикальний шортс 1080x1920 з розділу довгого відео Attic Files.

  python tools/attic_short.py <spec.json>

spec:
{"name": "miv_s1", "src": "<dir розділу з voice.wav і words.json>", "w0": 0, "w1": 34,
 "img": "<dir фото>", "vid": "<dir відео>", "outro": "<dir з voice.wav/words.json аутро>",
 "bg": "#101010", "accent": "#ffd23f", "mood": "upbeat", "end_text": ["ПОВНА ІСТОРІЯ", "НА ATTIC FILES"],
 "scenes": [[індекс слова (відносно w0), "img:p02.jpg" або "vid:cook_1.mp4", "ТЕКСТ або порожньо", "АКЦЕНТ"], ...]}
Перша сцена видно з першого кадру (хук). Де в сцені є текст, субтитри вимкнені; де тексту немає, йдуть субтитри.
Без звукових ефектів: лише голос і музика.
"""
import html as H
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = json.load(open(sys.argv[1]))
src, job = Path(S["src"]), Path(S["job"])
job.mkdir(parents=True, exist_ok=True)
W = json.load(open(src / "words.json"))
w0, w1 = S["w0"], S["w1"]
t0 = max(0.0, W[w0][1] - 0.05)
t1 = W[w1 + 1][1] - 0.02 if w1 + 1 < len(W) else float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src / "voice.wav")]))
gap = 0.35
seg = t1 - t0
if S.get("outro"):
    o = Path(S["outro"])
    od = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(o / "voice.wav")]))
    # голос: відрізок розділу + пауза + аутро
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{seg:.3f}", "-i", str(src / "voice.wav"), "-i", str(o / "voice.wav"),
                    "-filter_complex", f"[0:a]aresample=48000,aformat=channel_layouts=mono,afade=t=out:st={seg - 0.08:.3f}:d=0.08,apad=pad_dur={gap}[a];[1:a]aresample=48000,aformat=channel_layouts=mono[b];[a][b]concat=n=2:v=0:a=1[o]",
                    "-map", "[o]", str(job / "voice.wav")], check=True)
    words = [[w, round(t - t0, 3)] for w, t in W[w0:w1 + 1]]
    outro_start = seg + gap
    words += [[w, round(t + outro_start, 3)] for w, t in json.load(open(o / "words.json"))]
    end = round(outro_start + od + 0.6, 2)
else:
    # трендовий шортс: увесь голос; фінальна картка з'являється на слові end_w ("Підписуйся")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{seg:.3f}", "-i", str(src / "voice.wav"), "-af", "aresample=48000", str(job / "voice.wav")], check=True)
    words = [[w, round(t - t0, 3)] for w, t in W[w0:w1 + 1]]
    outro_start = words[S["end_w"]][1] + 0.1
    end = round(seg + 0.6, 2)
json.dump(words, open(job / "words.json", "w"), ensure_ascii=False)
(job / "END.txt").write_text(str(end))
(job / "script.txt").write_text(" ".join(w for w, _ in words))

acc, bg = S.get("accent", "#ffd23f"), S.get("bg", "#101010")
subprocess.run([sys.executable, str(ROOT / "tools" / "kit_new.py"), str(job), str(job / "hf"), "--bg", bg], check=True, stdout=subprocess.DEVNULL)
(job / "hf" / "assets" / "img").mkdir(exist_ok=True)
(job / "hf" / "assets" / "vid").mkdir(exist_ok=True)
css = (f".full{{position:absolute;inset:0;overflow:hidden}}.full img,.full video{{width:100%;height:100%;object-fit:cover}}"
       f".dk{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.15) 40%,rgba(0,0,0,.25) 60%,rgba(0,0,0,.8))}}"
       f".bgr{{position:absolute;inset:-80px;background:radial-gradient(circle at 50% 42%,{S.get('bg2', '#2a2a2a')} 0,{bg} 70%)}}"
       f".tt{{position:absolute;left:70px;right:70px;text-align:center;font:700 130px/1.02 Osw;color:#fff;text-shadow:0 10px 40px rgba(0,0,0,.75)}}"
       f".tt b{{color:{acc};font-weight:700}}.sb{{position:absolute;left:90px;right:90px;text-align:center;font:800 54px/1.2 UI;color:#fff;text-shadow:0 6px 24px rgba(0,0,0,.8)}}")
secs, tl, caps_off = [], [], []
sc = S["scenes"] + [[None, "end", " ".join(S.get("end_text", ["ПОВНА ІСТОРІЯ", "НА ATTIC FILES"])), S.get("end_acc", "FILES")]]
starts = []
for k, (wi, media, text, accw) in enumerate(sc):
    starts.append(0.0 if k == 0 else (outro_start - 0.1 if wi is None else max(0.1, words[wi][1] - 0.08)))
starts.append(end)
TR = ["whip", "push", "zoom", "slideUp", "whip", "push"]
for k, (wi, media, text, accw) in enumerate(sc):
    sid = f"s{k + 1}"
    a, b = starts[k], starts[k + 1]
    vis = " style=\"visibility:visible\"" if k == 0 else ""
    body = ""
    if media == "end":
        body = "<div class='bgr'></div>"
    elif media.startswith("img:"):
        f = media[4:]
        shutil.copy(Path(S["img"]) / f, job / "hf" / "assets" / "img" / f)
        body = f"<div class='full' id='f{k}'><img src='assets/img/{f}' style='object-position:{S.get('pos', {}).get(f, 'center')}'></div><div class='dk'></div>"
        tl.append(f"Kit.drift(tl, '#f{k} img', {a:.3f}, {b:.3f}, {{to: 1.14}});")
    elif media.startswith("vid:"):
        f = media[4:]
        shutil.copy(Path(S["vid"]) / f, job / "hf" / "assets" / "vid" / f)
        body = (f"<div class='full' id='f{k}'><video class='clip' muted playsinline data-start='{a:.3f}' data-duration='{b - a + .5:.3f}' data-media-start='0' "
                f"src='assets/vid/{f}'></video></div><div class='dk'></div>")
        tl.append(f"Kit.drift(tl, '#f{k} video', {a:.3f}, {b:.3f}, {{to: 1.1}});")
    if text:
        parts = [f"<b>{H.escape(w)}</b>" if accw and w.strip('«»,.?!').upper().startswith(accw.upper()) else H.escape(w) for w in text.split()]
        top = 760 if media == "end" else 520
        body += f"<div class='tt' id='t{k}' style='top:{top}px'>{' '.join(parts)}</div>"
        if k == 0:
            tl.append(f"tl.fromTo('#t{k}', {{scale: 1.1}}, {{scale: 1, duration: 1, ease: 'power2.out', immediateRender: false}}, 0);")
        else:
            tl.append(f"Kit.in(tl, '#t{k}', {a + .05:.3f}, '{'pop' if media == 'end' else 'rise'}');")
        caps_off.append((a - .05 if k else 0, b - .06))
    secs.append(f"    <section class=\"scene\" id=\"{sid}\"{vis}>{body}</section>")
    if k:
        tl.append(f"Kit.cut(tl, '#s{k}', '#{sid}', {a - .06:.3f}, '{TR[k % len(TR)]}');")
kw = json.dumps([w.lower() for w in S.get("keywords", [])], ensure_ascii=False)
tl.insert(0, f"Kit.captions(tl, {{keywords: {kw}, end: END}});")
for a, b in caps_off:
    tl.append(f"Kit.capsOff(tl, {max(0, a):.3f}, {b if b < end - .1 else 'null'});")
tl.append(f"Kit.loop(tl, '#s{len(sc)}', '#s1', END, 'zoom');")
(job / "css.txt").write_text(css)
(job / "scenes.txt").write_text("<!--SCENES-->\n" + "\n".join(secs) + "\n<!--/SCENES-->")
(job / "tl.txt").write_text("//TIMELINE\n" + "\n".join(tl) + "\n///TIMELINE")
print("job", job, "end", end, "scenes", len(sc))
