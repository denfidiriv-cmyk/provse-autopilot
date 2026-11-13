"""Автопілот PROВсе з Claude Code: тренд -> Claude Code зі скілами робить ролик -> приватно на YouTube -> Telegram.

Код (дешево) обирає тему й збирає джерела. Claude Code (headless, зі скілами з приватного репозиторію)
пише сценарій, озвучує, монтує і перевіряє кадри. Код завантажує приватно й надсилає власнику з кнопками.

  python run_claude.py           # бойовий режим
  python run_claude.py --test    # найсильніший тренд без правил свіжості, нічого не записує у стан
Змінні: CC_BUDGET_USD (ліміт на один ролик, за замовчуванням 3), CC_DAILY_MAX (роликів на добу, 4), CC_MODEL.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

from pipeline import notify, select
from pipeline.classify import classify, load_config, rank_value
from pipeline.trends import fetch_news, fetch_trends

ROOT = Path(__file__).resolve().parent
STATE, JOB = ROOT / "state", ROOT / "job"


def runs_today() -> list:
    p = STATE / "cc_runs.json"
    runs = json.loads(p.read_text()) if p.exists() else []
    cut = (datetime.now() - timedelta(days=1)).isoformat()
    return [r for r in runs if r["at"] >= cut]


def log_run(entry: dict) -> None:
    p = STATE / "cc_runs.json"
    runs = json.loads(p.read_text()) if p.exists() else []
    p.write_text(json.dumps((runs + [entry])[-200:], ensure_ascii=False, indent=1))


def probe(mp4: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                          "-of", "json", str(mp4)], capture_output=True, text=True).stdout
    j = json.loads(out or "{}")
    v = [s for s in j.get("streams", []) if s.get("codec_type") == "video"]
    return {"dur": float(j.get("format", {}).get("duration", 0)), "w": v[0]["width"] if v else 0,
            "h": v[0]["height"] if v else 0, "audio": any(s.get("codec_type") == "audio" for s in j.get("streams", []))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    STATE.mkdir(exist_ok=True)
    ctl = notify.control(STATE)
    if ctl.get("actions"):
        notify.run_actions(ctl)
        (STATE / "control.json").write_text(json.dumps(ctl))
    if ctl["paused"]:
        print("пауза"); return 0
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("немає ANTHROPIC_API_KEY"); return 0
    daily = int(os.environ.get("CC_DAILY_MAX") or 4)
    if not a.test and len(runs_today()) >= daily:
        print(f"денний ліміт Claude Code {daily} вичерпано"); return 0

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
    from pipeline.research import gather
    from pipeline.script import CHANNEL_NOTES, TOPIC
    tried = set()
    for attempt in range(3):  # якщо Claude відмовився від теми (мало фактів), беремо наступну
        left = [t for t in cands if t.query not in tried]
        if a.test:
            pool = sorted(left, key=rank_value, reverse=True)
            topic, why = (pool[0], "тест: найсильніший тренд") if pool else (None, "кандидатів немає")
        else:
            topic, why = select.pick_topic(left, hist, STATE)
        if not topic:
            print("тему не обрано:", why); return 0
        tried.add(topic.query)
        ch = cfg["channels"][topic.channel]
        print(f"ТЕМА: {topic.query} -> {ch['name']} ({why})")

        shutil.rmtree(JOB, ignore_errors=True); JOB.mkdir()
        recent = json.loads((STATE / "styles.json").read_text()) if (STATE / "styles.json").exists() else []
        brief = {"query": topic.query, "traffic": topic.traffic_label, "channel": topic.channel, "channel_name": ch["name"],
                 "channel_note": CHANNEL_NOTES.get(topic.channel, ""), "topic_word": TOPIC[topic.channel], "voice": ch["voice"],
                 "materials": gather(topic), "recent_styles": recent[-12:]}
        try:  # перевірені факти з двома джерелами через веб-пошук Claude (без доступу до файлів і команд)
            from pipeline.claude import web_research
            brief["verified_facts"] = web_research(topic.query, brief["channel_note"], brief["materials"])
        except Exception as e:
            print("web_research:", e); brief["verified_facts"] = {}
        print("матеріали:", [(m["source"], len(m["text"])) for m in brief["materials"]],
              "| перевірених фактів:", len(brief["verified_facts"].get("facts", [])))
        (JOB / "brief.json").write_text(json.dumps(brief, ensure_ascii=False, indent=1), encoding="utf-8")

        budget = os.environ.get("CC_BUDGET_USD") or "3"
        # Безпека: Claude Code бачить лише ключі для моделі й озвучки (жодних YouTube/Telegram/GitHub токенів),
        # має явний список дозволених інструментів і не ходить в інтернет інструментами пошуку (матеріали вже зібрані кодом).
        safe_env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "TZ", "HF_BROWSER", "ANTHROPIC_API_KEY",
                                               "GEMINI_API_KEY", "GEMINI_TTS_MODEL", "MUSIC_DIR") if os.environ.get(k)}
        allowed = ["Read", "Write", "Edit", "Glob", "Grep", "Skill", "Bash(python:*)", "Bash(python3:*)", "Bash(ffmpeg:*)",
                   "Bash(ffprobe:*)", "Bash(npx:*)", "Bash(node:*)", "Bash(npm:*)", "Bash(ls:*)", "Bash(mkdir:*)", "Bash(cp:*)"]
        cmd = ["claude", "-p", (ROOT / "prompts" / "claude_video.md").read_text(encoding="utf-8"),
               "--model", os.environ.get("CC_MODEL") or "claude-sonnet-5-5", "--max-budget-usd", budget,
               "--allowedTools", *allowed, "--disallowedTools", "WebFetch", "WebSearch",
               "--output-format", "json"]
        t0 = time.time()
        res = subprocess.run(cmd, cwd=ROOT, env=safe_env, capture_output=True, text=True, timeout=50 * 60)
        try:
            info = json.loads(res.stdout.strip().splitlines()[-1])
        except Exception:
            info = {}
        cost = info.get("total_cost_usd", 0)
        print(f"Claude Code: {time.time() - t0:.0f} с, ${cost:.2f}, ходів {info.get('num_turns')}")
        print((info.get("result") or res.stdout[-2000:] or res.stderr[-2000:])[:3000])

        meta_p, mp4 = JOB / "meta.json", JOB / "final.mp4"
        meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
        entry = {"at": datetime.now().isoformat(), "query": topic.query, "channel": topic.channel, "cost": cost}
        if meta.get("skip"):
            print("Claude відмовився від теми:", meta["skip"])
            if not a.test:
                select.record_published(STATE, topic.query, topic.channel, "ПОМИЛКА"); log_run(entry)
            continue
        break
    else:
        print("жодна тема не пройшла"); return 0
    p = probe(mp4) if mp4.exists() else {}
    if not p or not (10 <= p["dur"] <= 45 and p["w"] == 1080 and p["h"] == 1920 and p["audio"]) or not meta.get("title"):
        notify.send(f"⚠️ Claude Code не зробив коректний ролик «{notify.esc(topic.query)}» для {ch['name']} (${cost:.2f}). {p}")
        if not a.test:
            select.record_published(STATE, topic.query, topic.channel, "ПОМИЛКА"); log_run(entry)
        return 1

    out = ROOT / "out" / f"{datetime.now():%Y%m%d_%H%M}_{topic.channel}.mp4"; out.parent.mkdir(exist_ok=True)
    shutil.copy(mp4, out)
    desc = meta.get("description", "") + "\n\nДжерела:\n" + "\n".join(f"{s['name']}: {s['url']}" for s in meta.get("sources", []))
    if meta.get("photo_credits"):
        desc += "\n\n" + "\n".join(meta["photo_credits"])
    tags = [h.lstrip("#").replace(" ", "") for h in meta.get("hashtags", [])]
    desc += "\n\n" + " ".join("#" + h for h in tags)
    from pipeline.youtube import upload
    url = upload(topic.channel, out, meta["title"], desc, tags, "private")
    if not a.test:
        select.record_published(STATE, topic.query, topic.channel, url); log_run({**entry, "url": url})
    (STATE / "styles.json").write_text(json.dumps((recent + [meta.get("style", "?")])[-30:], ensure_ascii=False))

    trend_url = "https://trends.google.com/trends/explore?geo=UA&date=now%201-d&q=" + urllib.parse.quote(topic.query)
    vid = url.rsplit("/", 1)[-1]
    msg = (f"🎬 <b>{ch['name']}</b>\nТренд: <a href=\"{trend_url}\">{notify.esc(topic.query)}</a> ({topic.traffic_label} пошуків)\n"
           f"<a href=\"{url}\">Відкрити на YouTube</a>\n\nВідео приватне, чекає твого рішення.")
    btns = [{"text": "✅ Опублікувати", "callback_data": f"pub:{topic.channel}:{vid}"},
            {"text": "🗑 Видалити", "callback_data": f"del:{topic.channel}:{vid}"}]
    try:
        notify.send_video(out, msg, btns)
    except Exception as e:
        print("telegram video:", e); notify.send(msg)
    frames = " ".join(f"-ss {t} -i {out}" for t in (0.3, p["dur"] * .25, p["dur"] * .5, p["dur"] * .75, p["dur"] - .3))
    subprocess.run(f"ffmpeg -loglevel error -y {frames} -filter_complex hstack=5,scale=1600:-1 -frames:v 1 -update 1 "
                   f"{STATE / 'last_preview.jpg'}", shell=True, check=False)
    print("ГОТОВО", url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
