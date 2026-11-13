"""Створює проєкт hyperframes з motion kit для одного ролика.

  python tools/kit_new.py <job_dir> <out_dir> [--bg "#0f1115"] [--no-plate]

Бере <job_dir>/words.json і END.txt, копіює templates/kit у <out_dir> і пише index.html-заготовку:
сцени ти дописуєш між <!--SCENES--> і <!--/SCENES-->, анімацію між //TIMELINE і ///TIMELINE.
Субтитри-караоке вже підключені (Kit.captions). Рендер: python tools/kit_render.py <job_dir> <out_dir> <audio.wav>
"""
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("job"); ap.add_argument("out")
ap.add_argument("--bg", default="#0f1115")
ap.add_argument("--no-plate", action="store_true", help="субтитри з обведенням без плашки (лише для дуже темного фону)")
a = ap.parse_args()
job, out = Path(a.job), Path(a.out)
words = json.loads((job / "words.json").read_text(encoding="utf-8"))
end = float((job / "END.txt").read_text())
if out.exists():
    shutil.rmtree(out)
shutil.copytree(ROOT / "templates" / "kit", out)
(out / "assets" / "img").mkdir(exist_ok=True)
(out / "assets" / "sound").mkdir(exist_ok=True)

html = f"""<!doctype html><html lang="uk"><head><meta charset="utf-8">
<link rel="stylesheet" href="assets/kit.css">
<style>
:root{{--bg:{a.bg};--cap-y:1240px;--cap-size:84px}}
/* Стилі сцен цього ролика */
</style>
<script src="assets/gsap.min.js"></script><script src="assets/kit.js"></script></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{end:.2f}" data-width="1080" data-height="1920">
  <div id="cam">
<!--SCENES-->
    <section class="scene" id="s1"><!-- ХУК: головна цифра/факт, видно з першого кадру --></section>
<!--/SCENES-->
  </div>
  <div id="caps"></div><div id="flash"></div><div id="grain"></div>
  <audio id="mix" class="clip" data-start="0" data-duration="{end:.2f}" data-track-index="6" data-volume="1" src="assets/sound/mix.wav"></audio>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{paused: true}});
const WORDS = {json.dumps(words, ensure_ascii=False)};
const END = {end:.2f};
Kit.init(WORDS);
const T = Kit.T;
tl.set("#s1", {{visibility: "visible"}}, 0);
//TIMELINE

///TIMELINE
Kit.captions(tl, {{keywords: [], plate: {str(not a.no_plate).lower()}, end: END}});
tl.set({{}}, {{}}, END);
window.__timelines["main"] = tl;
</script></body></html>
"""
(out / "index.html").write_text(html, encoding="utf-8")
print(f"проєкт: {out} | слів {len(words)} | кінець {end:.2f} с")
