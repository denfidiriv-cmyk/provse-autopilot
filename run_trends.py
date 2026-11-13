"""Агент трендів: раз на кілька годин читає Google Trends (Україна), розкладає тренди по каналах,
перевіряє кількість незалежних джерел у Google News, відкидає вже бачені теми і надсилає звіт у Telegram.
Жодного LLM, жодних кредитів: лише HTTP-запити до відкритих RSS.

Запуск:
  python run_trends.py                 # звичайний запуск
  python run_trends.py --no-news       # без перевірки Google News (швидше)
  python run_trends.py --fixture tests/fixtures/trends_ua.xml --no-news --dry   # офлайн-тест
Змінні середовища (файл .env поруч): TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID. Без них звіт лише зберігається у out/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline.classify import classify, load_config, rank_value
from pipeline.trends import fetch_news, fetch_trends, parse_trends_rss

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
SEEN = OUT / "seen_trends.json"


def load_env(path: Path = ROOT / ".env") -> None:
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def load_seen(days: int = 3) -> dict:
    if not SEEN.exists():
        return {}
    seen = json.loads(SEEN.read_text(encoding="utf-8"))
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    return {k: v for k, v in seen.items() if v >= cutoff}


def send_telegram(text: str) -> bool:
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        return False
    for i in range(0, len(text), 3800):  # ліміт Telegram 4096 символів
        data = urllib.parse.urlencode({"chat_id": chat, "text": text[i:i + 3800], "parse_mode": "HTML",
                                       "disable_web_page_preview": "true"}).encode()
        urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/sendMessage", data=data, timeout=20).read()
    return True


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_report(cfg: dict, picked: dict, skipped: list, stamp: str) -> tuple[str, str]:
    md = [f"# Тренди Україна, {stamp}", ""]
    tg = [f"<b>Тренди Україна · {esc(stamp)}</b>"]
    for key, ch in cfg["channels"].items():
        items = picked.get(key, [])
        md.append(f"## {ch['name']}")
        tg.append(f"\n<b>{esc(ch['name'])}</b>")
        if not items:
            md.append("- нових трендів немає, можна зробити пізнавальне відео на тему каналу")
            tg.append("· нових трендів немає")
        for t in items:
            src = f", джерел у Google News: {t.extra_sources}" if t.extra_sources else ""
            md.append(f"- **{t.query}** ({t.traffic_label or t.traffic} пошуків{src}; збіг: {', '.join(t.matched)})")
            line = f"· <b>{esc(t.query)}</b> {esc(t.traffic_label)}"
            if t.extra_sources:
                line += f" · джерел: {t.extra_sources}"
            tg.append(line)
            for n in t.news[:2]:
                md.append(f"  - [{n.title}]({n.url}) · {n.source}")
                tg.append(f"   ↳ <a href=\"{esc(n.url)}\">{esc(n.title[:90])}</a> ({esc(n.source)})")
        md.append("")
    if skipped:
        md.append("## Пропущено")
        md += [f"- {t.query}: {t.skipped_reason}" for t in skipped]
    return "\n".join(md), "\n".join(tg)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", help="локальний XML замість запиту до Google (для тестів)")
    ap.add_argument("--no-news", action="store_true", help="не рахувати джерела в Google News")
    ap.add_argument("--dry", action="store_true", help="не надсилати в Telegram і не позначати тренди як бачені")
    ap.add_argument("--per-channel", type=int, default=3)
    a = ap.parse_args()
    load_env()
    cfg = load_config(ROOT / "config" / "channels.json")
    OUT.mkdir(exist_ok=True)

    trends = parse_trends_rss(Path(a.fixture).read_bytes()) if a.fixture else fetch_trends("UA")
    seen = {} if a.dry else load_seen()
    picked, skipped = {}, []
    for t in trends:
        classify(t, cfg)
        if not t.channel:
            skipped.append(t)
            continue
        if t.query.lower() in seen:
            continue
        if not a.no_news:
            try:
                t.extra_sources = len({n.source for n in fetch_news(t.query) if n.source})
                time.sleep(1.0)  # ввічливо до Google
            except Exception as e:  # мережа, ліміт, тощо: звіт однаково буде
                print("news:", t.query, e, file=sys.stderr)
        picked.setdefault(t.channel, []).append(t)
    for k in picked:
        picked[k] = sorted(picked[k], key=rank_value, reverse=True)[: a.per_channel]

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    md, tg = build_report(cfg, picked, skipped, stamp)
    base = OUT / f"trends_{datetime.now():%Y-%m-%d_%H%M}"
    base.with_suffix(".md").write_text(md, encoding="utf-8")
    base.with_suffix(".json").write_text(json.dumps(
        {k: [t.__dict__ | {"news": [n.__dict__ for n in t.news]} for t in v] for k, v in picked.items()},
        ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "latest_trends.json").write_text(base.with_suffix(".json").read_text(encoding="utf-8"), encoding="utf-8")

    sent = False if a.dry else send_telegram(tg)
    if not a.dry:
        now = datetime.now(timezone.utc).isoformat()
        for v in picked.values():
            for t in v:
                seen[t.query.lower()] = now
        SEEN.write_text(json.dumps(seen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(md)
    print(f"\nЗвіт: {base.with_suffix('.md')}  Telegram: {'надіслано' if sent else 'ні'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
