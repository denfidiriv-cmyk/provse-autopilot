"""Trend scan for GTA 6 Kiosk: what is winning right now, so every video copies a proven FORMAT (never the content).

Sources (each one optional, failures are logged and skipped):
  - YouTube Data API: GTA 6 Shorts from the last 48 h ranked by views per hour (+ their thumbnails for visual analysis)
  - Google News RSS (English): fresh GTA 6 headlines
  - Reddit r/GTA6 top of the day: what players ask and argue about
  - state/gta6_social.json: notes about X and TikTok written by the Chrome task (if fresh)
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def _get(url: str, headers: dict | None = None, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _iso_dur(s: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return 0
    h, mi, se = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + se


def youtube_board(token: str, hours: int = 48, top: int = 12, thumbs_dir: Path | None = None) -> list[dict]:
    after = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    auth = {"Authorization": f"Bearer {token}"}
    ids: list[str] = []
    for q in ("GTA 6", "GTA VI gameplay", "GTA 6 tips"):
        p = urllib.parse.urlencode({"part": "id", "q": q, "type": "video", "videoDuration": "short", "order": "viewCount",
                                    "publishedAfter": after, "maxResults": 25, "relevanceLanguage": "en"})
        data = json.loads(_get("https://www.googleapis.com/youtube/v3/search?" + p, auth))
        ids += [it["id"]["videoId"] for it in data.get("items", []) if it.get("id", {}).get("videoId")]
    ids = list(dict.fromkeys(ids))[:50]
    if not ids:
        return []
    p = urllib.parse.urlencode({"part": "snippet,statistics,contentDetails", "id": ",".join(ids)})
    data = json.loads(_get("https://www.googleapis.com/youtube/v3/videos?" + p, auth))
    now = datetime.now(timezone.utc)
    rows = []
    for v in data.get("items", []):
        sn, st = v["snippet"], v.get("statistics", {})
        pub = datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
        age_h = max(1.0, (now - pub).total_seconds() / 3600)
        views = int(st.get("viewCount", 0))
        th = sn.get("thumbnails", {})
        rows.append({"id": v["id"], "url": f"https://youtube.com/shorts/{v['id']}", "title": sn["title"],
                     "channel": sn["channelTitle"], "views": views, "views_per_hour": round(views / age_h),
                     "likes": int(st.get("likeCount", 0)), "comments": int(st.get("commentCount", 0)),
                     "age_h": round(age_h, 1), "duration_s": _iso_dur(v["contentDetails"].get("duration", "")),
                     "tags": sn.get("tags", [])[:10], "description": sn.get("description", "")[:300],
                     "thumb": (th.get("maxres") or th.get("high") or th.get("medium") or {}).get("url", "")})
    rows = [r for r in rows if 0 < r["duration_s"] <= 75]
    rows.sort(key=lambda r: r["views_per_hour"], reverse=True)
    rows = rows[:top]
    if thumbs_dir:
        thumbs_dir.mkdir(parents=True, exist_ok=True)
        for i, r in enumerate(rows):
            if r["thumb"]:
                try:
                    (thumbs_dir / f"{i + 1:02d}_{r['id']}.jpg").write_bytes(_get(r["thumb"]))
                except Exception as e:
                    print("thumb", r["id"], e)
    return rows


def news(n: int = 15) -> list[dict]:
    q = urllib.parse.urlencode({"q": "GTA 6 when:2d", "hl": "en-US", "gl": "US", "ceid": "US:en"})
    root = ET.fromstring(_get("https://news.google.com/rss/search?" + q))
    out = []
    for it in root.iter("item"):
        src = it.find("source")
        out.append({"title": it.findtext("title", ""), "source": src.text if src is not None else "",
                    "url": it.findtext("link", ""), "published": it.findtext("pubDate", "")})
        if len(out) >= n:
            break
    return out


def bing_news(n: int = 12) -> list[dict]:
    """Direct article links (Google News links are redirects), used to fetch article text."""
    q = urllib.parse.urlencode({"q": "GTA 6", "format": "rss", "setlang": "en", "cc": "US", "mkt": "en-US", "qft": 'interval="7"'})
    root = ET.fromstring(_get("https://www.bing.com/news/search?" + q))
    out = []
    for it in root.iter("item"):
        link = it.findtext("link", "")
        m = re.search(r"[?&]url=([^&]+)", link)
        url = urllib.parse.unquote(m.group(1)) if m else link
        out.append({"title": it.findtext("title", ""), "source": urllib.parse.urlparse(url).netloc.replace("www.", ""), "url": url})
        if len(out) >= n:
            break
    return out


def reddit(n: int = 15) -> list[dict]:
    data = json.loads(_get("https://www.reddit.com/r/GTA6/top.json?t=day&limit=25", {"Accept": "application/json"}))
    out = []
    for c in data.get("data", {}).get("children", []):
        d = c.get("data", {})
        out.append({"title": d.get("title", ""), "score": d.get("score", 0), "comments": d.get("num_comments", 0),
                    "flair": d.get("link_flair_text") or "", "url": "https://reddit.com" + d.get("permalink", "")})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out[:n]


def social(state: Path, max_age_h: int = 36) -> dict:
    p = state / "gta6_social.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text(encoding="utf-8"))
    try:
        at = datetime.fromisoformat(d.get("at", "1970-01-01T00:00:00+00:00"))
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - at > timedelta(hours=max_age_h):
            return {}
    except Exception:
        return {}
    return d


def scan(token: str | None, state: Path, thumbs_dir: Path) -> dict:
    board: dict = {"at": datetime.now(timezone.utc).isoformat()}
    for key, fn in (("youtube", lambda: youtube_board(token, thumbs_dir=thumbs_dir) if token else []),
                    ("news", news), ("articles", bing_news), ("reddit", reddit), ("social", lambda: social(state))):
        try:
            board[key] = fn()
        except Exception as e:
            print(f"scan {key}: {e}")
            board[key] = [] if key != "social" else {}
    return board
