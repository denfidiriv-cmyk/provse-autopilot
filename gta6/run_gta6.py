"""GTA 6 Kiosk autopilot (English channel, same engine as the «Все про …» channels).

trend scan (YouTube Shorts by views/hour, news, r/GTA6, X/TikTok notes) -> planner picks topic + winning format + verified
facts -> Claude Code with skills makes the video (Gemini voice, official Rockstar screenshots, word-synced text,
quiet music, no SFX) -> public upload to the GTA 6 Kiosk YouTube channel -> files for TikTok/X cross-posting.

  python gta6/run_gta6.py            # production
  python gta6/run_gta6.py --test     # private upload, state not written
  python gta6/run_gta6.py --no-upload
Env: ANTHROPIC_API_KEY, GEMINI_API_KEY, YT_CLIENT_ID, YT_CLIENT_SECRET, YT_TOKEN_GTA6KIOSK
     (optional YT_CLIENT_ID_GTA6KIOSK / YT_CLIENT_SECRET_GTA6KIOSK for a separate API quota),
     GTA6_DAILY_MAX (3), GTA6_PRIVACY (public), GTA6_VOICE (Puck), CC_MODEL, CC_BUDGET_USD.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gta6 import plan as planner  # noqa: E402
from gta6 import scan as scanner  # noqa: E402

STATE, JOB, MEDIA = ROOT / "state", ROOT / "job", ROOT / "gta6_media"
CH = "gta6kiosk"
VOICE_STYLE = ("Read the text below in English only, exactly as written, adding nothing. "
               "Voice of an energetic, upbeat gaming news host: fast pace, bright, very clear diction. Text:")


def published() -> list:
    p = STATE / "gta6_published.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def record(entry: dict) -> None:
    (STATE / "gta6_published.json").write_text(json.dumps((published() + [entry])[-300:], ensure_ascii=False, indent=1), encoding="utf-8")


def slot_name() -> str:
    h = datetime.now().hour
    return "morning: news recap or HOW TO" if h < 13 else "afternoon: HOW TO, spotlight or hidden detail" if h < 18 else "evening: question/debate or day recap"


def probe(mp4: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                          "-of", "json", str(mp4)], capture_output=True, text=True).stdout
    j = json.loads(out or "{}")
    v = [s for s in j.get("streams", []) if s.get("codec_type") == "video"]
    return {"dur": float(j.get("format", {}).get("duration", 0)), "w": v[0]["width"] if v else 0,
            "h": v[0]["height"] if v else 0, "audio": any(s.get("codec_type") == "audio" for s in j.get("streams", []))}


def small_copy(src: Path, dst: Path, limit_mb: float = 3.4) -> None:
    """Claude in Chrome uploads at most ~3.8 MB per file, so TikTok/X get an HEVC copy under 3.4 MB."""
    if src.stat().st_size <= limit_mb * 1e6:
        shutil.copy(src, dst); return
    dur = probe(src)["dur"] or 20
    vb = max(300, min(2500, int((limit_mb * 8e6 / dur - 96000) / 1000)))
    base = ["ffmpeg", "-v", "error", "-y", "-i", str(src), "-c:v", "libx265", "-preset", "medium", "-b:v", f"{vb}k"]
    subprocess.run(base + ["-x265-params", "pass=1:log-level=error", "-an", "-f", "null", "/dev/null"], check=True, cwd="/tmp")
    subprocess.run(base + ["-x265-params", "pass=2:log-level=error", "-tag:v", "hvc1", "-c:a", "aac", "-b:a", "96k",
                           "-movflags", "+faststart", str(dst)], check=True, cwd="/tmp")


def notify(text: str) -> None:
    try:
        from pipeline import notify as tg
        tg.send(text)
    except Exception as e:
        print("telegram:", e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--no-upload", action="store_true")
    a = ap.parse_args()
    STATE.mkdir(exist_ok=True)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("no ANTHROPIC_API_KEY"); return 0
    cut = (datetime.now() - timedelta(days=1)).isoformat()
    today = [p for p in published() if p.get("at", "") >= cut and p.get("url", "").startswith("http")]
    if not a.test and len(today) >= int(os.environ.get("GTA6_DAILY_MAX") or 3):
        print("daily limit reached"); return 0

    shutil.rmtree(JOB, ignore_errors=True); JOB.mkdir()
    token = None
    try:
        from pipeline.youtube import access_token
        token = access_token(CH)
    except Exception as e:
        print("youtube token:", e)
    board = scanner.scan(token, STATE, JOB / "trend_thumbs")
    (JOB / "trend_board.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print("trend board:", {k: len(v) if isinstance(v, (list, dict)) else v for k, v in board.items()})

    recent = [p.get("title", "") for p in published()[-30:]]
    plan = planner.pick(board, recent, slot_name())
    print("plan:", json.dumps({k: plan.get(k) for k in ("topic", "pillar", "hook", "skip")}, ensure_ascii=False))
    if plan.get("skip"):
        print("skip:", plan["skip"]); return 0

    brief = {"channel": CH, "channel_name": "GTA 6 Kiosk", "language": "en", "voice": os.environ.get("GTA6_VOICE") or "Puck",
             "plan": plan, "trend_board": board, "recent": recent,
             "baseline_facts": (ROOT / "gta6" / "facts.md").read_text(encoding="utf-8")}
    (JOB / "brief.json").write_text(json.dumps(brief, ensure_ascii=False, indent=1), encoding="utf-8")

    # Claude Code sees only model and voice keys (no YouTube/Telegram/GitHub tokens) and has no web tools.
    safe_env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "TZ", "HF_BROWSER", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
                                           "GEMINI_TTS_MODEL", "MUSIC_DIR", "CHROME_PATH", "PUPPETEER_EXECUTABLE_PATH",
                                           "HYPERFRAMES_BROWSER_PATH", "PLAYWRIGHT_BROWSERS_PATH", "npm_config_cache") if os.environ.get(k)}
    safe_env["VOICE_STYLE"] = VOICE_STYLE
    allowed = ["Read", "Write", "Edit", "Glob", "Grep", "Skill", "Bash(python:*)", "Bash(python3:*)", "Bash(ffmpeg:*)",
               "Bash(ffprobe:*)", "Bash(npx:*)", "Bash(node:*)", "Bash(npm:*)", "Bash(ls:*)", "Bash(mkdir:*)", "Bash(cp:*)"]
    cmd = ["claude", "-p", (ROOT / "prompts" / "gta6_video.md").read_text(encoding="utf-8"),
           "--model", os.environ.get("CC_MODEL") or "claude-sonnet-5-5", "--max-budget-usd", os.environ.get("CC_BUDGET_USD") or "3",
           "--allowedTools", *allowed, "--disallowedTools", "WebFetch", "WebSearch", "--output-format", "json"]
    t0 = time.time()
    res = subprocess.run(cmd, cwd=ROOT, env=safe_env, capture_output=True, text=True, timeout=55 * 60)
    try:
        info = json.loads(res.stdout.strip().splitlines()[-1])
    except Exception:
        info = {}
    cost = info.get("total_cost_usd", 0)
    print(f"Claude Code: {time.time() - t0:.0f} s, ${cost:.2f}, turns {info.get('num_turns')}")
    print((info.get("result") or res.stdout[-2000:] or res.stderr[-2000:])[:3000])

    meta_p, mp4 = JOB / "meta.json", JOB / "final.mp4"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
    if meta.get("skip"):
        print("Claude skipped:", meta["skip"]); return 0
    p = probe(mp4) if mp4.exists() else {}
    if not p or not (10 <= p["dur"] <= 45 and p["w"] == 1080 and p["h"] == 1920 and p["audio"]) or not meta.get("title"):
        notify(f"⚠️ GTA 6 Kiosk: відео не вдалося ({plan.get('topic')}, ${cost:.2f}). {p}")
        return 1

    stamp = f"{datetime.now():%Y%m%d_%H%M}"
    out = ROOT / "out" / f"gta6_{stamp}.mp4"; out.parent.mkdir(exist_ok=True)
    shutil.copy(mp4, out)
    tags = [h.lstrip("#").replace(" ", "") for h in meta.get("hashtags", [])] or ["GTA6", "GTAVI"]
    desc = (meta.get("description", "") + "\n\nSources:\n" + "\n".join(f"{s['name']}: {s['url']}" for s in meta.get("sources", []))
            + "\n\nScreenshots via @RockstarGames. Fan page. Not affiliated with Rockstar Games or Take-Two Interactive.\n\n"
            + " ".join("#" + h for h in tags))
    url = ""
    if not a.no_upload:
        from pipeline.youtube import upload
        privacy = "private" if a.test else (os.environ.get("GTA6_PRIVACY") or "public")
        url = upload(CH, out, meta["title"], desc, tags, privacy, lang="en")
    entry = {"at": datetime.now().isoformat(), "topic": plan.get("topic"), "pillar": plan.get("pillar"), "title": meta["title"],
             "url": url, "file": f"gta6_{stamp}.mp4", "format_ref": meta.get("format_ref") or (plan.get("format_ref") or {}).get("url"),
             "style": meta.get("style"), "tiktok_caption": meta.get("tiktok_caption", ""), "x_post": meta.get("x_post", ""), "cost": cost}
    if not a.test:
        record(entry)
    # Files for the Chrome task (TikTok/X cross-posting): the workflow pushes this folder to the gta6-media branch.
    MEDIA.mkdir(exist_ok=True)
    small_copy(out, MEDIA / entry["file"])
    (MEDIA / f"gta6_{stamp}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy(JOB / "format.md", MEDIA / f"gta6_{stamp}_format.md") if (JOB / "format.md").exists() else None
    notify(f"🎮 GTA 6 Kiosk: {meta['title']}\n{url or '(без завантаження)'}\nФормат з: {entry['format_ref']}\n${cost:.2f}")
    print("DONE", url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
