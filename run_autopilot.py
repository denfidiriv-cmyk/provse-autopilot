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


def duration(p: Path) -> float:
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def produce(spec: dict, wt: list, voice_wav: Path, channel: str, out_mp4: Path, theme: str, photo_dir: Path, find_photos=True) -> dict:
    print("стиль:", theme, "| музика:", spec.get("music_mood"))
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
    mix = audio.mix(voice_wav, end, channel, cuts, stamps, WORK / "mix.wav", mood=spec.get("music_mood", ""))
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
    theme = os.environ.get("DEMO_THEME", "chalkboard__hand")
    produce(spec, wt, WORK / "voice.wav", "ekonomika", out, theme, WORK, find_photos=os.environ.get("DEMO_PHOTOS") == "1")
    print("demo:", out)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--test", action="store_true", help="взяти найсильніший тренд без правил свіжості, нічого не публікувати і не записувати")
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
    if a.test:
        a.no_upload = True
    has_llm = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not has_llm:
        print("немає ключа ні Claude, ні Gemini: лише збираю тренди"); return 0
    if ctl["paused"]:
        print("пауза: відео не роблю"); return 0
    from pipeline.classify import rank_value
    from pipeline.research import gather
    from pipeline.script import write_script
    from pipeline.voice import synth, tighten_and_align
    tried, topic, spec = set(), None, None
    for attempt in range(3):  # якщо модель відмовилась від теми (не підходить каналу, мало фактів), беремо наступну
        if a.test:
            pool = [t for t in sorted(cands, key=rank_value, reverse=True) if t.query not in tried]
            topic, why = (pool[0], "тестовий режим: найсильніший тренд") if pool else (None, "кандидатів немає")
        else:
            topic, why = select.pick_topic([t for t in cands if t.query not in tried], hist, STATE)
        if not topic:
            print("тему не обрано:", why); return 0
        tried.add(topic.query)
        ch = cfg["channels"][topic.channel]
        print(f"ТЕМА: {topic.query} -> {ch['name']} ({why})")
        try:
            from pipeline import themes
            recent = json.loads((STATE / "styles.json").read_text()) if (STATE / "styles.json").exists() else []
            options = themes.shortlist(recent)
            spec = write_script(topic.query, topic.channel, gather(topic), themes.describe(options))
            if spec.get("style") not in themes.ALL:
                spec["style"] = options[0]
            (STATE / "styles.json").write_text(json.dumps((recent + [spec["style"]])[-30:]))
            break
        except ValueError as e:
            print("відмова:", e)
            if not a.test:
                select.record_published(STATE, topic.query, topic.channel, "ПОМИЛКА")
            spec = None
    if not spec:
        print("жодна тема не пройшла перевірку"); return 0
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    try:
        (WORK / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(spec, ensure_ascii=False, indent=1))
        if not os.environ.get("GEMINI_API_KEY"):  # озвучка лише через Gemini TTS: у Claude немає синтезу мови
            notify.send(f"📝 Сценарій для {ch['name']} (озвучки ще немає, бо немає GEMINI_API_KEY):\n\n{spec['script']}")
            print("Сценарій готовий, озвучки немає (немає GEMINI_API_KEY)"); return 0
        raw = synth(spec["script"], ch["voice"], WORK / "voice_raw.wav")
        wt = tighten_and_align(raw, spec["script"].split(), WORK / "voice.wav")
        theme = spec["style"]
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
        if not a.test:
            select.record_published(STATE, topic.query, topic.channel, url)
        import urllib.parse as _u
        trend_url = "https://trends.google.com/trends/explore?geo=UA&date=now%201-d&q=" + _u.quote(topic.query)
        msg = (f"🎬 <b>{ch['name']}</b>\n"
               f"Тренд: <a href=\"{trend_url}\">{notify.esc(topic.query)}</a> ({topic.traffic_label} пошуків)\n"
               + (f"<a href=\"{url}\">Відкрити на YouTube</a>" if url else "Тест, на YouTube не завантажено"))
        try:
            notify.send_video(out, msg)
        except Exception as ex:
            print("telegram video:", ex); notify.send(msg)
        try:  # контактний лист кадрів для перевірки
            import subprocess
            frames = [f"-ss {t} -i {out}" for t in (0.3, 3, 7, 11, 15)]
            cmd = "ffmpeg -loglevel error -y " + " ".join(frames) + " -filter_complex hstack=5,scale=1600:-1 -frames:v 1 -update 1 " + str(STATE / "last_preview.jpg")
            subprocess.run(cmd, shell=True, check=False)
        except Exception:
            pass
        print("ГОТОВО", url or out)
    except Exception as e:
        traceback.print_exc()
        if not a.test:
            select.record_published(STATE, topic.query, topic.channel, "ПОМИЛКА")  # щоб не зациклитися на тій самій темі
        notify.send(f"⚠️ Не вийшло зробити відео «{topic.query}» для {ch['name']}: {str(e)[:300]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
