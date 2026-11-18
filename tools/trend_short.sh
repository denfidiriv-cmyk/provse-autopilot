#!/bin/bash
# Трендовий шортс з docs/trend_shorts/<name>.json -> <job>/final.mp4 + <job>/sheet.jpg
#   bash tools/trend_short.sh <name>
# Кроки: attic_short.py (вирівнює час слів через cc_align.py, якщо в src є script.txt) -> trend_build.py -> cc_mix.py -> kit_render.py -> контактний аркуш.
cd "$(dirname "$0")/.." || exit 1
n=$1; J=$(python3 -c "import json;print(json.load(open('docs/trend_shorts/$n.json'))['job'])"); mood=$(python3 -c "import json;print(json.load(open('docs/trend_shorts/$n.json')).get('mood','upbeat'))")
python3 tools/attic_short.py docs/trend_shorts/$n.json || exit 1
python3 tools/trend_build.py $J || exit 1
MUSIC_DIR=${MUSIC_DIR:-assets_cache/music_cc} python3 tools/cc_mix.py $J $mood "" 2>&1 | head -1
B=${HF_BROWSER:-$(ls -d /opt/pw-browsers/chromium-*/chrome-linux64/chrome 2>/dev/null | tail -1)}
rm -f $J/final.mp4; HF_BROWSER=$B python3 tools/kit_render.py $J $J/hf $J/mix.wav > $J/render.log 2>&1
[ -f $J/final.mp4 ] || { tail -3 $J/render.log; exit 1; }
rm -rf "$J/hf/renders"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $J/final.mp4)
mkdir -p $J/fr; rm -f $J/fr/*
python3 - "$J" "$D" <<'PY'
import sys,subprocess
from PIL import Image,ImageDraw
J,D=sys.argv[1],float(sys.argv[2]);ts=[0]+[round(D*i/9,1) for i in range(1,10)]
im=Image.new('RGB',(5*216,2*384))
for i,t in enumerate(ts):
  f=f'{J}/fr/{t}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(min(t,D-.1)),'-i',J+'/final.mp4','-frames:v','1','-vf','scale=216:384',f])
  x=Image.open(f);ImageDraw.Draw(x).text((5,5),str(t),fill='yellow');im.paste(x,(216*(i%5),384*(i//5)))
im.save(J+'/sheet.jpg');print('dur',D)
PY
