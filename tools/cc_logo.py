"""Логотип організації з Wikimedia Commons (лише вільна ліцензія або суспільне надбання).

  python tools/cc_logo.py "<назва англійською> logo" <папка_виходу>

Друкує JSON {path, credit, page} або null. SVG браузер малює напряму (<img src="...svg">), PNG теж.
Логотип ставимо на білу картку; якщо назва організації вже звучить і з'являється текстом, обріж лого до значка.
Внизу кадру підпис: «Логотип: Wikimedia Commons, <ліцензія>».
"""
import json
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.photos import API, OK_LIC, _get  # noqa: E402

query, out = sys.argv[1], Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
q = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 10,
                            "gsrsearch": query, "prop": "imageinfo", "iiprop": "url|extmetadata|mime"})
pages = sorted(json.loads(_get(f"{API}?{q}")).get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
res = None
for p in pages:
    info = (p.get("imageinfo") or [{}])[0]
    lic = (info.get("extmetadata", {}).get("LicenseShortName", {}) or {}).get("value", "")
    if "logo" not in p["title"].lower() or not OK_LIC.match(lic) or info.get("mime") not in ("image/svg+xml", "image/png"):
        continue
    name = Path(urllib.parse.unquote(info["url"].split("?")[0])).name
    (out / name).write_bytes(_get(info["url"]))
    res = {"path": str(out / name), "credit": f"Логотип: Wikimedia Commons, {lic}", "page": info.get("descriptionurl", "")}
    break
print(json.dumps(res, ensure_ascii=False))
