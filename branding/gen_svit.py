import asyncio, os
from playwright.async_api import async_playwright
F="/tmp/claude-0/-home-claude/1aa8b6ad-0ff9-5c05-a29e-50e8238d6250/scratchpad/myth2/代码工程/lib/fonts"
CSS=f"@font-face{{font-family:O;src:url(file://{F}/Oswald-700.woff)}}body{{margin:0}} .w{{position:relative;overflow:hidden}} svg{{position:absolute;inset:0}}"
def label(cx,y,name,c1,c2,s=1):
  return f'<g transform="translate({cx},{y}) scale({s})"><text x="0" y="0" font-family="O" font-size="40" fill="{c1}" text-anchor="middle" letter-spacing="8">ВСЕ ПРО</text><text x="0" y="78" font-family="O" font-size="84" fill="{c2}" text-anchor="middle" letter-spacing="3">{name}</text></g>'
# політика: темно-синій, будівля з колонами і терези

def globe(cx,cy,r):
  cont=[ "M-0.55,-0.45 C-0.35,-0.7 -0.05,-0.62 0.02,-0.42 C0.1,-0.22 -0.12,-0.12 -0.2,0.05 C-0.28,0.25 -0.45,0.2 -0.55,0.02 C-0.68,-0.15 -0.66,-0.32 -0.55,-0.45Z",
         "M0.15,-0.05 C0.35,-0.15 0.6,-0.05 0.62,0.15 C0.64,0.38 0.42,0.55 0.25,0.48 C0.1,0.42 0.05,0.2 0.15,-0.05Z",
         "M0.25,-0.62 C0.4,-0.7 0.6,-0.55 0.55,-0.4 C0.48,-0.3 0.3,-0.35 0.25,-0.62Z",
         "M-0.25,0.45 C-0.12,0.4 0.02,0.55 -0.05,0.68 C-0.15,0.76 -0.3,0.62 -0.25,0.45Z"]
  g=f'<g transform="translate({cx},{cy})"><circle r="{r}" fill="#2a9d8f"/><g transform="scale({r})" fill="#e9c46a">'+''.join(f'<path d="{d}"/>' for d in cont)+'</g>'
  g+=''.join(f'<ellipse rx="{r*k}" ry="{r}" fill="none" stroke="#ffffff" stroke-opacity=".35" stroke-width="{r*0.025}"/>' for k in (0.35,0.72))
  g+=''.join(f'<path d="M{-r*abs(1-(y*y)) ** .5:.1f},{y*r:.1f}H{r*abs(1-(y*y))**.5:.1f}" stroke="#ffffff" stroke-opacity=".35" stroke-width="{r*0.025}"/>' for y in (-0.5,0,0.5))
  g+=f'<circle r="{r}" fill="none" stroke="#073b3a" stroke-width="{r*0.06}"/>'
  # heart badge = добрі новини
  hx,hy,hs=r*0.62,-r*0.66,r*0.36
  g+=f'<g transform="translate({hx},{hy}) scale({hs/50})"><circle r="50" fill="#e76f51" stroke="#073b3a" stroke-width="6"/><path d="M0,22 C-30,2 -28,-22 -12,-24 C-4,-25 0,-18 0,-14 C0,-18 4,-25 12,-24 C28,-22 30,2 0,22Z" fill="#fff"/></g></g>'
  return g
def sv_bg(w,h,cx,cy): return f'<rect width="{w}" height="{h}" fill="#0f3d47"/>'+''.join(f'<path d="M{cx},{cy} L{cx+3000*__import__("math").cos(a/12*6.283):.0f},{cy+3000*__import__("math").sin(a/12*6.283):.0f} L{cx+3000*__import__("math").cos((a+.5)/12*6.283):.0f},{cy+3000*__import__("math").sin((a+.5)/12*6.283):.0f}Z" fill="#ffffff" fill-opacity=".05"/>' for a in range(12))
def sv_av(): return f'<div class="w" style="width:800px;height:800px"><svg viewBox="0 0 800 800">{sv_bg(800,800,400,320)}{globe(400,320,215)}<g transform="translate(400,655) rotate(-3)"><rect x="-240" y="-95" width="480" height="180" rx="18" fill="#f4a261" stroke="#073b3a" stroke-width="8"/>{label(0,-40,"СВІТ","#073b3a","#ffffff")}</g></svg></div>'
def sv_ban(): return f'<div class="w" style="width:2560px;height:1440px"><svg viewBox="0 0 2560 1440">{sv_bg(2560,1440,940,720)}{globe(930,720,170)}<text x="1150" y="670" font-family="O" font-size="60" fill="#f4a261" letter-spacing="10">ВСЕ ПРО</text><text x="1146" y="800" font-family="O" font-size="140" fill="#ffffff">СВІТ</text><text x="1150" y="870" font-family="O" font-size="38" fill="#bfe3dc">добрі та дивовижні новини з усіх куточків планети</text></svg></div>'
JOBS=[('svit_avatar.png',sv_av,800,800),('svit_banner.png',sv_ban,2560,1440)]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--allow-file-access-from-files'])
    for fn,f,w,h in JOBS:
      pg=await b.new_page(viewport={'width':w,'height':h}); open('t.html','w').write(f"<html><head><style>{CSS}</style></head><body>{f()}</body></html>")
      await pg.goto('file://'+os.path.abspath('t.html')); await pg.wait_for_timeout(600); await pg.screenshot(path=fn); await pg.close()
    await b.close()
asyncio.run(main())
