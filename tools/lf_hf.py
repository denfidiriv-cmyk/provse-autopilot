"""Розділ довгого відео 1920x1080 для Attic Files: біти -> проєкт hyperframes з плавною GSAP-анімацією.

  python tools/lf_hf.py <chapter.json> <project_dir>

chapter.json:
{"job": "<dir з voice.wav, words.json>", "img": "<dir фото>", "theme": "asia", "music": "<файл музики>", "music_start": 0,
 "beats": [[anchor, type, {params}], ...]}
Типи бітів: photo, polaroid, big, chapter, versus, timeline, list, mascot.
Склейки між бітами чергуються (wipe, slide, zoom, flip, iris, push) — без трясіння камери.
Після генерації: python tools/kit_render.py <job> <project_dir> <job>/mix.wav  (mix.wav робить цей скрипт).
"""
import html as H
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / "templates" / "kit"

THEMES = {
    # bg, panel, ink, accent, accent2, font для заголовків, фон-патерн
    "hook":    dict(bg="#0b0b0d", ink="#f5f1e8", acc="#ff3b30", acc2="#ffd60a", head="Osw", pat="scan"),
    "asia":    dict(vacc="#ff4d5e", bg="#f3e6cf", ink="#2a1b12", acc="#c8102e", acc2="#1f3a5f", head="PF",  pat="sun"),
    "austria": dict(vacc="#8ec5ff", bg="#dfe8f2", ink="#0e1f3a", acc="#1e4aa8", acc2="#c0c7d1", head="Osw", pat="stripes"),
    "news":    dict(vacc="#ff5a4f", bg="#efe9dc", ink="#1b1b1b", acc="#b3121f", acc2="#1b1b1b", head="PF",  pat="paper"),
    "monster": dict(bg="#070907", ink="#e9ffe9", acc="#6bff3c", acc2="#ffffff", head="Osw", pat="claws"),
    "ukraine2000s": dict(bg="#0f3d91", ink="#ffffff", acc="#ffd500", acc2="#7fd3ff", head="Osw", pat="y2k"),
    "war":     dict(bg="#1c1f17", ink="#e6e2d3", acc="#c9b37e", acc2="#7d8a5a", head="Osw", pat="dust"),
    "health":  dict(bg="#eef6f6", ink="#0f2d33", acc="#e63946", acc2="#1d7f86", head="Osw", pat="grid"),
}

CSS = """
@font-face{font-family:Osw;src:url(assets/fonts/Oswald-700.woff)}
@font-face{font-family:PF;src:url(assets/fonts/PlayfairDisplay-700.woff)}
@font-face{font-family:JB;src:url(assets/fonts/JBMono-700.woff)}
@font-face{font-family:Cav;src:url(assets/fonts/Caveat-700.woff)}
@font-face{font-family:UI;src:url(assets/fonts/inter-cyrillic-800-normal.woff2);unicode-range:U+0400-045F,U+0490-0491,U+2116}
@font-face{font-family:UI;src:url(assets/fonts/inter-latin-800-normal.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:var(--bg)}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:var(--bg);font-family:UI;color:var(--ink)}
.sc{position:absolute;inset:0;visibility:hidden;overflow:hidden;background:var(--bg)}
.pat{position:absolute;inset:-200px}
.pat.scan{background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 2px,transparent 2px 6px),radial-gradient(circle at 50% 50%,#2a0d0d,#0b0b0d 70%)}
.pat.sun{background:repeating-linear-gradient(0deg,rgba(0,0,0,.025) 0 2px,transparent 2px 9px),radial-gradient(circle at 50% 50%,#f8eedc,#e6d0a8)}
.pat.stripes{background:repeating-linear-gradient(115deg,rgba(30,74,168,.08) 0 40px,transparent 40px 120px),linear-gradient(180deg,#eef3f9,#cfdbea)}
.pat.paper{background:repeating-linear-gradient(0deg,rgba(0,0,0,.04) 0 1px,transparent 1px 38px),#efe9dc}
.pat.claws{background:radial-gradient(circle at 50% 50%,#0f2a0f,#050705 70%)}
.pat.y2k{background:radial-gradient(circle at 30% 30%,#2f6fe0,#0f3d91 50%,#071d4a)}
.pat.dust{background:radial-gradient(circle at 50% 40%,#2b3022,#14160f 75%)}
.pat.grid{background:linear-gradient(rgba(29,127,134,.08) 2px,transparent 2px) 0 0/80px 80px,linear-gradient(90deg,rgba(29,127,134,.08) 2px,transparent 2px) 0 0/80px 80px,#eef6f6}
.grain{position:absolute;inset:-100px;opacity:.12;pointer-events:none;z-index:90;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='300' height='300' filter='url(%23n)'/></svg>")}
.vig{position:absolute;inset:0;pointer-events:none;z-index:89;background:radial-gradient(ellipse at 50% 50%,transparent 55%,rgba(0,0,0,.55) 100%)}
.ph{position:absolute;inset:0;overflow:hidden}
.ph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;will-change:transform}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.05),rgba(0,0,0,.15) 55%,rgba(0,0,0,.7))}
.tag{position:absolute;left:100px;bottom:110px;font:700 64px/1 var(--head);padding:18px 32px;background:var(--acc);color:#fff;letter-spacing:1px}
.tag2{position:absolute;left:100px;bottom:200px;font:800 46px/1 UI;color:#fff;background:rgba(0,0,0,.6);padding:12px 20px}
.pol{position:absolute;background:#faf6ee;padding:24px 24px 80px;box-shadow:0 40px 80px rgba(0,0,0,.45)}
.pol img{display:block;object-fit:cover}
.pol .cap{position:absolute;left:0;right:0;bottom:18px;text-align:center;font:700 44px/1 Cav;color:#333}
.tape{position:absolute;width:200px;height:54px;background:rgba(240,228,180,.8);top:-26px;left:50%;margin-left:-100px;transform:rotate(-4deg)}
.stamp{position:absolute;border:10px solid var(--acc);color:var(--acc);font:700 80px/1 Osw;padding:12px 34px;letter-spacing:3px;text-transform:uppercase}
.bigt{position:absolute;left:120px;right:120px;text-align:center;font:700 200px/1.02 var(--head);color:var(--ink)}
.bigt .w{display:inline-block;margin:0 .12em}
.bigt .a{color:var(--acc)}
.vt .a{color:var(--vacc)}
.subt{position:absolute;left:220px;right:220px;text-align:center;font:800 52px/1.25 UI;color:var(--ink);opacity:.9}
.hl{position:absolute;height:26px;background:var(--acc2);opacity:.35;transform-origin:0 50%}
.chapno{position:absolute;left:140px;top:250px;font:700 60px/1 JB;color:var(--acc);letter-spacing:12px}
.chapt{position:absolute;left:140px;right:140px;top:340px;font:700 210px/1.02 var(--head);color:var(--ink)}
.chapt .l{display:inline-block}
.chapbar{position:absolute;left:140px;top:600px;width:520px;height:18px;background:var(--acc);transform-origin:0 50%}
.vs{position:absolute;top:250px;width:640px;height:520px;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:30px;background:rgba(255,255,255,.08);border:6px solid var(--acc)}
.vs b{font:700 150px/1 var(--head);color:var(--ink)}
.vs i{font:800 46px/1.2 UI;font-style:normal;color:var(--ink);opacity:.85;margin-top:20px;text-align:center;padding:0 30px}
.vsx{position:absolute;left:880px;top:430px;width:160px;height:160px;border-radius:50%;background:var(--acc);color:#fff;font:700 80px/160px Osw;text-align:center}
.tline{position:absolute;left:160px;right:160px;top:560px;height:10px;background:var(--ink);transform-origin:0 50%;opacity:.8}
.tdot{position:absolute;top:530px;width:70px;height:70px;margin-left:-35px;border-radius:50%;background:var(--acc);box-shadow:0 0 0 12px rgba(0,0,0,.08)}
.tlab{position:absolute;top:620px;width:360px;margin-left:-180px;text-align:center;font:700 64px/1.05 var(--head);color:var(--ink)}
.tlab small{display:block;font:800 30px/1.2 UI;opacity:.8;margin-top:8px}
.li{position:absolute;left:330px;right:330px;height:140px;display:flex;align-items:center;gap:44px;font:800 76px/1 UI;color:var(--ink);border-bottom:4px solid rgba(128,128,128,.3)}
.li b{font:700 84px/1 var(--head);color:var(--acc);min-width:300px}
.masc{position:absolute;width:420px;height:420px;border-radius:50%;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.45)}
.masc img{width:100%;height:100%}
.bub{position:absolute;max-width:900px;background:#fff;color:#111;font:800 66px/1.2 UI;padding:40px 52px;border-radius:40px;box-shadow:0 20px 50px rgba(0,0,0,.3)}
"""

TRANS = ["slide", "cut", "push", "zoom", "cut", "wipe", "slide", "cut"]


def esc(s):
    return H.escape(str(s))


def words_html(text, acc_words=()):
    out = []
    for w in str(text).split():
        cls = "w a" if any(w.lower().startswith(a.lower()) for a in acc_words) else "w"
        out.append(f"<span class='{cls}'>{esc(w)}</span>")
    return " ".join(out)


def scene(i, t, p, img, S=0.0, D=0.0):
    """HTML сцени + JS-анімації (функція від часу початку s і тривалості d)."""
    sid = f"b{i}"
    pat = "<div class='pat {pat}'></div>"
    if t == "video":
        vid = f"<video class='clip' id='v{i}' muted playsinline data-start='{S:.3f}' data-duration='{D:.3f}' data-media-start='{p.get('from', 0)}' src='assets/vid/{p['vid']}' style='position:absolute;inset:0;width:100%;height:100%;object-fit:cover'></video>"
        body = (f"<div class='ph vw'>{vid}</div><div class='shade'></div>"
                + (f"<div class='tag2'>{esc(p['kicker'])}</div>" if p.get("kicker") else "")
                + (f"<div class='tag'>{esc(p['tag'])}</div>" if p.get("tag") else "")
                + (f"<div class='bigt vt' style='top:{p.get('top', 380)}px;font-size:{p.get('size', 150)}px;color:#fff;text-shadow:0 10px 40px rgba(0,0,0,.8)'>{words_html(p['text'], p.get('acc', []))}</div>" if p.get("text") else ""))
        js = (f"tl.fromTo('#{sid} .vw',{{scale:1.02}},{{scale:1.1,duration:d,ease:'none',immediateRender:false}},s);"
              f"tl.fromTo('#{sid} .tag',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:.55,ease:'expo.out',immediateRender:false}},s+.45);"
              f"tl.fromTo('#{sid} .tag2',{{y:24,opacity:0,filter:'blur(8px)'}},{{y:0,opacity:1,filter:'blur(0px)',duration:.55,ease:'power3.out',immediateRender:false}},s+.75);"
              f"tl.fromTo('#{sid} .bigt .w',{{yPercent:55,opacity:0,filter:'blur(14px)'}},{{yPercent:0,opacity:1,filter:'blur(0px)',duration:.6,ease:'power3.out',stagger:.07,immediateRender:false}},s+.3);")
    elif t == "photo":
        src = f"assets/img/{p['img']}"
        body = (f"<div class='ph'><img src='{src}' style='object-position:{p.get('pos','center')}'></div><div class='shade'></div>"
                + (f"<div class='tag2'>{esc(p['kicker'])}</div>" if p.get("kicker") else "")
                + (f"<div class='tag'>{esc(p['tag'])}</div>" if p.get("tag") else ""))
        dx = p.get("dx", 60 if i % 2 else -60)
        js = (f"tl.fromTo('#{sid} .ph img',{{scale:1.04,x:0}},{{scale:1.16,x:{dx},duration:d,ease:'none',immediateRender:false}},s);"
              f"tl.fromTo('#{sid} .tag',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:.55,ease:'expo.out',immediateRender:false}},s+.45);"
              f"tl.fromTo('#{sid} .tag2',{{y:24,opacity:0,filter:'blur(8px)'}},{{y:0,opacity:1,filter:'blur(0px)',duration:.55,ease:'power3.out',immediateRender:false}},s+.75);")
    elif t == "polaroid":
        src = f"assets/img/{p['img']}"
        w, h = p.get("w", 900), p.get("h", 620)
        rot = p.get("rot", -4)
        left, top = (1920 - w) // 2 - 48 + p.get("x", 0), (1080 - h) // 2 - 50
        body = (pat + f"<div class='pol' style='left:{left}px;top:{top}px;transform:rotate({rot}deg)'><div class='tape'></div>"
                f"<img src='{src}' style='width:{w}px;height:{h}px;object-position:{p.get('pos','center')}'>"
                + (f"<div class='cap'>{esc(p['cap'])}</div>" if p.get("cap") else "") + "</div>"
                + (f"<div class='stamp' style='left:{left + w // 2 - 60}px;top:{top + h - 150}px;transform:rotate(-9deg);background:rgba(250,246,238,.85);white-space:nowrap'>{esc(p['stamp'])}</div>" if p.get("stamp") else ""))
        js = (f"tl.fromTo('#{sid} .pol',{{scale:1.3,opacity:0,y:40,rotation:{rot + 9}}},{{scale:1,opacity:1,y:0,rotation:{rot},duration:.7,ease:'power3.out',immediateRender:false}},s+.05);"
              f"tl.fromTo('#{sid} .pol img',{{scale:1}},{{scale:1.1,duration:d,ease:'none',immediateRender:false}},s);"
              f"tl.fromTo('#{sid} .pat',{{x:0}},{{x:-120,duration:d,ease:'none',immediateRender:false}},s);"
              f"tl.fromTo('#{sid} .stamp',{{scale:2.2,opacity:0}},{{scale:1,opacity:1,duration:.28,ease:'power4.in',immediateRender:false}},s+.95);")
    elif t == "big":
        bgimg = f"<div class='ph' style='filter:blur(5px) brightness(.45)'><img src='assets/img/{p['img']}'></div>" if p.get("img") else pat
        size = p.get("size", 190)
        top = p.get("top", 330 if p.get("sub") else 400)
        body = (bgimg + f"<div class='bigt' style='top:{top}px;font-size:{size}px;{'color:#fff' if p.get('img') else ''}'>{words_html(p['text'], p.get('acc', []))}</div>"
                + (f"<div class='subt' style='top:{top + int(size * 1.15) + 40}px;{'color:#fff' if p.get('img') else ''}'>{esc(p['sub'])}</div>" if p.get("sub") else ""))
        js = (f"tl.fromTo('#{sid} .bigt .w',{{yPercent:55,opacity:0,filter:'blur(14px)'}},{{yPercent:0,opacity:1,filter:'blur(0px)',duration:.6,ease:'power3.out',stagger:.08,immediateRender:false}},s+.15);"
              f"tl.fromTo('#{sid} .subt',{{y:24,opacity:0,filter:'blur(8px)'}},{{y:0,opacity:1,filter:'blur(0px)',duration:.55,ease:'power3.out',immediateRender:false}},s+.7);"
              f"tl.fromTo('#{sid} .bigt',{{scale:1}},{{scale:1.06,duration:d,ease:'none',immediateRender:false}},s);"
              f"tl.fromTo('#{sid} .ph img, #{sid} .pat',{{scale:1.05,x:0}},{{scale:1.15,x:-50,duration:d,ease:'none',immediateRender:false}},s);")
        if p.get("count"):
            a, b, fmt = p["count"]
            js += (f"(function(){{const o={{v:{a}}};const el=document.querySelector('#{sid} .bigt .w');"
                   f"tl.to(o,{{v:{b},duration:{p.get('cdur',1.4)},ease:'power2.out',onUpdate:()=>{{el.textContent='{fmt}'.replace('#',Math.round(o.v).toString().replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,' '))}}}},s+.2);}})();")
    elif t == "chapter":
        letters = "".join(f"<span class='l'>{esc(ch) if ch != ' ' else '&nbsp;'}</span>" for ch in p["text"])
        body = pat + f"<div class='chapno'>{esc(p.get('no', ''))}</div><div class='chapt'>{letters}</div><div class='chapbar'></div>"
        js = (f"tl.fromTo('#{sid} .chapt .l',{{yPercent:110,opacity:0}},{{yPercent:0,opacity:1,duration:.5,ease:'power4.out',stagger:.035,immediateRender:false}},s+.2);"
              f"tl.fromTo('#{sid} .chapno',{{x:-80,opacity:0}},{{x:0,opacity:1,duration:.5,ease:'power2.out',immediateRender:false}},s+.05);"
              f"tl.fromTo('#{sid} .chapbar',{{scaleX:0}},{{scaleX:1,duration:.8,ease:'expo.out',immediateRender:false}},s+.6);"
              f"tl.fromTo('#{sid} .pat',{{scale:1,rotation:0}},{{scale:1.12,rotation:2,duration:d,ease:'none',immediateRender:false}},s);")
    elif t == "versus":
        body = (pat + f"<div class='vs' style='left:180px'><b>{esc(p['a'])}</b><i>{esc(p.get('ai',''))}</i></div>"
                f"<div class='vs' style='left:1100px'><b>{esc(p['b'])}</b><i>{esc(p.get('bi',''))}</i></div><div class='vsx'>VS</div>")
        js = (f"tl.fromTo('#{sid} .vs:nth-of-type(2)',{{x:-900}},{{x:0,duration:.7,ease:'expo.out',immediateRender:false}},s+.1);"
              f"tl.fromTo('#{sid} .vs:nth-of-type(3)',{{x:900}},{{x:0,duration:.7,ease:'expo.out',immediateRender:false}},s+{p.get('bt',.5)});"
              f"tl.fromTo('#{sid} .vsx',{{scale:0,rotation:-180}},{{scale:1,rotation:0,duration:.5,ease:'back.out(2)',immediateRender:false}},s+.9);")
    elif t == "timeline":
        pts = p["points"]
        n = len(pts)
        body = pat + "<div class='tline'></div>"
        js = f"tl.fromTo('#{sid} .tline',{{scaleX:0}},{{scaleX:1,duration:1.2,ease:'power2.inOut',immediateRender:false}},s+.1);"
        for k, (lab, sub) in enumerate(pts):
            x = 160 + int((1600) * (k / max(1, n - 1))) if n > 1 else 960
            body += f"<div class='tdot' style='left:{x}px'></div><div class='tlab' style='left:{x}px'>{esc(lab)}<small>{esc(sub)}</small></div>"
            dt = p.get("times", [None] * n)[k]
            when = f"s+{0.35 + k * 0.35}" if dt is None else f"{dt}"
            js += (f"tl.fromTo('#{sid} .tdot:nth-of-type({k * 2 + 3})',{{scale:0}},{{scale:1,duration:.4,ease:'back.out(3)',immediateRender:false}},{when});"
                   f"tl.fromTo('#{sid} .tlab:nth-of-type({k * 2 + 4})',{{y:40,opacity:0}},{{y:0,opacity:1,duration:.4,ease:'power2.out',immediateRender:false}},{when}+.1);")
    elif t == "list":
        body = pat + (f"<div class='bigt' style='top:150px;font-size:130px'>{words_html(p['title'], p.get('acc', []))}</div>" if p.get("title") else "")
        js = (f"tl.fromTo('#{sid} .bigt .w',{{yPercent:55,opacity:0,filter:'blur(12px)'}},{{yPercent:0,opacity:1,filter:'blur(0px)',duration:.55,stagger:.07,ease:'power3.out',immediateRender:false}},s+.1);")
        for k, (a, b) in enumerate(p["items"]):
            body += f"<div class='li' style='top:{360 + k * 160}px'><b>{esc(a)}</b><span>{esc(b)}</span></div>"
            js += f"tl.fromTo('#{sid} .li:nth-of-type({k + (3 if p.get('title') else 2)})',{{x:-60,opacity:0,filter:'blur(8px)'}},{{x:0,opacity:1,filter:'blur(0px)',duration:.5,ease:'power3.out',immediateRender:false}},s+{0.5 + k * p.get('gap', .45)});"
    elif t == "mascot":
        body = (pat + f"<div class='masc' style='left:180px;top:330px'><img src='assets/img/avatar.png'></div>"
                f"<div class='bub' style='left:690px;top:300px'>{esc(p['text'])}</div>")
        js = (f"tl.fromTo('#{sid} .masc',{{scale:0,rotation:-30}},{{scale:1,rotation:0,duration:.6,ease:'back.out(2)',immediateRender:false}},s+.1);"
              f"tl.fromTo('#{sid} .bub',{{scale:.3,opacity:0,transformOrigin:'0% 50%'}},{{scale:1,opacity:1,duration:.45,ease:'back.out(2)',immediateRender:false}},s+.45);"
              f"tl.fromTo('#{sid} .masc',{{y:0}},{{y:-18,duration:.5,yoyo:true,repeat:Math.max(1,Math.floor(d/0.5)-2),ease:'sine.inOut',immediateRender:false}},s+.7);")
    else:
        raise ValueError(t)
    if t in ("versus", "timeline", "list", "mascot"):
        js += f"tl.fromTo('#{sid} .pat',{{scale:1,x:0}},{{scale:1.1,x:-80,duration:d,ease:'none',immediateRender:false}},s);"
    return f"<section class='sc' id='{sid}'>{body}</section>", js


def trans_js(a, b, s, kind):
    A, B = f"#b{a}", f"#b{b}"
    d = .55
    js = f"tl.set('{B}',{{visibility:'visible'}},{s:.3f});"
    if kind == "wipe":
        js += f"tl.fromTo('{B}',{{clipPath:'inset(0 0 0 100%)'}},{{clipPath:'inset(0 0 0 0%)',duration:{d},ease:'power3.inOut',immediateRender:false}},{s:.3f});"
    elif kind == "slide":
        js += (f"tl.fromTo('{B}',{{xPercent:100}},{{xPercent:0,duration:{d},ease:'expo.inOut',immediateRender:false}},{s:.3f});"
               f"tl.fromTo('{A}',{{xPercent:0}},{{xPercent:-35,duration:{d},ease:'expo.inOut',immediateRender:false}},{s:.3f});")
    elif kind == "zoom":
        js += (f"tl.fromTo('{B}',{{scale:1.12,opacity:0,filter:'blur(12px)'}},{{scale:1,opacity:1,filter:'blur(0px)',duration:{d},ease:'power3.out',immediateRender:false}},{s:.3f});"
               f"tl.fromTo('{A}',{{scale:1}},{{scale:.85,duration:{d},ease:'power3.in',immediateRender:false}},{s:.3f});")
    elif kind == "flip":
        js += f"tl.fromTo('{B}',{{rotationY:-90,transformPerspective:2000,opacity:.4}},{{rotationY:0,opacity:1,duration:{d + .1},ease:'power3.out',immediateRender:false}},{s:.3f});"
    elif kind == "iris":
        js += f"tl.fromTo('{B}',{{clipPath:'circle(0% at 50% 50%)'}},{{clipPath:'circle(75% at 50% 50%)',duration:{d + .1},ease:'power2.inOut',immediateRender:false}},{s:.3f});"
    elif kind == "push":
        js += (f"tl.fromTo('{B}',{{yPercent:100}},{{yPercent:0,duration:{d},ease:'power4.inOut',immediateRender:false}},{s:.3f});"
               f"tl.fromTo('{A}',{{yPercent:0}},{{yPercent:-100,duration:{d},ease:'power4.inOut',immediateRender:false}},{s:.3f});")
    elif kind == "cut":
        d = 0
    elif kind == "flash":
        js += f"tl.fromTo('{B}',{{filter:'brightness(3)'}},{{filter:'brightness(1)',duration:.35,ease:'power2.out',immediateRender:false}},{s:.3f});"
        d = 0
    js += f"tl.set('{A}',{{visibility:'hidden'}},{s + d + .12:.3f});"
    return js


def norm(w):
    return re.sub(r"[^\wʼ'’-]", "", w.lower())


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    proj = Path(sys.argv[2])
    job = Path(cfg["job"])
    th = THEMES[cfg["theme"]]
    if proj.exists():
        shutil.rmtree(proj)
    shutil.copytree(KIT, proj, ignore=shutil.ignore_patterns("EXAMPLE.html", "README.md"))
    (proj / "assets" / "img").mkdir(exist_ok=True); (proj / "assets" / "sound").mkdir(exist_ok=True)
    img = Path(cfg["img"])
    used = {b[2].get("img") for b in cfg["beats"]} | {"avatar.png"}
    (proj / "assets" / "vid").mkdir(exist_ok=True)
    for b in cfg["beats"]:
        if b[2].get("vid"):
            shutil.copy(Path(cfg["vid"]) / b[2]["vid"], proj / "assets" / "vid" / b[2]["vid"])
    for u in used:
        if u:
            shutil.copy(img / u, proj / "assets" / "img" / u)
    words = json.loads((job / "words.json").read_text(encoding="utf-8"))
    vdur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(job / "voice.wav")]))
    end = round(vdur + cfg.get("tail", 0.8), 2)
    starts, pos, kidx = [], 0, []
    for a, _, _ in cfg["beats"]:
        k = next((i for i in range(pos, len(words)) if norm(words[i][0]).startswith(norm(a))), None)
        if k is None:
            raise SystemExit(f"не знайшов якір '{a}' після слова {pos}")
        starts.append(0.0 if not starts else max(.1, words[k][1] - .25)); pos = k + 1; kidx.append(k)

    def wt(a, k0):
        """час слова-якоря a, шукаючи від слова k0"""
        k = next((i for i in range(k0, len(words)) if norm(words[i][0]).startswith(norm(a))), None)
        if k is None:
            raise SystemExit(f"не знайшов слово '{a}' після {k0}")
        return words[k][1]
    ev, drops = [], []  # звукові ефекти [час, назва, гучність]; провали музики [від, до]
    starts.append(end)
    secs, js = [], []
    for i, (_, t, p) in enumerate(cfg["beats"]):
        s, d = starts[i], starts[i + 1] - starts[i]
        h, j = scene(i, t, p, img, s, d + .7)
        if i == 0:  # хук: головна цифра на екрані з першого кадру, без появи
            j = re.sub(r"tl\.fromTo\('#b0 \.bigt \.w',[^;]*;", "", j).replace("s+.2);", "s);")
        j = re.sub(r"tl\.fromTo\(('[^']+'),(\{[^{}]*\}),(\{[^{}]*\}),s\+([^)]*)\);", lambda m: f"tl.set({m[1]},{m[2]},s);" + m[0], j)
        bt = THEMES[p.get("theme", cfg["theme"])]
        sv = f"--vacc:{bt.get('vacc', bt['acc'])};--bg:{bt['bg']};--ink:{bt['ink']};--acc:{bt['acc']};--acc2:{bt['acc2']};--head:{bt['head']}"
        h = h.replace(f"<section class='sc' id='b{i}'>", f"<section class='sc' id='b{i}' style=\"{sv}\">", 1)
        secs.append(h.replace("{pat}", bt["pat"]))
        js.append(f"(function(s,d){{{j}}})({s:.3f},{d + .7:.3f});")
        kind = None
        if i == 0:
            js.append("tl.set('#b0',{visibility:'visible'},0);")
        else:
            kind = p.get("tr") or cfg.get("trans", TRANS)[i % len(cfg.get("trans", TRANS))]
            js.append(trans_js(i - 1, i, s, kind))
        # звук під подію (як у референсах: вжух на переходах, удар на великих написах, «поп» на плашках)
        if kind == "flash":
            ev.append([s, "boom", .8])
        elif kind and kind != "cut":
            ev.append([s - .18, "whoosh", .45])
        if t == "chapter":
            ev += [[s - 1.5, "riser", .35], [s + .15, "boom", .7]]
        elif t == "big":
            ev.append([s + .15, "hit", .5])
        elif t == "polaroid":
            ev += [[s, "whoosh_fast", .4], [s + .9, "shutter", .6]] + ([[s + 1.1, "hit", .6]] if p.get("stamp") else [])
        elif t == "versus":
            ev += [[s + .1, "whoosh_fast", .4], [s + .9, "hit", .6]]
        elif t == "list":
            ev += [[s + .5 + k2 * p.get("gap", .45), "pop", .45] for k2 in range(len(p["items"]))]
        elif t == "timeline":
            ev += [[s + .35 + k2 * .35, "pop", .45] for k2 in range(len(p["points"]))]
        elif t == "mascot":
            ev.append([s + .45, "pop", .5])
        if p.get("tag"):
            ev.append([s + .45, "pop", .4])
        for a in p.get("punch", []):  # різке наближення на слові
            tp = wt(a, kidx[i]) - .05
            js.append(f"tl.to('#b{i}',{{scale:1.14,duration:.14,ease:'power4.out'}},{tp:.3f});tl.to('#b{i}',{{scale:1,duration:.5,ease:'power2.inOut'}},{tp + 1.1:.3f});")
            ev.append([tp - .05, "whoosh_fast", .35])
        if p.get("freeze"):  # чорно-білий «стоп-кадр» на панчлайні
            tf = wt(p["freeze"], kidx[i]) - .05
            js.append(f"tl.set('#b{i}',{{filter:'grayscale(1) contrast(1.35)'}},{tf:.3f});tl.fromTo('#b{i}',{{scale:1}},{{scale:1.08,duration:.18,ease:'power4.out',immediateRender:false}},{tf:.3f});")
            ev.append([tf, "shutter", .8])
        if p.get("drop"):  # тиша в музиці під жарт: [слово, тривалість]
            td = wt(p["drop"][0], kidx[i]) - .1
            drops.append([td, td + p["drop"][1]])
        for o, nm, g in p.get("sfx", []):
            ev.append([s + o, nm, g])
    root_vars = f"--bg:{th['bg']};--ink:{th['ink']};--acc:{th['acc']};--acc2:{th['acc2']};--head:{th['head']}"
    page = f"""<!doctype html><html lang="uk"><head><meta charset="utf-8"><style>{CSS}</style>
<script src="assets/gsap.min.js"></script></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{end}" data-width="1920" data-height="1080" style="{root_vars}">
{''.join(secs)}
<div class="vig"></div><div class="grain"></div>
<audio id="mix" class="clip" data-start="0" data-duration="{end}" data-track-index="6" data-volume="1" src="assets/sound/mix.wav"></audio>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{paused: true}});
{chr(10).join(js)}
tl.fromTo('.grain',{{x:0,y:0}},{{x:-60,y:40,duration:{end},ease:'steps({int(end * 12)})'}},0);
tl.set({{}}, {{}}, {end});
window.__timelines["main"] = tl;
</script></body></html>"""
    (proj / "index.html").write_text(page, encoding="utf-8")
    (job / "END.txt").write_text(str(end))
    # мікс: голос + музика розділу (тихо, з приглушенням під голос)
    # музика нормалізується до music_lufs (типово -31 LUFS, голос близько -16), тож гучність треку не залежить від файлу; vol лише множник
    # музика: або один трек ("music"), або кілька ("musics": [[індекс біта, файл, зсув у треку, гучність], ...]) з перехресними згасаннями
    import numpy as np
    from scipy.io import wavfile
    sfxdir = ROOT / "assets_cache" / "sfx"
    if not (sfxdir / "whoosh.wav").exists():
        subprocess.run([sys.executable, str(ROOT / "tools" / "sfx_lib.py")], check=True)
    trk = np.zeros(int((end + 2) * 48000))
    # власник не хоче звуків на переходах: «вжух», наростання й подібне вимкнено за замовчуванням
    mute = set(cfg.get("sfx_mute", ["whoosh", "whoosh_fast", "riser", "boom", "hit", "pop", "shutter", "scratch", "ding", "typewriter"]))  # власник: лише голос і музика
    for tt, nm, g in ev:
        if nm in mute:
            continue
        x = wavfile.read(sfxdir / f"{nm}.wav")[1].astype(float) / 32767
        a = int(max(0, tt) * 48000); trk[a:a + len(x)] += x[:len(trk) - a] * g
    wavfile.write(job / "sfx.wav", 48000, (np.clip(trk, -1, 1) * 32767).astype(np.int16))
    segs = cfg.get("musics") or ([[0, cfg["music"], cfg.get("music_start", 0), cfg.get("music_vol", .2)]] if cfg.get("music") else [])
    if segs:
        ins, fl = ["-i", str(job / "voice.wav")], []
        for k, (bi, f, off, vol) in enumerate(segs):
            t0 = starts[bi]
            t1 = starts[segs[k + 1][0]] if k + 1 < len(segs) else end
            ln = t1 - t0 + (0.8 if k + 1 < len(segs) else 0)
            ins += ["-ss", str(off), "-i", f]
            fi = 0.8 if k else 1.0
            fl.append(f"[{k + 1}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{ln:.3f},asetpts=PTS-STARTPTS,"
                      f"loudnorm=I={cfg.get('music_lufs', -31)}:TP=-3:LRA=11,aresample=48000,afade=t=in:d={fi},afade=t=out:st={max(0, ln - (0.8 if k + 1 < len(segs) else 1.5)):.3f}:d={0.8 if k + 1 < len(segs) else 1.5},volume={vol},adelay={int(t0 * 1000)}|{int(t0 * 1000)},apad=whole_dur={end}[m{k}]")
        dexpr = "*".join(f"(1-between(t,{a:.2f},{b:.2f}))" for a, b in drops) or "1"
        fl.append("".join(f"[m{k}]" for k in range(len(segs))) + f"amix=inputs={len(segs)}:normalize=0,volume='{dexpr}':eval=frame[mm]")
        fl.append(f"[0:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={end},asplit=2[v][sc]")
        fl.append("[mm][sc]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=350[md]")
        ins += ["-i", str(job / "sfx.wav")]
        fl.append(f"[{len(segs) + 1}:a]aresample=48000,aformat=channel_layouts=stereo,volume={cfg.get('sfx_vol', .5)}[fx]")
        fl.append("[v][md][fx]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,atrim=0:" + str(end) + "[o]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[o]", "-ar", "48000", str(job / "mix.wav")], check=True)
    else:
        shutil.copy(job / "voice.wav", job / "mix.wav")
    print("проєкт:", proj, "тривалість", end, "бітів", len(cfg["beats"]))


if __name__ == "__main__":
    main()
