"""Google Trends (Україна) без API-ключів і без LLM.

Джерело: офіційний RSS «Популярне зараз» https://trends.google.com/trending/rss?geo=UA
Для кожного тренду RSS уже містить 1-3 новини (заголовок, URL, видання).
Додатково можна підтягнути Google News RSS, щоб порахувати незалежні джерела (правило «2+ джерела»).
Тільки стандартна бібліотека Python.
"""
from __future__ import annotations

import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime

TRENDS_RSS = "https://trends.google.com/trending/rss?geo={geo}"
NEWS_RSS = "https://news.google.com/rss/search?q={q}&hl=uk&gl=UA&ceid=UA:uk"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
HT = "{https://trends.google.com/trending/rss}"


@dataclass
class News:
    title: str
    url: str
    source: str = ""


@dataclass
class Trend:
    query: str
    traffic: int = 0          # приблизна кількість пошуків, «5 тис.+» -> 5000
    traffic_label: str = ""
    published: str = ""       # ISO-час появи тренду
    news: list[News] = field(default_factory=list)
    channel: str | None = None
    score: int = 0
    matched: list[str] = field(default_factory=list)
    skipped_reason: str = ""
    extra_sources: int = 0    # скільки різних видань знайшов Google News


def _get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "uk,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_traffic(label: str) -> int:
    s = (label or "").replace(" ", " ").replace(",", "").replace("+", "").strip().lower()
    m = re.match(r"([\d.]+)\s*([kmкм]|тис|млн)?", s)
    if not m:
        return 0
    n = float(m.group(1))
    mult = {"k": 1e3, "к": 1e3, "тис": 1e3, "m": 1e6, "м": 1e6, "млн": 1e6}.get(m.group(2) or "", 1)
    return int(n * mult)


def parse_trends_rss(xml_bytes: bytes) -> list[Trend]:
    root = ET.fromstring(xml_bytes)
    out: list[Trend] = []
    for item in root.iter("item"):
        q = (item.findtext("title") or "").strip()
        if not q:
            continue
        label = (item.findtext(f"{HT}approx_traffic") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        try:
            pub = parsedate_to_datetime(pub).isoformat() if pub else ""
        except (TypeError, ValueError):
            pass
        news = []
        for n in item.findall(f"{HT}news_item"):
            t = (n.findtext(f"{HT}news_item_title") or "").strip()
            u = (n.findtext(f"{HT}news_item_url") or "").strip()
            s = (n.findtext(f"{HT}news_item_source") or "").strip()
            if t or u:
                news.append(News(t, u, s))
        out.append(Trend(q, parse_traffic(label), label, pub, news))
    return out


def fetch_trends(geo: str = "UA") -> list[Trend]:
    return parse_trends_rss(_get(TRENDS_RSS.format(geo=geo)))


def parse_news_rss(xml_bytes: bytes, limit: int = 10) -> list[News]:
    root = ET.fromstring(xml_bytes)
    out = []
    for item in list(root.iter("item"))[:limit]:
        src = item.find("source")
        out.append(News((item.findtext("title") or "").strip(), (item.findtext("link") or "").strip(),
                        (src.text or "").strip() if src is not None else ""))
    return out


def fetch_news(query: str, limit: int = 10) -> list[News]:
    return parse_news_rss(_get(NEWS_RSS.format(q=urllib.parse.quote(query))), limit)
