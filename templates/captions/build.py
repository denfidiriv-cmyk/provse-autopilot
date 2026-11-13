#!/usr/bin/env python3
"""Series «Якщо ядерний удар», episode 1 «У тебе 10 секунд». 1080x1920, 30 fps, Gemini stills + motion + code sound.
Guidance follows the ДСНС/АрміяInform memo and Ready.gov: don't look at the flash, lie face down feet toward the blast,
cover exposed skin, mouth and nose, stay down until the blast wave passes."""
import json, html, pathlib, random

HERE = pathlib.Path(__file__).parent
rnd = random.Random(3)
W, H = 1080, 1920
IMG_H = round(1080 * 2327 / 1300)   # 1933
import os
RUN = os.environ.get("RUN", "e2_04")
DOOR = os.environ.get("DOOR", "e2_07")
DOOR_T = float(os.environ.get("DOOR_T", "46.0"))

# (start, end, image, camera from, camera to)  camera = (scale, x, y)
VO = 0.2
import os
CL = json.loads(os.environ.get("CLIPS", "{}"))
def F(name): return CL.get(name, name)
_WT = json.loads((HERE / "wordtimes.json").read_text(encoding="utf-8"))
def WTm(i): return round(_WT[i][1] + VO, 3)
def C(i): return round(WTm(i) - 0.08, 3)
BEATS = [0.0, 29.24]
SC = []
PICK=[[1]]
MOV=[((1.10,0,0),(1.0,0,0)),((1.0,0,0),(1.08,0,-20)),((1.06,-20,0),(1.0,20,0))]
STARTS=set()
for bi in range(len(PICK)):
    a0,b0=BEATS[bi],BEATS[bi+1]; fr=PICK[bi]; d=(b0-a0)/len(fr)
    for k,n in enumerate(fr):
        if k==0: STARTS.add(len(SC))
        SC.append((round(a0+k*d,3), round(a0+(k+1)*d,3), f"c4_{n:02d}", MOV[k%3][0], MOV[k%3][1]))
END = 29.24
SC=[(0.0,END,"film.mp4@0",(1,0,0),(1,0,0))]; STARTS={0}
TX = []
WT = json.loads((HERE / "wordtimes.json").read_text(encoding="utf-8"))
KEY = set(['сорок', 'дві', 'тисячі', 'втратити', 'Скринінг', 'серця', 'судин', 'нирок', 'Дії', 'ЦНАПі', 'тижня', 'пастка', 'лише', 'обстеження', 'двох', 'місяців', 'бюджет', 'два', 'мільйони', "дев'ятисот", 'спершу', 'лікарню', 'Підписуйся'])
# chunks of up to 3 words, break after punctuation
chunks=[];seg=[]
def flush(seg):
    n=len(seg)
    if not n: return
    k=(n+2)//3; base,rem=divmod(n,k); i=0
    for j in range(k):
        m=base+(1 if j<rem else 0); chunks.append(seg[i:i+m]); i+=m
for w,t in WT:
    seg.append((w,t+VO))
    if w[-1] in ".,:?!": flush(seg); seg=[]
flush(seg)
caps=[]
for ci,ch in enumerate(chunks):
    st=ch[0][1]; en=(chunks[ci+1][0][1]-0.05) if ci+1<len(chunks) else END
    spans="".join(f'<span class="w{" k" if w.strip(".,:?!") in KEY else ""}" id="w{ci}_{j}">{w.rstrip(",.:")}</span> ' for j,(w,t) in enumerate(ch))
    caps.append((ci,st,en,spans,ch))
# info chips (r1 style)
CH = []
KIT = []
events = []
def ev(t, kind, **kw): events.append(dict(t=round(t, 3), kind=kind, **kw))
js = []; add = js.append

def scene_html(i, a, b, f):
    if ".mp4" in f:
        name, ms = f.split("@")
        return f'<video class="vid clip" id="s{i}" data-start="{a:.2f}" data-duration="{b - a:.2f}" data-media-start="{ms}" data-track-index="1" src="assets/vid/{name}" muted playsinline></video>'
    return f'<div class="sc clip" id="s{i}" data-start="{a:.2f}" data-duration="{b - a:.2f}" data-track-index="1"><img class="im" id="im{i}" src="assets/img/{f}.jpg" alt=""></div>'
XF=0.35
scenes = "".join(scene_html(i, a, (b+XF if i<len(SC)-1 else b), f) for i, (a, b, f, _, _) in enumerate(SC))
texts = "".join(f'<div class="cap2" id="c{ci}">{sp}</div>' for ci,st,en,sp,ch in caps)
texts += "".join(f'<div class="chip" id="ch{i}"><b>{a_}</b><span>{b_}</span></div>' for i,(t0,t1,a_,b_) in enumerate(CH))
texts += '<div id="kit">' + "".join(f'<div class="kitem" id="k{i}">✓ {n}</div>' for i,(t,n) in enumerate(KIT)) + '</div>'
# floating dust motes (thriller atmosphere)
NP = 0
dust = "".join(f'<i class="mote" id="m{k}"></i>' for k in range(NP))
for k in range(NP):
    x0 = rnd.uniform(0, 1080); y0 = rnd.uniform(0, 1920); sz = rnd.uniform(3, 9)
    add(f'gsap.set("#m{k}",{{x:{x0:.0f},y:{y0:.0f},width:{sz:.1f},height:{sz:.1f},opacity:{rnd.uniform(.25,.7):.2f}}});')
    add(f'tl.to("#m{k}",{{x:"+={rnd.uniform(-160,160):.0f}",y:"+={rnd.uniform(-420,120):.0f}",duration:{END:.2f},ease:"none"}},0);')
# lamp flicker: quick dips of the dark overlay
for t in ():
    add(f'tl.fromTo("#flick",{{opacity:0}},{{keyframes:[{{opacity:.55,duration:.05}},{{opacity:.1,duration:.06}},{{opacity:.45,duration:.05}},{{opacity:0,duration:.18}}],ease:"none"}},{t});')
    ev(t, "beat", vol=0.25)

for i, (a, b, f, c0, c1) in enumerate(SC):
    add(f'tl.fromTo("#im{i}",{{scale:{c0[0]},x:{c0[1]},y:{c0[2]}}},{{scale:{c1[0]},x:{c1[1]},y:{c1[2]},duration:{b - a:.2f},ease:"power1.inOut"}},{a:.2f});')

add('tl.fromTo("#tint",{opacity:0.0},{opacity:0.0,duration:0.4,ease:"power2.inOut"},0.3);')
pass
for k in range(4):
    ev(0.4 + k * 0.95, "beat", vol=0.35)
for i, a, b, k, h in TX:
    if k in ("big", "hook"):
        add(f'tl.fromTo("#{i}",{{opacity:0,scale:1.35,filter:"blur(10px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.28,ease:"power3.out"}},{a:.2f});')
        if "<small>" in h: add(f'tl.fromTo("#{i} small",{{opacity:0,y:20}},{{opacity:0.9,y:0,duration:0.35,ease:"power3.out"}},{a + 0.45:.2f});')
        if i != "t0":
            ev(a, "hit", vol=0.6)
    elif k == "cap":
        add(f'tl.fromTo("#{i}",{{opacity:0,y:18,filter:"blur(6px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.25,ease:"power2.out"}},{a:.2f});')
    else:
        add(f'tl.fromTo("#{i}",{{opacity:0,y:40}},{{opacity:1,y:0,duration:0.5,ease:"power3.out"}},{a:.2f});')
        add(f'tl.fromTo("#{i} .ep",{{scale:0.6}},{{scale:1,duration:0.6,ease:"back.out(2)"}},{a + 0.1:.2f});')
        ev(a, "hit", vol=1.0)
    if b < END - 0.05:
        add(f'tl.to("#{i}",{{opacity:0,filter:"blur(6px)",duration:0.15,ease:"power2.in"}},{b - 0.15:.2f});')
for j,(a_, b_, f_, c0_, c1_) in enumerate(SC[1:],1):
    if j in STARTS:
        add(f'tl.fromTo("#cam",{{scale:1.06}},{{scale:1,duration:0.35,ease:"power3.out"}},{a_:.2f});')
        ev(a_ - 0.05, "hit", vol=0.35)
for ci,st,en,sp,ch in caps:
    add(f'tl.fromTo("#c{ci}",{{opacity:0,y:14,scale:0.96}},{{opacity:1,y:0,scale:1,duration:0.12,ease:"power2.out"}},{st:.3f});')
    for j,(w,t) in enumerate(ch):
        add(f'tl.to("#w{ci}_{j}",{{opacity:1,duration:0.06}},{t:.3f});')
    add(f'tl.to("#c{ci}",{{opacity:0,duration:0.06}},{max(en-0.06,st+0.14):.3f});')
for i,(t0,t1,a_,b_) in enumerate(CH):
    add(f'tl.fromTo("#ch{i}",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:0.25,ease:"back.out(2.2)"}},{t0:.2f});tl.to("#ch{i}",{{opacity:0,duration:0.15}},{t1-0.15:.2f});')
    ev(t0, "beat", vol=0.3)
for i,(t,n) in enumerate(KIT):
    add(f'tl.fromTo("#k{i}",{{opacity:0,x:30}},{{opacity:1,x:0,duration:0.2,ease:"back.out(2)"}},{t+VO:.2f});')
    ev(t+VO, "beat", vol=0.3)


for i,(a_,b_,f_,c0_,c1_) in enumerate(SC):
    if i>0 and i in STARTS: add(f'tl.fromTo("#s{i}",{{opacity:0,filter:"blur(18px) brightness(1.6)"}},{{opacity:1,filter:"blur(0px) brightness(1)",duration:0.35,ease:"power2.out"}},{a_:.2f});')
    elif i>0: add(f'tl.fromTo("#s{i}",{{opacity:0}},{{opacity:1,duration:0.35,ease:"power1.inOut"}},{a_:.2f});')
# hook: light flicker then darkness on "Клац"
k=WTm(0)

ev(k+0.05,"hit",vol=1.0)
# big 3 ДОБИ stamp
ev(WTm(0)+0.1,"boom",vol=0.8)

audio_tag = (f'<audio id="mix" class="clip" data-start="0" data-duration="{END:.2f}" data-track-index="6" data-volume="1" src="assets/sound/mix.wav"></audio>'
             if (HERE / "assets/sound/mix.wav").exists() else "")
fonts = "".join(
    f'@font-face{{font-family:"UI";font-weight:{w};src:url("assets/fonts/inter-{sub}-{w}-normal.woff2") format("woff2");unicode-range:{rng}}}\n'
    for w in (600, 800)
    for sub, rng in (("cyrillic", "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"),
                     ("latin", "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")))
CSS = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#0b0b0c}}
#root{{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;font-family:"UI",sans-serif;color:#fff;background:#0b0b0c}}
#cam{{position:absolute;left:0;top:0;width:1080px;height:1920px}}
.sc{{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden}}
.vid{{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}}
.im{{position:absolute;left:0;top:-6px;width:1080px;height:{IMG_H}px;object-fit:cover;transform-origin:50% 50%}}
#tint,#endtint{{position:absolute;left:0;top:0;width:1080px;height:1920px;background:#000}}
#endtint{{opacity:0}}
#scrim{{display:none;position:absolute;left:0;top:1060px;width:1080px;height:860px;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.7) 40%,rgba(0,0,0,.85))}}
#topscrim{{display:none;position:absolute;left:0;top:0;width:1080px;height:820px;background:linear-gradient(rgba(0,0,0,.75),rgba(0,0,0,.5) 55%,rgba(0,0,0,0))}}
#series{{position:absolute;left:60px;top:180px;font:800 30px "UI";letter-spacing:.08em;background:rgba(0,0,0,.6);padding:8px 16px;border-radius:10px}}
#series b{{color:#FF7A2F}}
.tx{{position:absolute;left:60px;width:960px;text-align:center;text-shadow:0 4px 30px rgba(0,0,0,.6)}}
.tx em{{font-style:normal;color:#FF8A45;text-shadow:0 2px 6px rgba(0,0,0,.95),0 0 28px rgba(0,0,0,.9)}}
.hook{{top:560px;font:800 112px/1.02 "UI";letter-spacing:-0.03em;text-transform:uppercase}}
.hook small{{display:block;margin-top:30px;font:600 44px/1.25 "UI";letter-spacing:0;text-transform:none;opacity:.92}}
.big{{top:360px;font:800 92px/1.02 "UI";letter-spacing:-0.025em;text-transform:uppercase}}
.big small{{display:block;margin-top:22px;font:600 44px/1.2 "UI";letter-spacing:0;text-transform:none;opacity:.9}}
.cap{{top:1220px;font:800 58px/1.2 "UI";letter-spacing:-0.01em}}
.end{{top:820px;display:flex;flex-direction:column;align-items:center;gap:22px}}
.end .ep{{font:800 44px "UI";letter-spacing:.1em;text-transform:uppercase;background:#FF7A2F;color:#0b0b0c;padding:10px 26px;border-radius:12px}}
.end b{{font:800 96px/1.05 "UI";letter-spacing:-0.03em}}
.end i{{font:600 42px "UI";font-style:normal;opacity:.85}}
#flash,#dip{{position:absolute;left:0;top:0;width:1080px;height:1920px;opacity:0}}
#flash{{background:#fff}}#dip{{background:#000}}
.cap2{{position:absolute;left:50px;width:980px;top:1400px;text-align:center;font:800 80px/1.12 "UI";text-transform:uppercase;letter-spacing:0.02em;color:#fff8e1;-webkit-text-stroke:9px #06241a;paint-order:stroke fill;text-shadow:0 6px 0 #06241a}}
.cap2 .k{{color:#f5c542}}
.chip{{position:absolute;left:50px;width:980px;top:1060px;display:flex;flex-direction:column;align-items:center;gap:4px;text-align:center;text-shadow:0 3px 10px rgba(0,0,0,.95),0 0 40px rgba(0,0,0,.9)}}
.chip b{{font:800 34px "UI";letter-spacing:.14em;color:#fff;text-transform:uppercase;opacity:.9}}
.chip span{{font:900 92px/1 "UI";color:#FF8A45;letter-spacing:-0.01em}}
#kit{{position:absolute;right:50px;top:230px;display:flex;flex-direction:column;gap:12px;align-items:flex-end}}
.kitem{{font:800 44px "UI";color:#fff;background:rgba(10,12,16,.8);padding:10px 22px;border-radius:12px;border:2px solid rgba(120,220,140,.8)}}
#tend{{top:520px}}
#big{{position:absolute;left:0;width:1080px;top:640px;text-align:center;font:900 132px/1 "UI";color:#FF8A45;letter-spacing:-0.02em;text-shadow:0 8px 40px rgba(0,0,0,.9),0 0 80px rgba(255,120,40,.35)}}
.brand{{position:absolute;left:190px;width:700px;top:560px;text-align:center;font:800 88px/1 "UI";letter-spacing:.02em;color:#fff;background:#7B2D8E;padding:26px 0;border-radius:22px;box-shadow:0 12px 40px rgba(0,0,0,.45)}}
.mote{{position:absolute;left:0;top:0;border-radius:50%;background:radial-gradient(rgba(255,214,170,.95),rgba(255,180,120,0));filter:blur(1px)}}
#vig{{display:none;position:absolute;left:0;top:0;width:1080px;height:1920px;background:radial-gradient(ellipse at 50% 45%,rgba(0,0,0,0) 55%,rgba(0,0,0,.45) 100%)}}
#flick{{position:absolute;left:0;top:0;width:1080px;height:1920px;background:#000;opacity:0}}
'''
page = f'''<!doctype html>
<html lang="uk" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
{fonts}{CSS}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END:.2f}" data-width="{W}" data-height="{H}">
  <div id="cam">{scenes}</div>
  <div id="dust">{dust}</div><div id="vig"></div><div id="flick"></div>
  <div id="tint"></div>
  <div id="scrim"></div><div id="topscrim"></div><div id="endtint"></div>
  {texts}
  <div id="flash"></div><div id="dip"></div>
  {audio_tag}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
(HERE / "index.html").write_text(page, encoding="utf-8")
(HERE / "events.json").write_text(json.dumps(dict(end=END, events=sorted(events, key=lambda e: e["t"])), indent=1), encoding="utf-8")
print(f"duration={END}s events={len(events)}")
