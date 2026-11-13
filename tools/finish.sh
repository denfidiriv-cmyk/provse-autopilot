#!/bin/bash
set -e
p=$1; cd $(dirname $0)/${p}fr
ffmpeg -y -loglevel error -i ../$p/film_raw.mp4 -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p -g 30 -an assets/vid/film.mp4
python3 build.py >/dev/null; rm -rf renders
HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome timeout 1800 npx --yes hyperframes@0.8.216 render --fps 30 --quality delivery > render.log 2>&1
R=$(ls renders/*.mp4)
ffmpeg -y -loglevel error -i $R -c:v libx264 -b:v 1900k -pass 1 -passlogfile p$p -preset slow -an -f null /dev/null
ffmpeg -y -loglevel error -i $R -i final_mix.wav -map 0:v -map 1:a -c:v libx264 -b:v 1900k -pass 2 -passlogfile p$p -preset slow -pix_fmt yuv420p -c:a aac -b:a 160k -shortest -movflags +faststart ${p}_final.mp4
cp ${p}_final.mp4 /mnt/user-data/uploads/out/
ls -la ${p}_final.mp4
