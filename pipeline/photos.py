"""Фото з вільними ліцензіями з Wikimedia Commons (місця, предмети, тварини; без людей)."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from .trends import UA

API = "https://commons.wikimedia.org/w/api.php"
OK_LIC = re.compile(r"^(cc0|public domain|pd|cc by(-sa)? [1-4]\.\d|cc by(-sa)? 4\.0)", re.I)
PEOPLE = re.compile(r"(people|person|portrait|men |women|man |woman|politician|actor|actress|singer|player|athlete|"
                    r"selfie|crowd|child|children|girl|boy|president|minister|footballer|boxer|face)", re.I)


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA + " provse-autopilot (contact via GitHub)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def find_photo(query: str, out: Path, width: int = 1400) -> dict | None:
    """Шукає фото, перевіряє ліцензію і відсутність людей у назві/категоріях, зберігає JPEG.
    Повертає {path, credit} або None."""
    q = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
                                "gsrlimit": 15, "gsrsearch": f"{query} filetype:bitmap", "prop": "imageinfo|categories",
                                "iiprop": "url|size|extmetadata|mime", "iiurlwidth": width, "cllimit": 50})
    data = json.loads(_get(f"{API}?{q}"))
    pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    for p in pages:
        info = (p.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "")
        cats = " ".join(c["title"] for c in p.get("categories", []))
        if not OK_LIC.match(lic) or PEOPLE.search(p["title"] + " " + cats):
            continue
        if info.get("mime") not in ("image/jpeg", "image/png") or info.get("width", 0) < 900:
            continue
        artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip()[:40] or "Wikimedia Commons"
        out.write_bytes(_get(info["thumburl"]))
        return {"path": str(out), "credit": f"Фото: {artist}, {lic}", "page": info.get("descriptionurl", "")}
    return None
