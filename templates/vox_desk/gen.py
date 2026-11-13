"""Vox-style investigation desk, 9:16. Real CC photos as prints; camera glides between items (sineInOut);
desk objects step at 12fps; red string; typed torn labels. Hook text on frame 0; word-pop captions; loop seam."""
import json, math
WT=json.load(open('../wordtimes_t.json')); T=lambda i: round(WT[i][1]+0.2,3); END=float(open('../END.txt').read())
RED='#c4302b'; INK='#141414'; DESK='#d6c9ae'; PAPER='#f6f0e2'; YEL='#f2d33b'
KEY={'Кремлі.','вийшло?','Віткофф','Кушнер','прогрес','є.','москалями','відновлюються,','європейці.','Дублін,','Зеленському.','Підписуйся,'}
pages=[];cur=[]
for i,(w,t) in enumerate(WT):
    cur.append(i)
    if len(cur)==3 or w[-1] in '.,!:?' or (len(cur)==2 and len(w)>8): pages.append(cur);cur=[]
if cur: pages.append(cur)
caps=''.join(f'<div class="cap" id="c{k}">'+''.join(f'<span class="w{" k" if WT[i][0] in KEY else ""}" id="w{k}_{j}">{WT[i][0].rstrip(".,:!?")}</span>' for j,i in enumerate(pg))+'</div>' for k,pg in enumerate(pages))
def tape(x,y,r,w=180): return f'<div class="tape" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({r}deg)"></div>'
def pin(x,y): return f'<div class="pin" style="left:{x}px;top:{y}px"></div>'
def printp(id_,img,x,y,w,h,r,credit,label=''):
    return (f'<div class="print" id="{id_}" style="left:{x}px;top:{y}px;width:{w+48}px;height:{h+96}px;transform:rotate({r}deg)">'
            f'<div class="ph" style="width:{w}px;height:{h}px;background-image:url(assets/img/{img})"></div><div class="cr">{credit}</div>'
            f'{tape(w/2-66,-26,-4)}</div>')
def label(id_,x,y,txt,size=46,r=-1.5): return f'<div class="lab" id="{id_}" style="left:{x}px;top:{y}px;font-size:{size}px;transform:rotate({r}deg)"><span class="ty">{txt}</span></div>'
US='''<svg viewBox="0 0 190 100" width="{w}"><rect width="190" height="100" fill="#b22234"/>'''+''.join(f'<rect y="{i*15.4}" width="190" height="7.7" fill="#fff"/>' for i in range(1,7,1) if True).replace('y="0"','')+'<rect width="76" height="54" fill="#3c3b6e"/>'+''.join(f'<circle cx="{8+c*12}" cy="{7+r*10}" r="2.2" fill="#fff"/>' for r in range(5) for c in range(6))+'</svg>'
UA='<svg viewBox="0 0 150 100" width="{w}"><rect width="150" height="50" fill="#0057b7"/><rect y="50" width="150" height="50" fill="#ffd700"/></svg>'
EU='<svg viewBox="0 0 150 100" width="{w}"><rect width="150" height="100" fill="#003399"/>'+''.join(f'<circle cx="{75+33*math.cos(a*math.pi/6):.1f}" cy="{50+33*math.sin(a*math.pi/6):.1f}" r="4.6" fill="#ffcc00"/>' for a in range(12))+'</svg>'
PIR='''<svg viewBox="0 0 150 100" width="{w}"><rect width="150" height="100" fill="#111"/><g fill="#f2f2f2"><ellipse cx="75" cy="42" rx="20" ry="18"/><rect x="64" y="52" width="22" height="12" rx="3"/>
<rect x="38" y="66" width="74" height="7" rx="3.5" transform="rotate(22 75 70)"/><rect x="38" y="66" width="74" height="7" rx="3.5" transform="rotate(-22 75 70)"/></g>
<g fill="#111"><circle cx="67" cy="41" r="5.5"/><circle cx="83" cy="41" r="5.5"/><path d="M75 47 l-3 6 h6z"/></g></svg>'''
def flag(svg,id_,x,y,w,r=0): return f'<div class="flag" id="{id_}" style="left:{x}px;top:{y}px;transform:rotate({r}deg)">{svg.replace("{w}",str(w))}</div>'
def card(id_,x,y,w,h,r,inner): return f'<div class="card" id="{id_}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({r}deg)">{inner}</div>'
# ---------- desk layout (world coords) ----------
D=''
D+=printp('pk','kremlin.jpg',120,160,640,960,-2,'Фото: Julmin · CC BY-SA 3.0')
D+=label('lk',150,1150,'КРЕМЛЬ · 12 ЛИСТОПАДА',44)
D+=f'<div class="stamp" id="st45" style="left:170px;top:600px;font-size:104px">4,5 ГОДИНИ</div><div class="small" id="sm45" style="left:260px;top:790px">за словами Віткоффа</div>'
D+=f'<div class="q" id="qm" style="left:840px;top:330px">?</div>'
D+=card('cw',1060,180,700,330,2,f'<div class="ix">ДОСЬЄ</div><div class="nm">Стів Віткофф</div><div class="rl">спецпосланець Трампа</div>')+flag(US,'f_us1',1630,140,130,8)
D+=card('ck',1080,560,700,330,-2,f'<div class="ix">ДОСЬЄ</div><div class="nm">Джаред Кушнер</div><div class="rl">зять і радник Трампа</div>')+flag(US,'f_us2',1650,520,130,-6)
D+=card('cq',1050,950,760,330,1,'<div class="quote">«Я думаю, що було досягнуто прогресу»</div><div class="rl" style="margin-top:18px">Стів Віткофф</div>')
D+=f'<div class="stamp g" id="stp" style="left:1160px;top:1330px">ПРОГРЕС Є</div>'
D+=printp('pa','abudhabi.jpg',100,1700,860,320,1.5,'Фото: Nepenthes · CC BY-SA 3.0')
D+=label('la',130,2140,'АБУ-ДАБІ · 10–11 ЛИСТОПАДА',40)
D+=card('tbl',140,2270,820,700,-1,'<div class="ix">ТРИСТОРОННІЙ ФОРМАТ</div><div class="ring"></div>')
D+=flag(US,'f_us3',230,2420,190,-4)+flag(UA,'f_ua',640,2420,170,3)+flag(PIR,'f_pi',430,2700,190,-2)
D+=printp('pb','brussels.jpg',1050,2050,820,547,-2,'Фото: Lukasz Kobus / ЄК · CC BY 4.0')
D+=flag(EU,'f_eu',1720,1980,190,10)
D+=label('lb',1080,2720,'+ ЄВРОПЕЙЦІ В НАСТУПНОМУ РАУНДІ',38)
D+=printp('pd','dublin.jpg',1050,3000,820,511,2,'Фото: William Murphy · CC BY-SA 2.0')
D+=label('ld',1080,3640,'ДУБЛІН · ЗУСТРІЧ ІЗ ЗЕЛЕНСЬКИМ',40)
D+=f'<div class="plane" id="pl">✈</div>'
D+=card('cta',150,3200,780,520,-2,'<div class="ix">ПОЛІТИКА</div><div class="nm" style="font-size:96px;margin-top:30px">головне<br>за хвилину</div>')
D+=f'<div class="sub" id="sub" style="left:230px;top:3790px">ПІДПИСУЙСЯ</div>'
STR=[('s1',(440,640),(1095,215)),('s2',(1095,215),(1115,595)),('s3',(530,1860),(540,2600)),('s4',(560,2600),(1460,2320)),('s5',(440,640),(1460,3250))]
svgs=''.join(f'<path id="{i}" d="M{a[0]} {a[1]} Q {(a[0]+b[0])/2+80} {(a[1]+b[1])/2-120} {b[0]} {b[1]}" fill="none" stroke="{RED}" stroke-width="7" stroke-linecap="round"/>' for i,a,b in STR)
pins=''.join(f'<div class="pin p_{i}" style="left:{a[0]-14}px;top:{a[1]-14}px"></div><div class="pin p_{i}" style="left:{b[0]-14}px;top:{b[1]-14}px"></div>' for i,a,b in STR)
CSS=f'''
@font-face{{font-family:Osw;src:url(assets/fonts/Oswald-700.woff)}}@font-face{{font-family:JB;src:url(assets/fonts/JBMono-700.woff)}}@font-face{{font-family:JBr;src:url(assets/fonts/JBMono-400.woff)}}
@font-face{{font-family:Play;src:url(assets/fonts/PlayfairDisplay-700i.woff)}}@font-face{{font-family:Cav;src:url(assets/fonts/Caveat-700.woff)}}
@font-face{{font-family:UI;font-weight:800;src:url(assets/fonts/inter-cyrillic-800-normal.woff2);unicode-range:U+0400-045F,U+0490-0491}}
@font-face{{font-family:UI;font-weight:800;src:url(assets/fonts/inter-latin-800-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F,U+2190-2193,U+2212}}
*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1080px;height:1920px;overflow:hidden;background:{DESK}}}
#root{{position:absolute;inset:0;overflow:hidden;background:{DESK}}}
#desk{{position:absolute;left:0;top:0;width:2000px;height:4200px;transform-origin:0 0;
 background:radial-gradient(rgba(60,40,10,.07) 2px,transparent 2px) 0 0/14px 14px,linear-gradient(90deg,rgba(0,0,0,.03) 1px,transparent 1px) 0 0/90px 90px,{DESK}}}
#strings{{position:absolute;left:0;top:0}}
.print{{position:absolute;background:#fbf8f0;padding:24px 24px 72px;box-shadow:0 18px 30px rgba(50,35,10,.35)}}
.print .ph{{background-size:cover;background-position:center;filter:contrast(1.05) saturate(.9)}}
.print .cr{{position:absolute;left:26px;bottom:20px;font:22px JBr;color:#6a6255}}
.tape{{position:absolute;height:52px;background:rgba(255,253,240,.6);box-shadow:0 2px 4px rgba(0,0,0,.08)}}
.pin{{position:absolute;width:28px;height:28px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#ff7b6e,{RED} 60%,#7a1712);box-shadow:0 4px 6px rgba(0,0,0,.35)}}
.lab{{position:absolute;background:{INK};color:#f4efe3;font-family:JB;padding:16px 26px 18px;letter-spacing:.02em;clip-path:polygon(0 6%,3% 0,40% 4%,70% 0,100% 5%,98% 50%,100% 96%,60% 100%,30% 95%,0 100%,2% 50%)}}
.stamp{{position:absolute;font:120px Osw;color:{RED};border:12px solid {RED};padding:0 30px;transform:rotate(-8deg);background:rgba(246,240,226,.85);letter-spacing:.02em;opacity:0}}
.stamp.g{{color:#1f6b3a;border-color:#1f6b3a}}
.small{{position:absolute;font:44px Cav;color:{INK};background:{YEL};padding:6px 18px;transform:rotate(-4deg);opacity:0}}
.q{{position:absolute;font:420px/1 Play;color:{RED};opacity:0}}
.card{{position:absolute;background:{PAPER};padding:34px 40px;box-shadow:0 14px 26px rgba(50,35,10,.3);
 background-image:repeating-linear-gradient(transparent 0 58px,rgba(196,48,43,.18) 58px 60px)}}
.card .ix{{font:30px JB;color:{RED};letter-spacing:.12em}}.card .nm{{font:84px/1 Osw;color:{INK};margin-top:22px}}.card .rl{{font:38px JBr;color:#4a4438;margin-top:14px}}
.card .quote{{font:64px/1.15 Play;color:{INK};margin-top:6px}}
.card .ring{{position:absolute;left:210px;top:170px;width:400px;height:400px;border-radius:50%;border:6px dashed #8a7f6a}}
.flag{{position:absolute;box-shadow:0 8px 14px rgba(0,0,0,.3);line-height:0}}
.plane{{position:absolute;font:110px UI;color:{INK};opacity:0}}
.sub{{position:absolute;width:620px;padding:22px 0;text-align:center;background:{RED};color:#fff;font:800 60px UI;border-radius:999px;box-shadow:0 14px 26px rgba(50,35,10,.3)}}
#hook{{position:absolute;left:60px;top:150px;width:960px;opacity:1}}
.cap{{position:absolute;left:90px;width:900px;top:1360px;text-align:center;font:800 82px/1.1 UI;text-transform:uppercase;color:#fff;
 -webkit-text-stroke:7px {INK};paint-order:stroke fill;text-shadow:0 8px 18px rgba(0,0,0,.35);opacity:0}}
.cap .w{{display:inline-block;margin:0 12px;opacity:0}}
#vig{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,transparent 55%,rgba(40,25,5,.35));pointer-events:none}}
'''
H=f'''<!doctype html><html lang="uk" data-resolution="portrait"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/><script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920">
<div id="desk"><svg id="strings" width="2000" height="4200">{svgs}</svg>{D}{pins}</div><div id="vig"></div>
<div id="hook">{label('hk',0,0,'4,5 ГОДИНИ В КРЕМЛІ. ЩО ДАЛІ?',50,-1)}</div>{caps}
<audio id="mix" class="clip" data-start="0" data-duration="{END:.2f}" data-track-index="6" data-volume="1" src="assets/sound/mix.wav"></audio>
</div><script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
'''
js=[];a=js.append
def cam(t,box,dur=.8,ease='sine.inOut',cy=720):
    x,y,w,h=box; s=min(1000/w, 1050/h); X=540-s*(x+w/2); Y=cy-s*(y+h/2)
    a(f'tl.to("#desk",{{x:{X:.1f},y:{Y:.1f},scale:{s:.4f},duration:{dur},ease:"{ease}"}},{t:.3f});')
    return (X,Y,s)
def setcam(box,cy=720):
    x,y,w,h=box; s=min(1000/w,1050/h); a(f'tl.set("#desk",{{x:{540-s*(x+w/2):.1f},y:{cy-s*(y+h/2):.1f},scale:{s:.4f}}},0);')
def slide(sel,t,dx=0,dy=-120,rot=0):  # 12fps stepped slide-in (Vox "on twos")
    a(f'tl.fromTo("{sel}",{{x:{dx},y:{dy},opacity:0}},{{x:0,y:0,opacity:1,duration:.42,ease:"steps(5)"}},{t:.3f});')
def typed(sel,t,n=None):  # 12fps typing via clip
    a(f'tl.fromTo("{sel} .ty",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.55,ease:"steps(9)"}},{t:.3f});tl.set("{sel}",{{opacity:1}},{t:.3f});')
def draw(sel,t,dur=.5): a(f'tl.fromTo("{sel}",{{strokeDasharray:2000,strokeDashoffset:2000}},{{strokeDashoffset:0,duration:{dur},ease:"steps(8)"}},{t:.3f});tl.set(".p_{sel[1:]}",{{opacity:1}},{t:.3f});')
def stamp(sel,t): a(f'tl.fromTo("{sel}",{{opacity:0,scale:1.8}},{{opacity:1,scale:1,duration:.14,ease:"power4.in"}},{t-.14:.3f});tl.fromTo("#desk",{{rotation:0}},{{rotation:.35,duration:.05,yoyo:true,repeat:3}},{t:.3f});')
# hidden by default
hid=['#lk','#sm45','#qm','#cw','#ck','#cq','#f_us1','#f_us2','#pa','#la','#tbl','#f_us3','#f_ua','#f_pi','#pb','#f_eu','#lb','#pd','#ld','#cta','#sub','.pin']
a(f'tl.set({json.dumps(hid)},{{opacity:0}},0);tl.set(["#s1","#s2","#s3","#s4","#s5"],{{strokeDasharray:2000,strokeDashoffset:2000}},0);')
# 0: HOOK — Kremlin print already on desk at frame 0, hook label on screen
setcam((100,140,700,1080))
a('tl.fromTo("#desk",{scale:"+=0"},{duration:0},0);')
cam(0.05,(130,170,660,1020),dur=2.6,ease='none')  # slow push
a('tl.set("#hk .ty",{clipPath:"inset(0 0% 0 0)"},0);')  # hook text fully visible at frame 0
stamp('#st45',T(1)-.05); a(f'tl.to("#sm45",{{opacity:1,duration:.01}},{T(3):.3f});')
typed('#lk',T(4)); a(f'tl.to("#hook",{{opacity:0,y:-30,duration:.25}},{T(7)-.3:.3f});')
# Q: "Що з цього вийшло?" quick punch on red ?
cam(T(7)-.1,(560,380,700,600),dur=.35,ease='power3.out'); a(f'tl.fromTo("#qm",{{opacity:0,scale:.4}},{{opacity:1,scale:1,duration:.3,ease:"back.out(3)"}},{T(7):.3f});')
# envoys: string from Kremlin to dossiers
cam(T(11)-.35,(1040,130,780,800),dur=.7); draw('#s1',T(11)-.3);
slide('#cw',T(11)-.05,dx=120,dy=0); a(f'tl.to("#f_us1",{{opacity:1,duration:.01}},{T(13):.3f});')
cam(T(15)-.3,(1040,130,780,1180),dur=.5); slide('#ck',T(15)-.1,dx=120,dy=0); a(f'tl.to("#f_us2",{{opacity:1,duration:.01}},{T(15)+.1:.3f});'); draw('#s2',T(15))
slide('#cq',T(17)-.15,dx=0,dy=120); stamp('#stp',T(18))
cam(T(17)-.25,(1040,900,780,560),dur=.5,ease='power2.out')
# trilateral: Abu Dhabi print + table with 3 flags (pirate = moskali)
cam(T(19)-.35,(90,1680,900,1320),dur=.75); draw('#s3',T(19)-.3)
slide('#pa',T(19)-.1); typed('#la',T(19)+.3); slide('#tbl',T(20)-.1,dy=120)
for k,(f,t) in enumerate([('#f_us3',T(20)+.25),('#f_ua',T(20)+.45),('#f_pi',T(22)-.1)]):
    a(f'tl.fromTo("{f}",{{opacity:0,scale:1.6,rotation:-20}},{{opacity:1,scale:1,rotation:0,duration:.25,ease:"back.out(2)"}},{t:.3f});')
# Europe joins
cam(T(26)-.3,(1030,1950,880,860),dur=.7); draw('#s4',T(26)-.3); slide('#pb',T(26)); 
a(f'tl.fromTo("#f_eu",{{opacity:0,scale:1.8,rotation:30}},{{opacity:1,scale:1,rotation:10,duration:.3,ease:"back.out(2)"}},{T(29)-.15:.3f});'); typed('#lb',T(28))
# Dublin: pull wide along red string Kremlin -> Dublin with plane
cam(T(30)-.3,(60,120,1900,3700),dur=.9); draw('#s5',T(30)-.1,dur=1.1)
a(f'tl.set("#pl",{{opacity:1}},{T(30):.3f});')
a(f'const pp={{t:0}};const P5=document.getElementById("s5");tl.fromTo(pp,{{t:0}},{{t:1,duration:1.4,ease:"power1.inOut",onUpdate(){{const L=P5.getTotalLength(),q=P5.getPointAtLength(L*pp.t),q2=P5.getPointAtLength(Math.min(L,L*pp.t+5));const el=document.getElementById("pl");el.style.left=(q.x-55)+"px";el.style.top=(q.y-70)+"px";el.style.transform="rotate("+(Math.atan2(q2.y-q.y,q2.x-q.x)*57.3)+"deg)"}}}},{T(30):.3f});')
cam(T(33)-.2,(1030,2980,880,760),dur=.8); slide('#pd',T(33)-.2); typed('#ld',T(35))
a(f'tl.to("#pl",{{opacity:0,duration:.2}},{T(36):.3f});')
# CTA + loop seam back to Kremlin hook framing
cam(T(39)-.35,(130,3170,840,760),dur=.6); slide('#cta',T(39)-.2,dy=120); a(f'tl.fromTo("#sub",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.3,ease:"back.out(2.5)"}},{T(40):.3f});tl.to("#sub",{{scale:.92,duration:.09}},{T(42):.3f});tl.to("#sub",{{scale:1,background:"#4a4438",duration:.3,ease:"back.out(3)"}},{T(42)+.09:.3f});')
ls=END-.75
x,y,w,h=(100,140,700,1080); s=min(1000/w,1050/h)
a(f'tl.to("#desk",{{x:{540-s*(x+w/2):.1f},y:{720-s*(y+h/2):.1f},scale:{s:.4f},duration:.6,ease:"power3.inOut"}},{ls:.3f});tl.to("#hook",{{opacity:1,y:0,duration:.3}},{ls+.3:.3f});')
# captions (word pop, active = yellow, key words red after)
for k,pg in enumerate(pages):
    st=T(pg[0])-.03; en=(T(pages[k+1][0])-.05) if k+1<len(pages) else END-.8
    a(f'tl.set("#c{k}",{{opacity:1}},{st:.3f});tl.set("#c{k}",{{opacity:0}},{max(en,st+.15):.3f});')
    for j,i in enumerate(pg):
        nxt=T(pg[j+1]) if j+1<len(pg) else en; kk=WT[i][0] in KEY
        a(f'tl.fromTo("#w{k}_{j}",{{opacity:0,scale:.55,y:24}},{{opacity:1,scale:1,y:0,duration:.2,ease:"back.out(3)"}},{T(i)-.02:.3f});')
        a(f'tl.set("#w{k}_{j}",{{color:"{YEL}"}},{T(i):.3f});tl.set("#w{k}_{j}",{{color:"{"#ff6b5e" if kk else "#ffffff"}"}},{max(nxt-.02,T(i)+.1):.3f});')
open('index.html','w').write(H+'\n'.join(js)+'\nwindow.__timelines["main"] = tl;\n</script></body></html>')
print('ok',END,len(pages))
