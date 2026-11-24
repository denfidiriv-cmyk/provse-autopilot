import asyncio, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from playwright.async_api import async_playwright
F=os.path.abspath(os.path.join(os.path.dirname(__file__),'../work/hf/assets/fonts'))
CSS=f"@font-face{{font-family:O;src:url(file://{F}/Oswald-700.woff)}}body{{margin:0}} .w{{position:relative;overflow:hidden}} svg{{position:absolute;inset:0}}"
def label(cx,y,name,c1,c2,s=1):
  return f'<g transform="translate({cx},{y}) scale({s})"><text x="0" y="0" font-family="O" font-size="40" fill="{c1}" text-anchor="middle" letter-spacing="8">ВСЕ ПРО</text><text x="0" y="98" font-family="O" font-size="92" fill="{c2}" text-anchor="middle" letter-spacing="4">{name}</text></g>'
# багатоповерхівка з вікнами, частина світиться теплим
def house(cx,cy,s):
  win=''
  lit={(0,1),(1,3),(2,0),(3,2),(1,0),(3,4),(0,4),(2,3)}
  for r in range(5):
    for c in range(4):
      col="#ffc857" if (c,r) in lit else "#2b3a55"
      win+=f'<rect x="{-150+c*80}" y="{-210+r*72}" width="50" height="46" rx="4" fill="{col}"/>'
  return f'''<g transform="translate({cx},{cy}) scale({s})"><rect x="-190" y="-250" width="380" height="430" rx="10" fill="#f4efe1"/>{win}
  <rect x="-35" y="120" width="70" height="60" fill="#c0503a"/><rect x="-230" y="180" width="460" height="22" fill="#c0503a"/>
  <path d="M-60,-250 v-40 h30 v40" fill="#c0503a"/></g>'''
def bg(w,h): return f'<rect width="{w}" height="{h}" fill="#1b2a44"/>'+''.join(f'<circle cx="{(i*173)%w}" cy="{(i*97)%(h*0.45)}" r="{2+i%3}" fill="#ffffff" fill-opacity=".35"/>' for i in range(1,30))
def av(): return f'<div class="w" style="width:800px;height:800px"><svg viewBox="0 0 800 800">{bg(800,800)}{house(400,300,0.85)}<g transform="translate(400,600) rotate(-3)"><rect x="-210" y="-85" width="420" height="200" rx="18" fill="#c0503a"/>{label(0,-25,"ОСББ","#ffc857","#ffffff")}</g></svg></div>'
def ban(): return f'<div class="w" style="width:2560px;height:1440px"><svg viewBox="0 0 2560 1440">{bg(2560,1440)}{house(960,700,0.75)}<text x="1180" y="670" font-family="O" font-size="60" fill="#ffc857" letter-spacing="10">ВСЕ ПРО</text><text x="1176" y="810" font-family="O" font-size="150" fill="#f4efe1">ОСББ</text><text x="1180" y="880" font-family="O" font-size="38" fill="#b9c6e0">опалення · лічильники · тарифи · ваш будинок</text></svg></div>'
JOBS=[('osbb_avatar.png',av,800,800),('osbb_banner.png',ban,2560,1440)]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--allow-file-access-from-files'])
    for fn,f,w,h in JOBS:
      pg=await b.new_page(viewport={'width':w,'height':h}); open('t.html','w').write(f"<html><head><style>{CSS}</style></head><body>{f()}</body></html>")
      await pg.goto('file://'+os.path.abspath('t.html')); await pg.wait_for_timeout(600); await pg.screenshot(path=fn); await pg.close()
    await b.close()
asyncio.run(main())
