"""Official GTA VI screenshots from rockstargames.com (credit: "via @RockstarGames" in the description).

  python gta6/media.py --list                      # categories and counts
  python gta6/media.py <keywords> <out_dir> [n]    # e.g. "vice_city" work/hf/assets/img 4
                                                   #      "cheetah" ... / "lucia" ... / "jason_and_lucia" ...

Keywords match the file names (case-insensitive, several words = all must match).
Files are saved as <out_dir>/<Name>_<NN>.jpg, already cropped to 1080x1920 (center) for full-screen use;
the original 16:9 is kept as *_wide.jpg for drift/pan shots.
"""
from __future__ import annotations

import random
import sys
import urllib.request
from pathlib import Path

BASE = "https://www.rockstargames.com/VI/_next/static/media/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
NAMES = sorted({n for n in (Path(__file__).with_name("official_media.txt").read_text().replace("\n", "|").split("|")) if n})


def categories() -> dict[str, int]:
    out: dict[str, int] = {}
    for n in NAMES:
        key = n.split(".")[0].rsplit("_", 1)[0]
        out[key] = out.get(key, 0) + 1
    return out


def find(keywords: str) -> list[str]:
    ks = [k.lower() for k in keywords.replace(",", " ").split() if k]
    return [n for n in NAMES if all(k in n.lower() for k in ks)]


def fetch(name: str, out_dir: Path) -> Path:
    from PIL import Image
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = name.split(".")[0]
    wide = out_dir / f"{stem}_wide.jpg"
    if not wide.exists():
        req = urllib.request.Request(BASE + name, headers={"User-Agent": UA, "Referer": "https://www.rockstargames.com/VI"})
        with urllib.request.urlopen(req, timeout=60) as r:
            wide.write_bytes(r.read())
    im = Image.open(wide).convert("RGB")
    w, h = im.size
    tw = int(h * 9 / 16)
    x0 = max(0, (w - tw) // 2)
    tall = im.crop((x0, 0, x0 + tw, h)).resize((1080, 1920), Image.LANCZOS)
    p = out_dir / f"{stem}.jpg"
    tall.save(p, quality=92)
    return p


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] == "--list":
        for k, v in categories().items():
            print(f"{k}: {v}")
        return
    kw, out = sys.argv[1], Path(sys.argv[2])
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    hits = find(kw)
    if not hits:
        sys.exit(f"no official screenshots match '{kw}'. Run --list for categories.")
    random.shuffle(hits)
    for name in hits[:n]:
        try:
            print(fetch(name, out))
        except Exception as e:  # one broken file must not stop the video
            print("skip", name, e)


if __name__ == "__main__":
    main()
