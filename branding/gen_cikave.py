import asyncio, os
from playwright.async_api import async_playwright
F="/tmp/claude-0/-home-claude/1aa8b6ad-0ff9-5c05-a29e-50e8238d6250/scratchpad/myth2/代码工程/lib/fonts"
CSS=f"@font-face{{font-family:O;src:url(file://{F}/Oswald-700.woff)}}body{{margin:0}} .w{{position:relative;overflow:hidden}} svg{{position:absolute;inset:0}}"
def label(cx,y,name,c1,c2,s=1):
  return f'<g transform="translate({cx},{y}) scale({s})"><text x="0" y="0" font-family="O" font-size="40" fill="{c1}" text-anchor="middle" letter-spacing="8">ВСЕ ПРО</text><text x="0" y="78" font-family="O" font-size="84" fill="{c2}" text-anchor="middle" letter-spacing="3">{name}</text></g>'
# політика: темно-синій, будівля з колонами і терези
def parl(cx,cy,s):
  cols=''.join(f'<rect x="{-150+i*66}" y="-60" width="36" height="170" fill="#f4efe1"/>' for i in range(5))
  return f'''<g transform="translate({cx},{cy}) scale({s})"><path d="M-210,-70 L0,-190 L210,-70Z" fill="#f4efe1"/><circle cx="0" cy="-112" r="22" fill="#c9a227"/>
  <rect x="-200" y="-70" width="400" height="22" fill="#c9a227"/>{cols}<rect x="-215" y="110" width="430" height="26" fill="#f4efe1"/><rect x="-240" y="136" width="480" height="26" fill="#c9a227"/></g>'''
def pol_bg(w,h): return f'<rect width="{w}" height="{h}" fill="#14233f"/>'+''.join(f'<path d="M{x},0V{h}" stroke="#1d3157" stroke-width="{w/40}"/>' for x in range(0,w,int(w/10)))
def pol_av(): return f'<div class="w" style="width:800px;height:800px"><svg viewBox="0 0 800 800">{pol_bg(800,800)}{parl(400,330,1.15)}<rect x="150" y="575" width="500" height="165" fill="none" stroke="#c9a227" stroke-width="5"/>{label(400,630,"ПОЛІТИКУ","#c9a227","#f4efe1")}</svg></div>'
def pol_ban(): return f'<div class="w" style="width:2560px;height:1440px"><svg viewBox="0 0 2560 1440">{pol_bg(2560,1440)}{parl(930,720,0.62)}<text x="1130" y="670" font-family="O" font-size="60" fill="#c9a227" letter-spacing="10">ВСЕ ПРО</text><text x="1126" y="800" font-family="O" font-size="140" fill="#f4efe1">ПОЛІТИКУ</text><text x="1130" y="870" font-family="O" font-size="38" fill="#9fb2d6">закони · виплати · рішення влади · сценарії подій</text></svg></div>'
# спорт: зелене поле, м'яч
def ball(cx,cy,r):
  import math
  pent=lambda a,b,q,rot=0:'<polygon points="'+' '.join(f"{a+q*math.cos(math.radians(rot+72*k-90)):.1f},{b+q*math.sin(math.radians(rot+72*k-90)):.1f}" for k in range(5))+'" fill="#17191c"/>'
  out=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fbfbf6" stroke="#17191c" stroke-width="{r*0.06}"/><clipPath id="b{cx}"><circle cx="{cx}" cy="{cy}" r="{r*0.97}"/></clipPath><g clip-path="url(#b{cx})">'+pent(cx,cy,r*0.3)
  for k in range(5):
    a=math.radians(72*k-90); out+=pent(cx+r*0.92*math.cos(a),cy+r*0.92*math.sin(a),r*0.3,36+72*k)+f'<path d="M{cx+r*0.3*math.cos(a):.1f},{cy+r*0.3*math.sin(a):.1f} L{cx+r*0.68*math.cos(a):.1f},{cy+r*0.68*math.sin(a):.1f}" stroke="#17191c" stroke-width="{r*0.05}"/>'
  return out+'</g>'
def sp_bg(w,h): return ''.join(f'<rect x="{x}" y="0" width="{w/8}" height="{h}" fill="{"#1f8a4c" if i%2 else "#23994f"}"/>' for i,x in enumerate([w/8*k for k in range(8)]))
def sp_av(): return f'<div class="w" style="width:800px;height:800px"><svg viewBox="0 0 800 800">{sp_bg(800,800)}<circle cx="400" cy="320" r="250" fill="none" stroke="#ffffff" stroke-opacity=".8" stroke-width="8"/><path d="M0,320H800" stroke="#ffffff" stroke-opacity=".8" stroke-width="8"/>{ball(400,320,170)}<g transform="translate(400,655) rotate(-3)"><rect x="-240" y="-95" width="480" height="180" rx="18" fill="#17191c"/>{label(0,-40,"СПОРТ","#ffd23f","#ffffff")}</g></svg></div>'
def sp_ban(): return f'<div class="w" style="width:2560px;height:1440px"><svg viewBox="0 0 2560 1440">{sp_bg(2560,1440)}<circle cx="1280" cy="720" r="330" fill="none" stroke="#ffffff" stroke-opacity=".5" stroke-width="8"/><path d="M1280,0V1440" stroke="#ffffff" stroke-opacity=".5" stroke-width="8"/><rect x="800" y="560" width="960" height="320" rx="24" fill="#17191c"/>{ball(940,720,105)}<text x="1090" y="680" font-family="O" font-size="56" fill="#ffd23f" letter-spacing="10">ВСЕ ПРО</text><text x="1086" y="800" font-family="O" font-size="130" fill="#ffffff">СПОРТ</text><text x="1090" y="852" font-family="O" font-size="32" fill="#cfd6d1">матчі · бої · рахунки · рекорди</text></svg></div>'
# розваги: фіолетовий, зірка і прожектори
def star(cx,cy,r,col="#ffd23f"):
  import math
  pts=' '.join(f"{cx+(r if k%2==0 else r*0.45)*math.cos(math.radians(36*k-90)):.1f},{cy+(r if k%2==0 else r*0.45)*math.sin(math.radians(36*k-90)):.1f}" for k in range(10))
  return f'<polygon points="{pts}" fill="{col}" stroke="#1c1030" stroke-width="{r*0.07}" stroke-linejoin="round"/>'
def en_bg(w,h,cx,cy): return f'<rect width="{w}" height="{h}" fill="#3b1d6e"/><path d="M{cx-w*0.42},0 L{cx},{cy} L{cx-w*0.2},0Z" fill="#ffffff" fill-opacity=".10"/><path d="M{cx+w*0.42},0 L{cx},{cy} L{cx+w*0.2},0Z" fill="#ffffff" fill-opacity=".10"/>'+''.join(f'<circle cx="{(i*197)%w}" cy="{(i*131)%h}" r="{4+i%3*2}" fill="#ff5fa2" fill-opacity=".7"/>' for i in range(1,26))
def en_av(): return f'<div class="w" style="width:800px;height:800px"><svg viewBox="0 0 800 800">{en_bg(800,800,400,330)}{star(400,320,210)}<g transform="translate(400,655) rotate(-3)"><rect x="-250" y="-95" width="500" height="180" rx="18" fill="#ff5fa2" stroke="#1c1030" stroke-width="8"/>{label(0,-40,"ЦІКАВЕ","#1c1030","#ffffff")}</g></svg></div>'
def en_ban(): return f'<div class="w" style="width:2560px;height:1440px"><svg viewBox="0 0 2560 1440">{en_bg(2560,1440,940,720)}{star(940,720,150)}<text x="1140" y="670" font-family="O" font-size="60" fill="#ff5fa2" letter-spacing="10">ВСЕ ПРО</text><text x="1136" y="800" font-family="O" font-size="140" fill="#ffffff">ЦІКАВЕ</text><text x="1140" y="870" font-family="O" font-size="38" fill="#d9c8ff">погода · прикмети · свята · несподівані факти</text></svg></div>'
JOBS=[('cikave_avatar.png',en_av,800,800),('cikave_banner.png',en_ban,2560,1440)]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--allow-file-access-from-files'])
    for fn,f,w,h in JOBS:
      pg=await b.new_page(viewport={'width':w,'height':h}); open('t.html','w').write(f"<html><head><style>{CSS}</style></head><body>{f()}</body></html>")
      await pg.goto('file://'+os.path.abspath('t.html')); await pg.wait_for_timeout(600); await pg.screenshot(path=fn); await pg.close()
    await b.close()
asyncio.run(main())
