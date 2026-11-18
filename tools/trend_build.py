"""Вставляє css.txt, scenes.txt і tl.txt (від attic_short.py) у hf/index.html роботи.  python tools/trend_build.py <job>"""
import re,sys
J=sys.argv[1]
f=J+"/hf/index.html"; h=open(f).read()
css=open(J+"/css.txt").read(); scenes=open(J+"/scenes.txt").read(); tl=open(J+"/tl.txt").read()
h=h.replace("/* Стилі сцен цього ролика */","/* Стилі сцен цього ролика */"+css)
h=re.sub(r"<!--SCENES-->.*?<!--/SCENES-->",lambda m:scenes,h,flags=re.S)
h=re.sub(r"//TIMELINE.*?///TIMELINE",lambda m:tl,h,flags=re.S)
open(f,"w").write(h)
