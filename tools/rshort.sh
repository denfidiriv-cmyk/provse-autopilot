#!/bin/bash
# Трендовий шортс у Remotion: docs/trend_shorts/<name>.json + картки big_card -> /mnt/user-data/outputs/short_<name>.mp4
#   bash tools/rshort.sh <name> <style> [cards.json ...]
# style: cards | paper | kinetic | board | radar. Музика й мікс як раніше (cc_mix.py), картинка рендериться remotion_short.
# env: VIDEO_SCENES='{"1":"clip.mp4"}' (кліп з <vid>/ замість фото сцени 1), BG=x.jpg (тло стилю radar з <img>/), PROPS_PATCH='{...}'.
exec 9>/tmp/rshort.lock; flock 9
cd "$(dirname "$0")/.." || exit 1
n=$1; style=$2; shift 2
J=$(python3 -c "import json;print(json.load(open('docs/trend_shorts/$n.json'))['job'])"); mood=$(python3 -c "import json;print(json.load(open('docs/trend_shorts/$n.json')).get('mood','upbeat'))")
python3 tools/attic_short.py docs/trend_shorts/$n.json || exit 1
python3 tools/trend_build.py $J > /dev/null || exit 1
MUSIC_DIR=${MUSIC_DIR:-assets_cache/music_cc} python3 tools/cc_mix.py $J $mood "" 2>&1 | head -1
python3 tools/remotion_props.py $n "$@" > /dev/null || exit 1
python3 - "$n" "$style" <<'PY'
import json,os,sys
p=f'remotion_short/props/{sys.argv[1]}.json';d=json.load(open(p));d['style']=sys.argv[2]
import shutil
spec=json.load(open(f'docs/trend_shorts/{sys.argv[1]}.json'));media=f'remotion_short/public/media/{sys.argv[1]}'
for i,f in json.loads(os.environ.get('VIDEO_SCENES','{}')).items():   # {"1":"snowcar.mp4"} from <vid>/
    shutil.copy(os.path.join(spec['vid'],f),media);d['scenes'][int(i)]['video']=f'media/{sys.argv[1]}/{os.path.basename(f)}'
if os.environ.get('BG'):                                               # radar backdrop from <img>/
    shutil.copy(os.path.join(spec['img'],os.environ['BG']),media);d['bgSrc']=f'media/{sys.argv[1]}/{os.environ["BG"]}'
d.update(json.loads(os.environ.get('PROPS_PATCH','{}')));json.dump(d,open(p,'w'),ensure_ascii=False,indent=1)
PY
B=${HF_BROWSER:-$(ls -d /opt/pw-browsers/chromium-*/chrome-linux64/chrome 2>/dev/null | tail -1)}
(cd remotion_short && npx remotion render Short $J/rm.mp4 --props=props/$n.json --browser-executable=$B --crf=18 --concurrency=${CONC:-2} > $J/rm.log 2>&1) || { tail -5 $J/rm.log; exit 1; }
O=/mnt/user-data/outputs/short_$n.mp4
ffmpeg -v error -y -i $J/rm.mp4 -c:v libx264 -crf 24 -maxrate 3M -bufsize 6M -preset veryfast -c:a aac -b:a 160k -movflags +faststart $O && cp $O /mnt/user-data/uploads/out/
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $O)
python3 - "$O" "$D" "$J/sheet.jpg" <<'PY'
import sys,subprocess
from PIL import Image
v,D,o=sys.argv[1],float(sys.argv[2]),sys.argv[3]
im=Image.new('RGB',(8*240,427))
for i in range(8):
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(D*(i+0.6)/8),'-i',v,'-frames:v','1','-vf','scale=240:427','/tmp/rs_f.png'])
  im.paste(Image.open('/tmp/rs_f.png'),(240*i,0))
im.save(o)
PY
echo "dur $D $(grep -m1 -o 'музика:.*' $J/mix.log 2>/dev/null)"
