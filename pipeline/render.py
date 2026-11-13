"""Шаблонний рендер: сцени з JSON-сценарію + таймінги слів -> index.html (GSAP) -> hyperframes -> MP4.
Чотири теми оформлення чергуються, щоб ролики не виглядали однаково.
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "templates" / "auto"

from .themes import theme as get_theme

TOPIC = {"dim": "ДІМ", "ekonomika": "ЕКОНОМІКУ", "yizha": "ЇЖУ", "avto": "АВТО", "sport": "СПОРТ", "svit": "СВІТ", "polityka": "ПОЛІТИКУ"}

e = lambda s: html.escape(str(s or ""))


def pages_of(wt: list) -> list[list[int]]:
    pages, cur = [], []
    for i, (w, _) in enumerate(wt):
        cur.append(i)
        if len(cur) == 3 or w[-1] in ".,!:?" or (len(cur) == 2 and len(w) > 8) or len(w) > 14:
            pages.append(cur); cur = []
    if cur:
        pages.append(cur)
    return pages


def _num(v) -> float | None:
    s = re.sub(r"[^\d.,]", "", str(v)).replace(",", ".")
    try:
        return float(s) if s else None
    except ValueError:
        return None


def scene_html(k: int, sc: dict, photos: dict, channel: str) -> str:
    t = sc.get("type"); out = [f'<div class="sc" id="s{k}">']
    ph = photos.get(k)
    if t == "hook":
        if ph:
            out.append(f'<div class="photo" id="ph{k}" style="background-image:url({ph["file"]});height:690px"><div class="cr">{e(ph["credit"])}</div></div>')
            out.append(f'<div class="big" id="bg{k}" style="top:850px;font-size:170px">{e(sc.get("big"))}<span class="unit">{e(sc.get("unit"))}</span></div>')
            out.append(f'<div class="head" style="top:1050px;font-size:58px">{e(sc.get("headline"))}</div>')
        else:
            out.append(f'<div class="big" id="bg{k}" style="top:380px;font-size:260px">{e(sc.get("big"))}<span class="unit">{e(sc.get("unit"))}</span></div>')
            out.append(f'<div class="head" style="top:720px;font-size:84px">{e(sc.get("headline"))}</div>')
    elif t == "number":
        out.append(f'<div class="big cnt" id="n{k}" data-v="{e(sc.get("value"))}" style="top:440px">{e(sc.get("value"))}</div>')
        out.append(f'<div class="unitline" style="top:660px">{e(sc.get("unit"))}</div><div class="head" style="top:760px">{e(sc.get("label"))}</div>')
    elif t == "compare":
        a, b = _num(sc.get("a_value")) or 1, _num(sc.get("b_value")) or 1
        m = max(a, b)
        for j, (lab, val, w) in enumerate([(sc.get("a_label"), sc.get("a_value"), a / m), (sc.get("b_label"), sc.get("b_value"), b / m)]):
            y = 260 + j * 440
            out.append(f'<div class="blab" style="top:{y}px">{e(lab)}</div><div class="bar b{j}" id="br{k}_{j}" data-w="{max(.06, w) * 920:.0f}" style="top:{y + 80}px"></div>'
                       f'<div class="bval cnt" id="bv{k}_{j}" data-v="{e(val)}" style="top:{y + 220}px">{e(val)} <small>{e(sc.get("unit"))}</small></div>')
    elif t == "quote":
        out.append(f'<div class="qm">“</div><div class="quote" id="q{k}">{e(sc.get("text"))}</div><div class="author">{e(sc.get("author"))}</div>')
    elif t == "list":
        for j, it in enumerate((sc.get("items") or [])[:3]):
            out.append(f'<div class="li" id="li{k}_{j}" style="top:{300 + j * 260}px"><b>{j + 1}</b>{e(it)}</div>')
    elif t == "photo_fact":
        if ph:
            out.append(f'<div class="photo" id="ph{k}" style="background-image:url({ph["file"]});height:820px"><div class="cr">{e(ph["credit"])}</div></div>')
            out.append(f'<div class="head" style="top:990px;font-size:62px">{e(sc.get("headline"))}</div>')
        else:
            out.append(f'<div class="head" style="top:520px;font-size:96px">{e(sc.get("headline"))}</div>')
    elif t == "cta":
        out.append(f'<div class="ring"></div><div class="cta"><div class="a">тут усе про</div><div class="b">{TOPIC[channel]}</div></div><div class="sub" id="sub{k}">ПІДПИСУЙСЯ</div>')
    if sc.get("stamp") and t != "cta":
        top = 250 if t == "hook" and ph else 1090
        out.append(f'<div class="stamp" id="st{k}" style="top:{top}px">{e(sc["stamp"])}</div>')
    out.append("</div>")
    return "".join(out)


def build_html(spec: dict, wt: list, end: float, theme: str, photos: dict, channel: str) -> str:
    th = get_theme(theme)
    T = lambda i: round(wt[min(i, len(wt) - 1)][1] + 0.2, 3)
    scenes = spec["scenes"]
    starts = [0.0] + [round(T(s["from_word"]) - 0.08, 3) for s in scenes[1:]]
    hl = {re.sub(r"[^\w'-]", "", h.lower()) for h in spec.get("highlight", [])}
    pages = pages_of(wt)
    caps = "".join(f'<div class="cap" id="c{k}"><span class="in">' + "".join(
        f'<span class="w" id="w{k}_{j}">{e(wt[i][0].rstrip(".,:!?"))}</span>' for j, i in enumerate(pg)) + "</span></div>" for k, pg in enumerate(pages))
    body = "".join(scene_html(k, sc, photos, channel) for k, sc in enumerate(scenes))
    css = (TPL / "style.css").read_text(encoding="utf-8")
    for key, val in th.items():
        css = css.replace("{" + key + "}", val)
    js = []; a = js.append
    a(f'tl.set({json.dumps(["#s%d" % k for k in range(1, len(scenes))])},{{opacity:0}},0);')
    for k, sc in enumerate(scenes):
        st = starts[k]; en = starts[k + 1] if k + 1 < len(scenes) else end
        if k:
            a(f'tl.set("#s{k-1}",{{opacity:0}},{st});tl.set("#s{k}",{{opacity:1}},{st});tl.fromTo("#cam",{{scale:1.1,rotation:{(-1) ** k}}},{{scale:1,rotation:0,duration:.35,ease:"power3.out",immediateRender:false}},{st});')
        t = sc.get("type")
        if t == "hook":
            a(f'tl.fromTo("#bg{k}",{{scale:1.15}},{{scale:1,duration:.6,ease:"elastic.out(1,.45)"}},0);')
            if k in photos:
                a(f'tl.fromTo("#ph{k}",{{scale:1.08}},{{scale:1,duration:{max(1, en):.2f},ease:"none"}},0);')
        if t in ("number", "compare"):
            a(f'document.querySelectorAll("#s{k} .cnt").forEach(el=>{{const v=el.dataset.v,n=parseFloat(v.replace(/[^\\d.,]/g,"").replace(",","."));if(isNaN(n))return;'
              f'const tail=el.innerHTML.replace(/^[^<]*/,""),o={{v:0}};const dec=(v.match(/[.,](\\d+)/)||["",""])[1].length;'
              f'tl.fromTo(o,{{v:0}},{{v:n,duration:.9,ease:"power3.out",immediateRender:false,onUpdate(){{let s=o.v.toFixed(dec).replace(".",",");s=s.replace(/\\B(?=(\\d{{3}})+(?!\\d))/g," ");el.innerHTML=s+" "+tail}}}},{st + .25});}});')
        if t == "compare":
            a(f'document.querySelectorAll("#s{k} .bar").forEach((b,j)=>tl.fromTo(b,{{width:0}},{{width:+b.dataset.w,duration:.8,ease:"power3.out",immediateRender:false}},{st + .2}+j*.5));')
        if t == "quote":
            a(f'tl.fromTo("#q{k}",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:1.0,ease:"steps(14)",immediateRender:false}},{st + .15});')
        if t == "list":
            n = len((sc.get("items") or [])[:3]); span = max(.6, (en - st - .4) / max(1, n))
            for j in range(n):
                a(f'tl.fromTo("#li{k}_{j}",{{opacity:0,x:-120}},{{opacity:1,x:0,duration:.3,ease:"back.out(2)",immediateRender:false}},{st + .15 + j * span:.3f});tl.set("#li{k}_{j}",{{opacity:0}},0);')
        if t == "photo_fact" and k in photos:
            a(f'tl.fromTo("#ph{k}",{{scale:1.12}},{{scale:1,duration:{max(.8, en - st):.2f},ease:"power2.out"}},{st});')
        if t == "cta":
            a(f'tl.fromTo("#s{k} .cta",{{opacity:0,y:40}},{{opacity:1,y:0,duration:.3,ease:"expo.out",immediateRender:false}},{st});tl.fromTo("#sub{k}",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.3,ease:"back.out(2.5)",immediateRender:false}},{st + .3});'
              f'tl.to("#sub{k}",{{scale:.92,duration:.09}},{st + 1.2});tl.to("#sub{k}",{{scale:1,opacity:.6,duration:.3}},{st + 1.29});')
        if sc.get("stamp") and t != "cta":
            ts = st + min(.7, (en - st) / 2)
            a(f'tl.set("#st{k}",{{opacity:0}},0);tl.fromTo("#st{k}",{{opacity:0,scale:1.6}},{{opacity:1,scale:1,duration:.22,ease:"power3.in",immediateRender:false}},{ts:.3f});tl.fromTo("#cam",{{y:0}},{{y:10,duration:.05,yoyo:true,repeat:1}},{ts + .22:.3f});')
    ls = round(end - .6, 3)  # петля: останні кадри повертають хук
    a(f'tl.set("#s{len(scenes) - 1}",{{opacity:0}},{ls});tl.set("#s0",{{opacity:1}},{ls});tl.fromTo("#s0",{{scale:.9,opacity:0}},{{scale:1,opacity:1,duration:.5,ease:"power2.out",immediateRender:false}},{ls});')
    for k, pg in enumerate(pages):
        st = T(pg[0]) - .08; en = (T(pages[k + 1][0]) - .08) if k + 1 < len(pages) else end - .65
        a(f'tl.set("#c{k}",{{opacity:1}},{st:.3f});tl.fromTo("#c{k}",{{scale:.85,y:20}},{{scale:1,y:0,duration:.18,ease:"back.out(2.5)",immediateRender:false}},{st:.3f});tl.set("#c{k}",{{opacity:0}},{max(en, st + .15):.3f});')
        for j, i in enumerate(pg):
            nxt = T(pg[j + 1]) if j + 1 < len(pg) else en
            key = re.sub(r"[^\w'-]", "", wt[i][0].lower()) in hl
            col = th["hl"]
            a(f'tl.set("#w{k}_{j}",{{color:"{col}",scale:1.08}},{T(i) - .03:.3f});tl.set("#w{k}_{j}",{{color:"{col if key else th["capfg"]}",scale:1}},{max(nxt - .03, T(i) + .1):.3f});')
    return (f'<!doctype html><html lang="uk" data-resolution="portrait"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>'
            f'<script src="assets/gsap.min.js"></script><style>{css}</style></head><body>'
            f'<div id="root" data-composition-id="main" data-start="0" data-duration="{end}" data-width="1080" data-height="1920"><div id="deco"></div><div id="cam">{body}</div>{caps}'
            f'<audio id="mix" class="clip" data-start="0" data-duration="{end:.2f}" data-track-index="6" data-volume="1" src="assets/sound/mix.wav"></audio></div>'
            '<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});\n' + "\n".join(js) +
            '\nwindow.__timelines["main"]=tl;</script></body></html>'), starts


def render(spec: dict, wt: list, end: float, theme: str, photos: dict, channel: str, mix_wav: Path, work: Path, out_mp4: Path) -> list[float]:
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(TPL, work, ignore=shutil.ignore_patterns("style.css"))
    (work / "assets" / "sound").mkdir(parents=True, exist_ok=True)
    shutil.copy(mix_wav, work / "assets" / "sound" / "mix.wav")
    ph = {}
    for k, p in photos.items():
        dst = work / "assets" / f"photo{k}.jpg"; shutil.copy(p["path"], dst)
        ph[k] = {"file": f"assets/photo{k}.jpg", "credit": p["credit"]}
    page, starts = build_html(spec, wt, end, theme, ph, channel)
    (work / "index.html").write_text(page, encoding="utf-8")
    env = dict(os.environ)
    if os.environ.get("HF_BROWSER"):
        env["HYPERFRAMES_BROWSER_PATH"] = os.environ["HF_BROWSER"]
    subprocess.run(["npx", "--yes", "hyperframes@0.8.216", "render", "--fps", "30", "--quality", "delivery"], cwd=work, env=env, check=True,
                   stdout=subprocess.DEVNULL)
    vid = sorted((work / "renders").glob("*.mp4"))[-1]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vid), "-i", str(mix_wav), "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                    "-b:v", "2600k", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    "-movflags", "+faststart", str(out_mp4)], check=True)
    return starts
