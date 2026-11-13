import json, random
rnd=random.Random(7)
WT=json.load(open('../nvp/wordtimes_t.json')); T=lambda i: round(WT[i][1]+0.2,3); C=lambda i: round(T(i)-0.08,3)
END=float(open('../nvp/END.txt').read())
c1,c2,c3,c4=C(7),C(17),C(28),C(41)
KEY={'Мінус','десять','відсотків','біржі!','Хуанг','керує','Nvidia.','Засновник','відставку','скандалу','розслідування.','Тимчасово','Колетт','Кресс,','нового','керівника.','Підписуйся,'}
# caption chunks of 2-3 words, break on punctuation
chunks=[];cur=[]
for i,(w,t) in enumerate(WT):
    cur.append((i,w)); 
    if len(cur)==3 or w[-1] in '.,!:' or (len(cur)==2 and len(w)>9): chunks.append(cur);cur=[]
if cur: chunks.append(cur)
def L(s): return ''.join(f'<span class="ch">{c if c!=" " else "&nbsp;"}</span>' for c in s)
caps=''.join(f'<div class="cap" id="c{k}">'+' '.join(f'<span class="w{" k" if w in KEY else ""}" id="w{k}_{j}">{w.rstrip(".,:!")}</span>' for j,(i,w) in enumerate(ch))+'</div>' for k,ch in enumerate(chunks))
CSS='''
@font-face{font-family:Play;src:url(assets/fonts/PlayfairDisplay-700.woff)}@font-face{font-family:PlayI;src:url(assets/fonts/PlayfairDisplay-700i.woff)}
@font-face{font-family:Cav;src:url(assets/fonts/Caveat-700.woff)}@font-face{font-family:EBG;src:url(assets/fonts/EBGaramond-600.woff)}@font-face{font-family:EBGi;src:url(assets/fonts/EBGaramond-400i.woff)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#e7dcc6}
#root{position:absolute;inset:0;overflow:hidden;background:#e7dcc6;color:#1e1b16;font-family:EBG}
#grain{position:absolute;inset:0;background:radial-gradient(rgba(0,0,0,.05) 2px,transparent 2px);background-size:12px 12px}
#cam{position:absolute;inset:0;transform-origin:50% 40%}
.sc{position:absolute;inset:0}
.card{position:absolute;background:#fbf7ee;box-shadow:0 20px 36px rgba(70,50,20,.3);border-radius:4px}
.tape{position:absolute;width:300px;height:68px;background:rgba(255,255,255,.55);box-shadow:0 2px 6px rgba(0,0,0,.08)}
.ch{display:inline-block}
.head{position:absolute;left:0;width:1080px;text-align:center;font:112px Play;color:#c8302a}
.note{position:absolute;padding:22px 40px;background:#f5d547;font:64px Cav;box-shadow:0 12px 24px rgba(70,50,20,.25)}
#chart{left:80px;top:330px;width:920px;height:540px;padding:44px}
#chart .t{font:96px Play;color:#2f6b3a}
#chart svg{position:absolute;left:30px;top:150px}
#big{position:absolute;left:0;width:1080px;top:920px;text-align:center;font:300px/1 PlayI;color:#c8302a}
#pre{left:250px;top:1230px}
#pc{left:150px;top:300px;width:780px;height:860px;display:flex;flex-direction:column;align-items:center;padding-top:60px}
#ph{width:470px;height:470px;border-radius:50%;border:10px solid #2f6b3a;filter:sepia(.3)}
#nm{font:66px Play;margin-top:40px}#role{position:relative;margin-top:16px;font:46px EBG;color:#6b6052}
#strike{position:absolute;left:-10px;right:-10px;top:52%;height:8px;background:#c8302a;transform-origin:0 50%}
#found{left:300px;top:150px;transform:rotate(-3deg)}
#stamp{position:absolute;left:190px;top:1030px;width:700px;height:200px;border:14px solid #c8302a;color:#c8302a;font:96px/172px Play;text-align:center;background:rgba(251,247,238,.85);border-radius:8px}
#n1{left:110px;top:1230px;background:#f5d547}#n2{left:330px;top:1360px;background:#fbf7ee;font-size:58px}
#kk{left:80px;top:330px;width:920px;height:330px;padding:0 54px;display:flex;align-items:center;gap:44px}
#av{width:200px;height:200px;border-radius:50%;background:#2f6b3a;color:#fff;font:80px/200px Play;text-align:center;flex:none}
#kk b{display:block;font:68px Play;font-weight:normal}#kk span{display:block;font:40px EBGi;color:#6b6052;margin-top:12px}
#srch{left:80px;top:730px;width:920px;height:440px;padding:56px}
#srch .t{font:64px Play}#srch em{font-style:normal;color:#c8302a}
#scrib{position:absolute;left:56px;top:250px}
#endc{left:190px;top:420px;width:700px;height:560px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:30px}
#endc .a{font:60px Cav;color:#6b6052}#endc .b{font:104px/1.05 Play;text-align:center}
#sub{left:240px;top:1080px;width:600px;padding:26px 0;text-align:center;background:#c8302a;color:#fff;font:84px Cav;box-shadow:0 14px 26px rgba(70,50,20,.3)}
.cap{position:absolute;left:60px;width:960px;top:1500px;text-align:center;font:100px/1.05 Cav;opacity:0}
.cap .w{opacity:.25}.cap .k{color:#c8302a}
'''
def tape(x,y,r): return f'<div class="tape" style="left:{x}px;top:{y}px;transform:rotate({r}deg)"></div>'
HTML=f'''<!doctype html><html lang="uk" data-resolution="portrait"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/><script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920"><div id="grain"></div><div id="cam">
<div class="sc" id="s1">
 <div class="card" id="chart"><div class="t">NVIDIA</div><svg width="860" height="380" viewBox="0 0 860 380"><path id="up" d="M30 300 L140 255 L250 275 L360 190 L470 215 L580 120" fill="none" stroke="#2f6b3a" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/><path id="dn" d="M580 120 L660 270 L700 235 L820 350" fill="none" stroke="#c8302a" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></svg>{tape(380,-30,-4)}</div>
 <div id="big">−10%</div>
 <div class="note" id="pre">ще до відкриття біржі</div>
</div>
<div class="sc" id="s2">
 <div class="head" id="h2" style="top:150px">{L("БІЛЬШЕ НЕ КЕРУЄ")}</div>
 <div class="card" id="pc"><img id="ph" src="assets/img/huang.png"/><div id="nm">Дженсен Хуанг</div><div id="role">CEO Nvidia<div id="strike"></div></div>{tape(240,-30,3)}</div>
 <div class="note" id="found">Засновник · з 1993</div>
 <div id="stamp">ВІДСТАВКА</div>
 <div class="note" id="n1">скандал</div><div class="note" id="n2">внутрішнє розслідування</div>
</div>
<div class="sc" id="s4">
 <div class="head" id="h4" style="top:150px">{L("ТИМЧАСОВО")}</div>
 <div class="card" id="kk"><div id="av">КК</div><div><b>Колетт Кресс</b><span>фінансова директорка → тимчасова CEO</span></div>{tape(560,-28,5)}</div>
 <div class="card" id="srch"><div class="t">Рада директорів <em>шукає нового CEO</em></div>
  <svg id="scrib" width="800" height="150" viewBox="0 0 800 150"><path id="sc" d="M10 90 C 80 20, 140 140, 210 70 S 330 30, 390 90 S 520 140, 580 60 S 700 40, 790 90" fill="none" stroke="#2f6b3a" stroke-width="9" stroke-linecap="round"/><circle id="q" cx="700" cy="60" r="44" fill="none" stroke="#c8302a" stroke-width="9"/></svg>{tape(300,-28,-3)}</div>
</div>
<div class="sc" id="s5">
 <div class="card" id="endc"><div class="a">тут усе про</div><div class="b">ЕКОНОМІКУ</div>{tape(200,-28,-4)}</div>
 <div class="note" id="sub">Підписуйся!</div>
</div>
</div>{caps}
<audio id="mix" class="clip" data-start="0" data-duration="{END:.2f}" data-track-index="6" data-volume="1" src="assets/sound/mix.wav"></audio>
</div><script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
'''
js=[];a=js.append
def slap(sel,t,rot,dur=.3):  # paper card falls onto table: lifted (bigger, softer shadow) -> lands (squash) -> settles (overlap)
    a(f'tl.fromTo("{sel}",{{opacity:0,scale:1.35,y:-90,rotation:{rot*3}}},{{opacity:1,scale:1,y:0,rotation:{rot},duration:{dur},ease:"power3.in"}},{t:.3f});')
    a(f'tl.to("{sel}",{{scaleY:.96,scaleX:1.03,duration:.06,ease:"power1.out"}},{t+dur:.3f});tl.to("{sel}",{{scaleY:1,scaleX:1,rotation:{rot*.7:.2f},duration:.5,ease:"elastic.out(1,.45)"}},{t+dur+.06:.3f});')
    a(f'tl.fromTo("#cam",{{y:0}},{{y:6,duration:.05,yoyo:true,repeat:1}},{t+dur:.3f});')
def sweep(sel,t,dx=-1300): a(f'tl.to("{sel}",{{x:{dx},rotation:-12,duration:.32,ease:"power3.in"}},{t:.3f});')
a('tl.set(["#s2","#s4","#s5"],{opacity:0},0);tl.set(["#pre","#found","#stamp","#n1","#n2","#sub"],{opacity:0},0);')
# S1
slap('#chart',0,-2,.25)
a('tl.fromTo("#up",{strokeDasharray:900,strokeDashoffset:900},{strokeDashoffset:0,duration:.4,ease:"power2.out"},.2);')
a('tl.fromTo("#dn",{strokeDasharray:400,strokeDashoffset:400},{strokeDashoffset:0,duration:.35,ease:"expo.in"},.55);')
slap('#big',0.12,-3,.28)
slap('#pre',T(3)-0.3,-4,.22)
a('tl.to("#cam",{scale:1.04,duration:'+str(c1)+',ease:"none"},0);')
sweep('#s1',c1-0.32)
# S2
a(f'tl.set("#s2",{{opacity:1}},{c1-.05});tl.set("#cam",{{scale:1}},{c1});')
slap('#pc',c1-.05,2,.28)
a(f'tl.fromTo("#h2 .ch",{{opacity:0,y:-60,rotation:()=>gsap.utils.random(-20,20)}},{{opacity:1,y:0,rotation:()=>gsap.utils.random(-4,4),duration:.25,ease:"back.out(2)",stagger:.03}},{T(13)-.3:.3f});')
a(f'tl.fromTo("#strike",{{scaleX:0}},{{scaleX:1,duration:.3,ease:"power2.inOut"}},{T(14)-.1:.3f});tl.to("#ph",{{filter:"sepia(.3) grayscale(1) brightness(.75)",duration:.6}},{T(15):.3f});')
a(f'tl.to("#h2",{{opacity:0,y:-40,duration:.2}},{c2-.15:.3f});tl.to("#pc",{{y:-60,scale:.82,rotation:-3,duration:.45,ease:"power3.inOut"}},{c2:.3f});')
slap('#found',c2+.05,-3,.25)
# stamp: anticipation (lift up big) then slam
a(f'tl.fromTo("#stamp",{{opacity:0,scale:1.9,rotation:-2}},{{opacity:.9,scale:1.6,rotation:-12,duration:.3,ease:"power2.out"}},{T(21)-.6:.3f});tl.to("#stamp",{{opacity:1,scale:1,rotation:-8,duration:.14,ease:"power4.in"}},{T(21)-.14:.3f});')
a(f'tl.to("#stamp",{{scale:1.04,duration:.08,yoyo:true,repeat:1}},{T(21):.3f});tl.fromTo("#cam",{{x:0}},{{x:"random(-14,14)",duration:.04,repeat:5,yoyo:true}},{T(21):.3f});tl.set("#cam",{{x:0}},{T(21)+.25:.3f});')
slap('#n1',T(24)-.28,-5,.22); slap('#n2',T(26)-.28,3,.22)
sweep('#s2',c3-.32)
# S4
a(f'tl.set("#s4",{{opacity:1}},{c3-.05});')
a(f'tl.fromTo("#h4 .ch",{{opacity:0,y:-60,rotation:()=>gsap.utils.random(-20,20)}},{{opacity:1,y:0,rotation:()=>gsap.utils.random(-4,4),duration:.25,ease:"back.out(2)",stagger:.035}},{c3:.3f});')
a(f'tl.set(["#kk","#srch"],{{opacity:0}},0);')
slap('#kk',T(33)-.35,-1.5,.28)
a(f'tl.fromTo("#av",{{scale:0}},{{scale:1,duration:.5,ease:"back.out(2.2)"}},{T(33)-.05:.3f});')
slap('#srch',T(36)-.3,1.5,.28)
a(f'tl.fromTo("#sc",{{strokeDasharray:1200,strokeDashoffset:1200}},{{strokeDashoffset:0,duration:1.2,ease:"power1.inOut"}},{T(37):.3f});tl.fromTo("#q",{{strokeDasharray:300,strokeDashoffset:300}},{{strokeDashoffset:0,duration:.4}},{T(39):.3f});')
a(f'tl.to("#q",{{x:-500,duration:1.2,ease:"sine.inOut",yoyo:true,repeat:1}},{T(39)+.4:.3f});')
sweep('#s4',c4-.32,1300)
# S5
a(f'tl.set("#s5",{{opacity:1}},{c4-.05});')
slap('#endc',c4-.05,-2,.28); slap('#sub',c4+.35,-3,.22)
a(f'tl.to("#sub",{{scale:.92,duration:.09}},{c4+1.2:.3f});tl.to("#sub",{{scale:1,background:"#6b6052",duration:.3,ease:"back.out(3)"}},{c4+1.29:.3f});tl.call(()=>{{document.querySelector("#sub").textContent="Ти з нами ✓"}},null,{c4+1.25:.3f});')
# captions
for k,ch in enumerate(chunks):
    st=T(ch[0][0])-.04; en=(T(chunks[k+1][0][0])-.06) if k+1<len(chunks) else END-.05
    a(f'tl.fromTo("#c{k}",{{opacity:0,y:20,rotation:{rnd.uniform(-2,2):.1f}}},{{opacity:1,y:0,duration:.12,ease:"power2.out"}},{st:.3f});')
    for j,(i,w) in enumerate(ch): a(f'tl.to("#w{k}_{j}",{{opacity:1,duration:.05}},{T(i):.3f});')
    a(f'tl.to("#c{k}",{{opacity:0,duration:.06}},{max(en-.06,st+.14):.3f});')
open('index.html','w').write(HTML+'\n'.join(js)+'\nwindow.__timelines["main"] = tl;\n</script></body></html>')
print('ok',END,len(chunks))
