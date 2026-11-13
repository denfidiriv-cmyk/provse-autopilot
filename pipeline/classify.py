"""Розподіл трендів по каналах за ключовими словами з config/channels.json. Без LLM.

Правила ключових слів:
  "основа"      збіг із початком будь-якого слова ("світл" ловить "світло", "світла")
  "=слово"      точний збіг слова ("=гол" не ловить "голова")
  "фраза з пробілом"  пошук фрази в тексті ("припинення вогню")
Назва тренду важить утричі більше, ніж заголовки новин.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .trends import Trend

WORD = re.compile(r"[\w'’ʼ-]+", re.U)


def load_config(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _norm(s: str) -> str:
    return s.lower().replace("’", "'").replace("ʼ", "'").replace("ё", "е")


def _hits(text: str, keywords: list[str]) -> list[str]:
    t = _norm(text)
    words = WORD.findall(t)
    found = []
    for kw in keywords:
        k = _norm(kw)
        if " " in k.strip():
            ok = k.strip() in t
        elif k.startswith("="):
            ok = k[1:] in words
        else:
            ok = any(w.startswith(k) for w in words)
        if ok:
            found.append(kw)
    return found


def classify(trend: Trend, cfg: dict) -> Trend:
    news_text = " ".join(n.title for n in trend.news)
    skip = _hits(trend.query + " " + news_text, cfg.get("skip", []))
    if skip:
        trend.skipped_reason = "негативна/заборонена тема: " + ", ".join(skip[:3])
        return trend
    best, best_score, best_hits = None, 0, []
    for key, ch in cfg["channels"].items():
        h_title = _hits(trend.query, ch["keywords"])
        h_news = _hits(news_text, ch["keywords"])
        score = 3 * len(h_title) + len(h_news)
        if score > best_score:
            best, best_score, best_hits = key, score, sorted(set(h_title + h_news))
    if best and best_score >= cfg.get("min_score", 1):
        trend.channel, trend.score, trend.matched = best, best_score, best_hits
    else:
        trend.skipped_reason = "не підходить жодному каналу"
    return trend


def rank_value(t: Trend) -> float:
    """Чим більше, тим вище в списку: обсяг пошуків + впевненість збігу + незалежні джерела."""
    return t.traffic * (1 + 0.15 * t.score) * (1 + 0.1 * min(t.extra_sources, 5))
