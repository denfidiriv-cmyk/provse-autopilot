"""Автопілот PROВсе: тренд -> факти -> сценарій -> озвучка -> монтаж -> YouTube Shorts.

Один запуск = максимум одне відео. GitHub Actions запускає це кожні 30 хвилин.
Сценарій: Claude API (якщо є ANTHROPIC_API_KEY), інакше Gemini. Озвучка: Gemini TTS. Завантаження: YouTube Data API.

  python run_autopilot.py              # бойовий режим
  python run_autopilot.py --demo       # офлайн-перевірка монтажу на тестовому сценарії й голосі, без ключів
  python run_autopilot.py --no-upload  # усе, крім завантаження на YouTube
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
import wave
from datetime import datetime
from pathlib import Path

from pipeline import audio, notify, render, select
from pipeline.classify import classify, load_config
from pipeline.trends import fetch_news, fetch_trends

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state"
WORK = ROOT / "work"
THEMES = list(render.THEMES)


def duration(p: Path) -> float:
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def produce(spec: dict, wt: list, voice_wav: Path, channel: str, out_mp4: Path, theme: str, photo_dir: Path, find_photos=True) -> dict:
    end = round(duration(voice_wav) + .2 + 1.0, 2)
    photos = {}
    if find_photos:
        from pipeline.photos import find_photo
        for k, sc in enumerate(spec["scenes"]):
            if sc.get("photo_query"):
                try:
                    ph = find_photo(sc["photo_query"], photo_dir / f"p{k}.jpg")
                    if ph:
                        photos[k] = ph
                except Exception as e:
                    print("photo:", e, file=sys.stderr)
    T = lambda i: wt[min(i, len(wt) - 1)][1] + .2
    cuts = [0.0] + [T(s["from_word"]) - .08 for s in spec["scenes"][1:]]
    stamps = []
    for k, s in enumerate(spec["scenes"]):
        if s.get("stamp") and s.get("type") != "cta":
            en = cuts[k + 1] if k + 1 < len(cuts) else end
            stamps.append(cuts[k] + min(.7, (en - cuts[k]) / 2) + .22)
    mix = audio.mix(voice_wav, end, channel, cuts, stamps, WORK / "mix.wav")
    render.render(spec, wt, end, theme, photos, channel, mix, WORK / "hf", out_mp4)
    return photos


def demo() -> int:
    """Перевірка без ключів: тестовий сценарій + вже записаний голос."""
    spec = json.loads((ROOT / "tests/fixtures/script_demo.json").read_text(encoding="utf-8"))
    voice_raw = ROOT / "tests/fixtures/voice_demo.wav"
    from pipeline.voice import tighten_and_align
    WORK.mkdir(exist_ok=True)
    wt = tighten_and_align(voice_raw, spec["script"].split(), WORK / "voice.wav")
    out = ROOT / "out" / "demo.mp4"; out.parent.mkdir(exist_ok=True)
    theme = os.environ.get("DEMO_THEME", "chalk")
    produce(spec, wt, WORK / "voice.wav", "ekonomika", out, theme, WORK, find_photos=os.environ.get("DEMO_PHOTOS") == "1")
    print("demo:", out)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--no-upload", action="store_true")
    a = ap.parse_args()
    if a.demo:
        return demo()
    STATE.mkdir(exist_ok=True); WORK.mkdir(exist_ok=True)
    ctl = notify.control(STATE)
    cfg = load_config(ROOT / "config" / "channels.json")
    trends = fetch_trends("UA")
    for t in trends:
        classify(t, cfg)
    hist = select.update_history(trends, STATE)
    cands = [t for t in trends if t.channel]
    for t in cands:
        try:
            t.extra_sources = len({n.source for n in fetch_news(t.query) if n.source}); time.sleep(.7)
        except Exception:
            pass
    if not os.environ.get("GEMINI_API_KEY"):  # озвучка поки лише через Gemini TTS (у Claude немає синтезу мови)
        print("GEMINI_API_KEY не задано: лише збираю тренди"); return 0
    if ctl["paused"]:
        print("пауза: відео не роблю"); return 0
    topic, why = select.pick_topic(cands, hist, STATE)
    if not topic:
        print("тему не обрано:", why); return 0
    ch = cfg["channels"][topic.channel]
    print(f"ТЕМА: {topic.query} -> {ch['name']} ({why})")
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    try:
        from pipeline.research import gather
        from pipeline.script import write_script
        from pipeline.voice import synth, tighten_and_align
        mats = gather(topic)
        spec = write_script(topic.query, topic.channel, mats)
        (WORK / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
        raw = synth(spec["script"], ch["voice"], WORK / "voice_raw.wav")
        wt = tighten_and_align(raw, spec["script"].split(), WORK / "voice.wav")
        n_pub = len(json.loads((STATE / "published.json").read_text())) if (STATE / "published.json").exists() else 0
        theme = THEMES[n_pub % len(THEMES)]
        out = ROOT / "out" / f"{stamp}_{topic.channel}.mp4"; out.parent.mkdir(exist_ok=True)
        photos = produce(spec, wt, WORK / "voice.wav", topic.channel, out, theme, WORK)
        desc = spec["description"] + "\n\nДжерела:\n" + "\n".join(f"{s['name']}: {s['url']}" for s in spec["sources"])
        if photos:
            desc += "\n\n" + "\n".join(f"{p['credit']} ({p.get('page', '')})" for p in photos.values())
        desc += "\n\n" + " ".join("#" + h.lstrip("#").replace(" ", "") for h in spec.get("hashtags", []))
        url = ""
        if not a.no_upload:
            from pipeline.youtube import upload
            url = upload(topic.channel, out, spec["title"], desc, spec.get("hashtags", []), os.environ.get("YT_PRIVACY", "public"))
        select.record_published(STATE, topic.query, topic.channel, url)
        notify.send(f"🎬 <b>{ch['name']}</b>\n{spec['title']}\nТренд: {topic.query} ({topic.traffic_label})\n{url or 'не завантажено (--no-upload)'}\n\n{spec['script']}")
        print("ГОТОВО", url or out)
    except Exception as e:
        traceback.print_exc()
        select.record_published(STATE, topic.query, topic.channel, "ПОМИЛКА")  # щоб не зациклитися на тій самій темі
        notify.send(f"⚠️ Не вийшло зробити відео «{topic.query}» для {ch['name']}: {str(e)[:300]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
