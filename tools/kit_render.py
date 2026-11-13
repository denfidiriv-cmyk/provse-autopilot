"""Рендер проєкту kit у готовий ролик і аркуш кадрів для перевірки.

  python tools/kit_render.py <job_dir> <project_dir> <audio.wav>

1) кладе audio.wav у project/assets/sound/mix.wav; 2) hyperframes render (30 fps);
3) збирає <job_dir>/final.mp4 (H.264 yuv420p + AAC, faststart);
4) пише <job_dir>/check.jpg: 12 кадрів поспіль (0,3 с ... кінець) і <job_dir>/check_motion.jpg: кадри кожні 0,1 с
   біля першої склейки, щоб побачити, чи анімація плавна. Подивись обидва зображення інструментом Read.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

job, proj, audio = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
shutil.copy(audio, proj / "assets" / "sound" / "mix.wav")
env = dict(os.environ)
if env.get("HF_BROWSER"):
    env.setdefault("PUPPETEER_EXECUTABLE_PATH", env["HF_BROWSER"]); env.setdefault("HYPERFRAMES_BROWSER_PATH", env["HF_BROWSER"])
for p in proj.glob("renders/*.mp4"):
    p.unlink()
subprocess.run(["npx", "--yes", "hyperframes@0.8.216", "render", "--fps", "30", "--quality", "delivery"], cwd=proj, env=env, check=True)
raw = sorted(proj.glob("renders/*.mp4"), key=lambda p: p.stat().st_mtime)[-1]
final = job / "final.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-i", str(audio), "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                "-shortest", "-movflags", "+faststart", str(final)], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)],
                           capture_output=True, text=True).stdout)
ts = [0.3 + k * (dur - 0.6) / 11 for k in range(12)]
inputs = sum((["-ss", f"{t:.2f}", "-i", str(final)] for t in ts), [])
grid = "".join(f"[{k}:v]scale=270:-1[v{k}];" for k in range(12)) + "".join(f"[v{k}]" for k in range(12)) + "xstack=inputs=12:layout=" + \
    "|".join(f"{(k % 6) * 270}_{(k // 6) * 480}" for k in range(12))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", grid, "-frames:v", "1", str(job / "check.jpg")], check=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0", "-t", "1.2", "-i", str(final), "-vf",
                "fps=10,scale=180:-1,tile=6x2", "-frames:v", "1", str(job / "check_motion.jpg")], check=True)
print(f"готово: {final} ({dur:.2f} с); перевір {job / 'check.jpg'} і {job / 'check_motion.jpg'}")
