"""Вибір теми для наступного відео. Без LLM.

Логіка:
  * кожен запуск зберігаємо трафік кожного тренду в state/traffic_history.json;
  * тренд «росте», якщо він з'явився нещодавно (молодший за FRESH_HOURS) або його трафік
    зріс щонайменше в GROWTH разів відносно попереднього заміру;
  * кандидат мусь мати мінімальний трафік і щонайменше MIN_SOURCES незалежних джерел;
  * обмеження: не частіше одного відео на канал за CHANNEL_COOLDOWN_H годин,
    не більше DAILY_MAX відео на добу загалом (ліміт YouTube API), тема не повторюється.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .classify import rank_value
from .trends import Trend

FRESH_HOURS = 6
GROWTH = 2.0
MIN_TRAFFIC = 500
MIN_SOURCES = 2
CHANNEL_COOLDOWN_H = 4
DAILY_MAX = 6


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _load(p: Path, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def _save(p: Path, data) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def update_history(trends: list[Trend], state: Path) -> dict:
    """Дописує заміри і повертає історію {query: [[iso, traffic], ...]} (останні 48 год)."""
    p = state / "traffic_history.json"
    hist = _load(p, {})
    now = _now()
    cutoff = (now - timedelta(hours=48)).isoformat()
    for t in trends:
        hist.setdefault(t.query.lower(), []).append([now.isoformat(), t.traffic])
    hist = {k: [x for x in v if x[0] >= cutoff] for k, v in hist.items()}
    hist = {k: v for k, v in hist.items() if v}
    _save(p, hist)
    return hist


def is_rising(t: Trend, hist: dict) -> tuple[bool, str]:
    rows = hist.get(t.query.lower(), [])
    first_seen = datetime.fromisoformat(rows[0][0]) if rows else _now()
    if t.published:
        try:
            first_seen = min(first_seen, datetime.fromisoformat(t.published))
        except ValueError:
            pass
    if len(rows) >= 2 and rows[-2][1] and rows[-1][1] >= GROWTH * rows[-2][1]:
        return True, f"трафік виріс з {rows[-2][1]} до {rows[-1][1]}"
    if _now() - first_seen <= timedelta(hours=FRESH_HOURS):
        return True, "новий тренд за останні години"
    return False, "тренд уже не свіжий"


def pick_topic(candidates: list[Trend], hist: dict, state: Path) -> tuple[Trend | None, str]:
    """Повертає одну тему для відео зараз (або None) і пояснення."""
    log = _load(state / "published.json", [])   # [{query, channel, at, url}]
    now = _now()
    day_ago = (now - timedelta(hours=24)).isoformat()
    if sum(1 for x in log if x["at"] >= day_ago and x.get("url") != "ПОМИЛКА") >= DAILY_MAX:
        return None, f"денний ліміт {DAILY_MAX} відео вичерпано"
    done = {x["query"].lower() for x in log}
    reasons = []
    pool = []
    for t in candidates:
        if not t.channel or t.query.lower() in done:
            continue
        last = max((x["at"] for x in log if x["channel"] == t.channel and x.get("url") != "ПОМИЛКА"), default="")
        if last and last >= (now - timedelta(hours=CHANNEL_COOLDOWN_H)).isoformat():
            reasons.append(f"{t.query}: канал {t.channel} на паузі")
            continue
        if t.traffic < MIN_TRAFFIC:
            reasons.append(f"{t.query}: малий трафік {t.traffic}")
            continue
        if t.extra_sources and t.extra_sources < MIN_SOURCES:
            reasons.append(f"{t.query}: мало джерел ({t.extra_sources})")
            continue
        ok, why = is_rising(t, hist)
        if not ok:
            reasons.append(f"{t.query}: {why}")
            continue
        pool.append((rank_value(t), t, why))
    if not pool:
        return None, "; ".join(reasons[:6]) or "кандидатів немає"
    pool.sort(key=lambda x: x[0], reverse=True)
    _, best, why = pool[0]
    return best, why


def record_published(state: Path, query: str, channel: str, url: str = "") -> None:
    p = state / "published.json"
    log = _load(p, [])
    log.append({"query": query, "channel": channel, "at": _now().isoformat(), "url": url})
    _save(p, log[-500:])
