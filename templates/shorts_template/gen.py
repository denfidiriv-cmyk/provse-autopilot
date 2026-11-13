"""9:16 short-form template: hook (on-screen by frame 0, odometer) -> uneven pattern interrupts -> lower thirds -> word-pop captions -> loop seam back to frame 0.
Everything lives on one paused GSAP timeline that the renderer seeks frame by frame (deterministic, no timers)."""
import json
P=dict(  # ---- topic props (swap these per video) ----
 words='../nvp/wordtimes_t.json', end='../nvp/END.txt',
 hook_top='АКЦІЇ NVIDIA', hook_q='чому? ↓', pct=10, pre='ще до відкриття біржі',
 people=[dict(id='lt1',name='Дженсен Хуанг',role='засновник Nvidia · пішов з посади CEO',at=11,out=17),
         dict(id='lt2',name='Колетт Кресс',role='тимчасова CEO · фінансова директорка',at=33,out=41)],
 key={'Мінус','десять','відсотків','Хуанг','керує','відставку','скандалу','розслідування.','Тимчасово','Кресс,','нового','керівника.','Підписуйся,'},
)
WT=json.load(open(P['words'])); T=lambda i: round(WT[i][1]+0.2,3); END=float(open(P['end']).read())
ACC='#c8302a'; INK='#1e1b16'; PAPER='#e7dcc6'; CARD='#fbf7ee'; GRN='#2f6b3a'; YEL='#f5d547'
# caption pages: 1-3 words, break on punctuation
pages=[];cur=[]
for i,(w,t) in enumerate(WT):
    cur.append(i)
    if len(cur)==3 or w[-1] in '.,!:' or (len(cur)==2 and len(w)>8): pages.append(cur);cur=[]
if cur: pages.append(cur)
def L(s): return ''.join(f'<span class="ch">{c if c!=" " else "&nbsp;"}</span>' for c in s)
def reel(id_): return f'<span class="reel" id="{id_}"><span class="col">'+''.join(f'<span>{d}</span>' for d in range(10))+'</span></span>'
def tape(x,y,r): return f'<div class="tape" style="left:{x}px;top:{y}px;transform:rotate({r}deg)"></div>'
caps=''.join(f'<div class="cap" id="c{k}">'+''.join(f'<span class="w{" k" if WT[i][0] in P["key"] else ""}" id="w{k}_{j}">{WT[i][0].rstrip(".,:!")}</span>' for j,i in enumerate(pg))+'</div>' for k,pg in enumerate(pages))
lts=''.join(f'<div class="lt" id="{p["id"]}"><div class="bar"></div><div class="acc"></div><div class="nm">{p["name"]}</div><div class="rl">{p["role"]}</div></div>' for p in P['people'])
CSS=f'''
@font-face{{font-family:Play;src:url(assets/fonts/PlayfairDisplay-700.woff)}}@font-face{{font-family:PlayI;src:url(assets/fonts/PlayfairDisplay-700i.woff)}}
@font-face{{font-family:Cav;src:url(assets/fonts/Caveat-700.woff)}}@font-face{{font-family:EBGi;src:url(assets/fonts/EBGaramond-400i.woff)}}
@font-face{{font-family:UI;font-weight:800;src:url(assets/fonts/inter-cyrillic-800-normal.woff2);unicode-range:U+0400-045F,U+0490-0491}}
@font-face{{font-family:UI;font-weight:800;src:url(assets/fonts/inter-latin-800-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F,U+2190-2193,U+2212}}
@font-face{{font-family:UI;font-weight:600;src:url(assets/fonts/inter-cyrillic-600-normal.woff2);unicode-range:U+0400-045F,U+0490-0491}}
@font-face{{font-family:UI;font-weight:600;src:url(assets/fonts/inter-latin-600-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F,U+2190-2193,U+2212}}
*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1080px;height:1920px;overflow:hidden;background:{PAPER}}}
#root{{position:absolute;inset:0;overflow:hidden;background:{PAPER};color:{INK}}}
#grain{{position:absolute;inset:0;background:radial-gradient(rgba(0,0,0,.05) 2px,transparent 2px);background-size:12px 12px}}
#cam{{position:absolute;inset:0;transform-origin:50% 38%}}
.sc{{position:absolute;inset:0}}
.card{{position:absolute;background:{CARD};box-shadow:0 20px 36px rgba(70,50,20,.3);border-radius:4px}}
.tape{{position:absolute;width:280px;height:64px;background:rgba(255,255,255,.55)}}
.ch{{display:inline-block}}
/* safe box: x 90..960, y 150..1600 */
#hk{{left:0;width:1080px;top:190px;text-align:center;font:800 92px UI;letter-spacing:-.02em}}
#hkq{{position:absolute;left:0;width:1080px;top:310px;text-align:center;font:80px Cav;color:{ACC}}}
#pct{{left:120px;top:440px;width:820px;height:440px;display:flex;align-items:center;justify-content:center;font:280px/1 PlayI;color:{ACC}}}
.reel{{display:inline-block;height:280px;overflow:hidden;vertical-align:top}}.reel .col{{display:flex;flex-direction:column}}.reel .col span{{height:280px;line-height:280px}}
#pre{{position:absolute;left:260px;top:900px;padding:18px 36px;background:{YEL};font:60px Cav;transform:rotate(-3deg)}}
#news{{left:120px;top:240px;width:820px;height:640px;padding:60px 56px}}
#news .a{{font:70px Cav;color:#6b6052}}#news .b{{font:110px/1.02 Play;margin-top:16px}}#news .b em{{font-style:normal;color:{ACC}}}
#pc{{left:240px;top:200px;width:600px;height:640px;display:flex;align-items:flex-start;justify-content:center;padding-top:50px}}
#ph{{width:500px;height:500px;border-radius:50%;border:10px solid {GRN};filter:sepia(.3)}}
#stamp1{{position:absolute;left:120px;top:650px;width:840px;height:160px;border:14px solid {ACC};color:{ACC};font:70px/132px Play;text-align:center;background:rgba(251,247,238,.9);border-radius:8px}}
#yr{{left:120px;top:250px;width:820px;height:560px;display:flex;flex-direction:column;align-items:center;justify-content:center}}
#yr .lab{{font:64px Cav;color:#6b6052}}#yr .num{{font:220px/1 Play;display:flex}}#yr .num .reel,#yr .num .reel .col span{{height:220px;line-height:220px}}
#yr .sub{{font:46px EBGi;color:#6b6052;margin-top:10px}}
#stamp2{{position:absolute;left:150px;top:300px;width:780px;height:200px;border:16px solid {ACC};color:{ACC};font:110px/168px Play;text-align:center;background:rgba(251,247,238,.92);border-radius:8px}}
.note{{position:absolute;padding:20px 40px;background:{YEL};font:64px Cav;box-shadow:0 12px 24px rgba(70,50,20,.25)}}
#n1{{left:140px;top:600px}}#n2{{left:230px;top:740px;background:{CARD};font-size:58px}}
#tmp{{position:absolute;left:0;width:1080px;top:200px;text-align:center;font:120px Play;color:{ACC}}}
#av{{left:300px;top:360px;width:480px;height:480px;border-radius:50%;background:{GRN};color:#fff;font:190px/480px Play;text-align:center;box-shadow:0 20px 36px rgba(70,50,20,.3)}}
#srch{{left:120px;top:260px;width:820px;height:600px;padding:60px}}
#srch .t{{font:86px/1.08 Play}}#srch em{{font-style:normal;color:{ACC}}}
#chairq{{position:absolute;left:300px;top:560px;width:220px;height:220px;border-radius:50%;border:12px dashed {ACC};font:150px/196px Play;text-align:center;color:{ACC}}}
#cta{{left:150px;top:300px;width:780px;height:520px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px}}
#cta .a{{font:70px Cav;color:#6b6052}}#cta .b{{font:110px/1 Play}}
#sub{{position:absolute;left:250px;top:880px;width:580px;padding:22px 0;text-align:center;background:{ACC};color:#fff;font:800 60px UI;border-radius:999px;box-shadow:0 14px 26px rgba(70,50,20,.3)}}
/* lower third: lifted above bottom UI zone, left-anchored in title-safe */
.lt{{position:absolute;left:90px;top:1010px;height:190px;width:840px;opacity:0}}
.lt .bar{{position:absolute;left:0;top:0;height:190px;width:840px;background:{INK};transform-origin:0 50%}}
.lt .acc{{position:absolute;left:0;top:0;width:16px;height:190px;background:{ACC}}}
.lt .nm{{position:absolute;left:52px;top:26px;font:800 74px UI;color:#fbf7ee;white-space:nowrap}}
.lt .rl{{position:absolute;left:54px;top:118px;font:600 38px UI;color:{YEL};white-space:nowrap}}
/* captions: bold sans, stroke+shadow, center band ~66% down */
.cap{{position:absolute;left:100px;width:860px;top:1250px;text-align:center;font:800 84px/1.1 UI;text-transform:uppercase;color:#fff;
 -webkit-text-stroke:7px {INK};paint-order:stroke fill;text-shadow:0 8px 18px rgba(0,0,0,.35);opacity:0}}
.cap .w{{display:inline-block;margin:0 12px;opacity:0}}.cap .w.on{{}}
'''
H=f'''<!doctype html><html lang="uk" data-resolution="portrait"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/><script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920"><div id="grain"></div><div id="cam">
<div class="sc" id="s0"><div class="card" id="hkc" style="left:0;top:0;width:0;height:0;box-shadow:none"></div>
 <div id="hk" class="sc" style="position:absolute;height:120px">{P["hook_top"]}</div><div id="hkq">{P["hook_q"]}</div>
 <div class="card" id="pct">−{reel("r1")}{reel("r0")}%{tape(270,-30,-4)}</div><div id="pre">{P["pre"]}</div></div>
<div class="sc" id="s1"><div class="card" id="news"><div class="a">ринок зустрів новину:</div><div class="b">засновник <em>іде</em> з посади CEO</div>{tape(270,-30,3)}</div></div>
<div class="sc" id="s2"><div class="card" id="pc"><img id="ph" src="assets/img/huang.png"/>{tape(160,-30,-3)}</div><div id="stamp1">БІЛЬШЕ НЕ КЕРУЄ</div></div>
<div class="sc" id="s3"><div class="card" id="yr"><div class="lab">засновник з</div><div class="num">{reel("y3")}{reel("y2")}{reel("y1")}{reel("y0")}</div><div class="sub">понад 30 років на чолі</div>{tape(270,-30,-2)}</div></div>
<div class="sc" id="s4"><div id="stamp2">ВІДСТАВКА</div><div class="note" id="n1">скандал</div><div class="note" id="n2">внутрішнє розслідування</div></div>
<div class="sc" id="s5"><div id="tmp">{L("ТИМЧАСОВО")}</div><div class="card" id="av">КК</div></div>
<div class="sc" id="s6"><div class="card" id="srch"><div class="t">Рада директорів <em>шукає нового CEO</em></div><div id="chairq">?</div>{tape(270,-30,-3)}</div></div>
<div class="sc" id="s7"><div class="card" id="cta"><div class="a">тут усе про</div><div class="b">ЕКОНОМІКУ</div>{tape(250,-30,-4)}</div><div id="sub">ПІДПИСУЙСЯ</div></div>
</div>{lts}{caps}
<audio id="mix" class="clip" data-start="0" data-duration="{END:.2f}" data-track-index="6" data-volume="1" src="assets/sound/mix.wav"></audio>
</div><script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
const RH={{r0:280,r1:280,y0:220,y1:220,y2:220,y3:220}};
function setReel(id,d){{ document.querySelector("#"+id+" .col").style.transform="translateY("+(-d*RH[id])+"px)"; }}
'''
js=[];a=js.append
SC=['#s0','#s1','#s2','#s3','#s4','#s5','#s6','#s7']
# uneven cut points (word-aligned): hook 0, news T7, portrait T11, founder T17, resign T21, temp T28, search T36, cta T41
cuts=[0,T(7)-.08,T(11)-.08,T(17)-.08,T(21)-.17,T(28)-.08,T(36)-.08,T(41)-.08]
a(f'tl.set({json.dumps(SC[1:])},{{opacity:0}},0);')
for k in range(1,len(SC)):
    t=cuts[k]
    a(f'tl.set("{SC[k-1]}",{{opacity:0}},{t:.3f});tl.set("{SC[k]}",{{opacity:1}},{t:.3f});')
    # pattern interrupt on every cut: snap punch-in 112% -> 100% + tiny rotation
    a(f'tl.fromTo("#cam",{{scale:1.12,rotation:{(-1)**k*1.2}}},{{scale:1,rotation:0,duration:.35,ease:"power3.out"}},{t:.3f});')
def slap(sel,t,rot,dur=.26):
    a(f'tl.fromTo("{sel}",{{scale:1.35,y:-80,rotation:{rot*3},opacity:0}},{{scale:1,y:0,rotation:{rot},opacity:1,duration:{dur},ease:"power3.in"}},{t:.3f});')
    a(f'tl.to("{sel}",{{scaleY:.95,scaleX:1.04,duration:.05}},{t+dur:.3f});tl.to("{sel}",{{scaleX:1,scaleY:1,rotation:{rot*.6:.2f},duration:.45,ease:"elastic.out(1,.45)"}},{t+dur+.05:.3f});')
# HOOK: hook line + card on screen at frame 0 (no fade-up); odometer rolls 00 -> 10
a('tl.set(["#hk","#hkq","#pct"],{opacity:1},0);tl.set("#pre",{opacity:0},0);')
a('tl.call(()=>{setReel("r1",1);setReel("r0",0)},null,0);const od={v:0};tl.fromTo(od,{v:0},{v:10,duration:.7,ease:"power3.out",onUpdate(){setReel("r0",od.v%10)},onComplete(){setReel("r0",0)}},0.02);')
a('tl.fromTo("#pct",{scale:1.06},{scale:1,duration:.9,ease:"power2.out"},0);')
a('tl.fromTo("#hkq",{y:0},{y:14,duration:.45,yoyo:true,repeat:5,ease:"sine.inOut"},0.4);')
a(f'tl.fromTo("#pct",{{x:0}},{{x:"random(-14,14)",duration:.04,repeat:7,yoyo:true}},{T(1):.3f});tl.set("#pct",{{x:0}},{T(1)+.32:.3f});')
slap('#pre',T(3)-.28,-3,.22)
# s1 news
slap('#news',cuts[1],-1.5,.24)
# s2 portrait + stamp (anticipation lift then slam on "не керує")
slap('#pc',cuts[2],2,.24)
a(f'tl.fromTo("#stamp1",{{opacity:0,scale:1.8,rotation:-2}},{{opacity:.85,scale:1.55,rotation:-11,duration:.25}},{T(14)-.45:.3f});tl.to("#stamp1",{{opacity:1,scale:1,rotation:-6,duration:.13,ease:"power4.in"}},{T(14)-.13:.3f});')
a(f'tl.to("#ph",{{filter:"sepia(.3) grayscale(1) brightness(.75)",duration:.5}},{T(15):.3f});tl.fromTo("#cam",{{x:0}},{{x:"random(-12,12)",duration:.04,repeat:5,yoyo:true}},{T(14):.3f});tl.set("#cam",{{x:0}},{T(14)+.24:.3f});')
# s3 founder year reel 1993 -> 2026 (countdown-style digit roll, value from timeline progress)
slap('#yr',cuts[3],-1.5,.24)
a(f'const yr={{v:1993}};tl.fromTo(yr,{{v:1993}},{{v:2026,duration:1.0,ease:"power2.inOut",onUpdate(){{const y=Math.round(yr.v);const s=String(y);["y3","y2","y1","y0"].forEach((id,i)=>setReel(id,+s[i]))}}}},{cuts[3]+.25:.3f});')
a('tl.call(()=>{},null,0);')  # keep
# s4 resign stamp + notes
a(f'tl.fromTo("#stamp2",{{opacity:0,scale:1.9}},{{opacity:1,scale:1,rotation:-6,duration:.16,ease:"power4.in"}},{T(21)-.16:.3f});tl.to("#stamp2",{{scale:1.05,duration:.07,yoyo:true,repeat:1}},{T(21):.3f});')
slap('#n1',T(24)-.26,-4,.2); slap('#n2',T(26)-.26,3,.2)
# s5 temporary + avatar
a(f'tl.fromTo("#tmp .ch",{{opacity:0,y:-60,rotation:()=>gsap.utils.random(-20,20)}},{{opacity:1,y:0,rotation:()=>gsap.utils.random(-4,4),duration:.24,ease:"back.out(2)",stagger:.03}},{cuts[5]:.3f});')
a(f'tl.fromTo("#av",{{scale:0,opacity:1}},{{scale:1,duration:.55,ease:"back.out(2)"}},{T(29)-.1:.3f});tl.set("#av",{{opacity:0}},0);tl.set("#av",{{opacity:1}},{T(29)-.1:.3f});')
# s6 search board, ? wobble (secondary action)
slap('#srch',cuts[6],1.5,.24)
a(f'tl.fromTo("#chairq",{{rotation:-12}},{{rotation:12,duration:.4,yoyo:true,repeat:5,ease:"sine.inOut"}},{cuts[6]+.3:.3f});tl.fromTo("#chairq",{{x:0}},{{x:300,duration:1.6,ease:"sine.inOut",yoyo:true,repeat:1}},{cuts[6]+.3:.3f});')
# s7 cta: button press
slap('#cta',cuts[7],-2,.24)
a(f'tl.fromTo("#sub",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.35,ease:"back.out(2.5)"}},{T(41)+.1:.3f});tl.to("#sub",{{scale:.92,duration:.09}},{T(43):.3f});tl.to("#sub",{{scale:1,background:"#6b6052",duration:.3,ease:"back.out(3)"}},{T(43)+.09:.3f});')
# LOOP SEAM: last ~0.7s rebuild frame-0 composition (hook text + card with 00%), so the replay cut is invisible
ls=END-.7
a(f'tl.set("#s7",{{opacity:0}},{ls:.3f});tl.set("#s0",{{opacity:1}},{ls:.3f});tl.set("#pre",{{opacity:0}},{ls:.3f});')
a(f'tl.call(()=>{{setReel("r0",0);setReel("r1",1)}},null,{ls:.3f});tl.fromTo("#pct",{{scale:.9,opacity:0}},{{scale:1.06,opacity:1,duration:.5,ease:"power2.out"}},{ls:.3f});tl.fromTo(["#hk","#hkq"],{{opacity:0}},{{opacity:1,duration:.3}},{ls:.3f});')
# LOWER THIRDS: bar wipe -> name -> role (stagger), hold, faster exit
for p in P['people']:
    t0=T(p['at'])-.1; t1=T(p['out'])-.45; i=p['id']
    a(f'tl.set("#{i}",{{opacity:1}},{t0:.3f});tl.fromTo("#{i} .bar",{{scaleX:0}},{{scaleX:1,duration:.4,ease:"expo.out"}},{t0:.3f});tl.fromTo("#{i} .acc",{{scaleY:0}},{{scaleY:1,duration:.3,ease:"expo.out"}},{t0:.3f});')
    a(f'tl.fromTo("#{i} .nm",{{clipPath:"inset(0 100% 0 0)",x:-20}},{{clipPath:"inset(0 0% 0 0)",x:0,duration:.45,ease:"expo.out"}},{t0+.13:.3f});tl.fromTo("#{i} .rl",{{opacity:0,y:16}},{{opacity:1,y:0,duration:.35,ease:"expo.out"}},{t0+.26:.3f});')
    a(f'tl.to("#{i}",{{x:-60,opacity:0,duration:.28,ease:"power2.in"}},{t1:.3f});')
# CAPTIONS: page-in, each word pops on its own start (overshoot), active word = accent
for k,pg in enumerate(pages):
    st=T(pg[0])-.03; en=(T(pages[k+1][0])-.05) if k+1<len(pages) else END-.75
    a(f'tl.set("#c{k}",{{opacity:1}},{st:.3f});tl.set("#c{k}",{{opacity:0}},{max(en,st+.15):.3f});')
    for j,i in enumerate(pg):
        nxt=T(pg[j+1]) if j+1<len(pg) else en
        k_cls = WT[i][0] in P['key']
        a(f'tl.fromTo("#w{k}_{j}",{{opacity:0,scale:.55,y:24}},{{opacity:1,scale:1,y:0,duration:.22,ease:"back.out(3)"}},{T(i)-.02:.3f});')
        a(f'tl.set("#w{k}_{j}",{{color:"{"#f5d547" if k_cls else "#f5d547"}"}},{T(i):.3f});tl.set("#w{k}_{j}",{{color:"{"#ff6b5e" if k_cls else "#ffffff"}"}},{max(nxt-.02,T(i)+.1):.3f});')
open('index.html','w').write(H+'\n'.join(js)+'\nwindow.__timelines["main"] = tl;\n</script></body></html>')
print('ok',END,len(pages))
