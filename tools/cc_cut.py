"""Вирізає предмет з фото без фону (rembg, isnet-general-use) -> прозорий PNG, щільно обрізаний.

  python tools/cc_cut.py <фото> <вихід.png>

Працює для окремих предметів (техніка, авто, їжа, прилад). Будівлі й краєвиди не вирізаються:
їх став просто фото без рамки й підпису.
"""
import sys
from PIL import Image
from rembg import new_session, remove

im = Image.open(sys.argv[1]).convert("RGB"); im.thumbnail((1600, 1600))
o = remove(im, session=new_session("isnet-general-use"))
a = o.split()[3]; o.putalpha(a.point(lambda v: 0 if v < 40 else v))
b = a.point(lambda v: 255 if v > 140 else 0).getbbox()
o.crop((max(0, b[0] - 10), max(0, b[1] - 10), b[2] + 10, b[3] + 10)).save(sys.argv[2])
print(sys.argv[2], o.size)
