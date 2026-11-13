"""Збір фактів під тренд: тексти статей із посилань, які дає сам Google Trends. Без LLM."""
from __future__ import annotations

import html
import re
import urllib.request

from .trends import UA, Trend, fetch_news

P = re.compile(r"<p[^>]*>(.*?)</p>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")


def article_text(url: str, limit: int = 2500) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "uk,ru;q=0.8,en;q=0.5"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read(1_500_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
    paras = [html.unescape(TAG.sub("", m)).strip() for m in P.findall(raw)]
    paras = [p for p in paras if len(p) > 60]
    return "\n".join(paras)[:limit]


def bing_news(query: str, n: int = 10) -> list[dict]:
    """Новини з Bing News RSS (Україна): [{source, title, url}] з прямими посиланнями."""
    import urllib.parse
    import xml.etree.ElementTree as ET
    q = urllib.parse.urlencode({"q": query, "format": "rss", "setlang": "uk", "cc": "UA", "mkt": "uk-UA"})
    req = urllib.request.Request(f"https://www.bing.com/news/search?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        root = ET.fromstring(r.read())
    res = []
    for it in root.iter("item"):
        link = it.findtext("link") or ""
        m = re.search(r"[?&]url=([^&]+)", link)
        url = urllib.parse.unquote(m.group(1)) if m else link
        src = urllib.parse.urlparse(url).netloc.replace("www.", "")
        if url.startswith("http") and src:
            res.append({"source": src, "title": html.unescape(it.findtext("title") or ""), "url": url})
        if len(res) >= n:
            break
    return res


def gather(trend: Trend, max_articles: int = 4) -> list[dict]:
    """[{source, title, url, text}] з різних видань."""
    out, seen = [], set()
    for n in trend.news:
        if n.source in seen or not n.url:
            continue
        try:
            txt = article_text(n.url)
        except Exception:
            txt = ""
        if len(txt) > 200:
            out.append({"source": n.source, "title": n.title, "url": n.url, "text": txt})
            seen.add(n.source)
        if len(out) >= max_articles:
            break
    if len(out) < 3:  # Bing News дає прямі посилання на статті (у Google News вони за редиректом)
        try:
            for n in bing_news(trend.query):
                if n["source"] in seen:
                    continue
                try:
                    txt = article_text(n["url"])
                except Exception:
                    txt = ""
                if len(txt) > 200:
                    out.append({**n, "text": txt}); seen.add(n["source"])
                if len(out) >= max_articles:
                    break
        except Exception:
            pass
    if len(out) < 2:  # добираємо заголовки з Google News, хоча б як підтвердження
        try:
            for n in fetch_news(trend.query, 10):
                if n.source and n.source not in seen:
                    out.append({"source": n.source, "title": n.title, "url": n.url, "text": ""})
                    seen.add(n.source)
                if len(out) >= max_articles:
                    break
        except Exception:
            pass
    return out
