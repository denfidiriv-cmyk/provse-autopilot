"""Telegram: повідомлення власнику і команди керування (/stop, /go, /status) без окремого сервера.
Кожен запуск агента читає нові повідомлення бота через getUpdates і оновлює state/control.json.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


def _api(method: str, **params):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not tok:
        return None
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/{method}", data=data, timeout=30) as r:
        return json.loads(r.read())


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def send(text: str) -> None:
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if chat:
        for i in range(0, len(text), 3800):
            _api("sendMessage", chat_id=chat, text=text[i:i + 3800], parse_mode="HTML", disable_web_page_preview="true")


def run_actions(ctl: dict) -> None:
    """Виконує натиснуті кнопки: pub:<канал>:<id> або del:<канал>:<id>."""
    from . import youtube
    for a in ctl.get("actions", []):
        try:
            kind, ch, vid = a.split(":", 2)
            if kind == "pub":
                youtube.set_public(ch, vid); send(f"✅ Опубліковано: https://youtube.com/shorts/{vid}")
            elif kind == "del":
                youtube.delete(ch, vid); send("🗑 Видалено.")
        except Exception as e:
            send(f"⚠️ Не вийшло виконати «{a}»: {str(e)[:200]}. Якщо YouTube ще не пройшов аудит API, відкрий відео в Studio і опублікуй вручну.")
    ctl["actions"] = []


def control(state: Path) -> dict:
    """Повертає {"paused": bool, "offset": int}. Команди приймаються лише від TELEGRAM_CHAT_ID."""
    p = state / "control.json"
    ctl = json.loads(p.read_text()) if p.exists() else {"paused": False, "offset": 0}
    chat = str(os.environ.get("TELEGRAM_CHAT_ID", ""))
    try:
        res = _api("getUpdates", offset=ctl["offset"] + 1, timeout=0) or {}
    except Exception:
        res = {}
    ctl.setdefault("actions", [])
    for u in res.get("result", []):
        ctl["offset"] = max(ctl["offset"], u["update_id"])
        cb = u.get("callback_query")
        if cb and str(cb.get("message", {}).get("chat", {}).get("id")) == chat:
            ctl["actions"].append(cb.get("data", ""))
            try:
                _api("answerCallbackQuery", callback_query_id=cb["id"], text="Прийнято, виконаю протягом 30 хвилин")
            except Exception:
                pass
            continue
        msg = u.get("message") or {}
        if str(msg.get("chat", {}).get("id")) != chat:
            continue
        cmd = (msg.get("text") or "").strip().lower()
        if cmd in ("/stop", "стоп"):
            ctl["paused"] = True; send("⏸ Автопостинг зупинено. Тренди далі збираю. /go щоб увімкнути.")
        elif cmd in ("/go", "/start", "старт"):
            ctl["paused"] = False; send("▶️ Автопостинг увімкнено.")
        elif cmd == "/status":
            send("Стан: " + ("пауза" if ctl["paused"] else "працюю"))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ctl))
    return ctl


def send_video(path: Path, caption: str, buttons: list | None = None) -> None:
    """Надсилає готовий ролик у Telegram (до 50 МБ)."""
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat or not Path(path).exists():
        return
    import uuid
    b = uuid.uuid4().hex
    parts = []
    fields = [("chat_id", chat), ("caption", caption[:1000]), ("parse_mode", "HTML"), ("supports_streaming", "true")]
    if buttons:
        fields.append(("reply_markup", json.dumps({"inline_keyboard": [buttons]})))
    for k, v in fields:
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="video"; filename="{Path(path).name}"\r\nContent-Type: video/mp4\r\n\r\n'.encode()
                 + Path(path).read_bytes() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendVideo", data=b"".join(parts),
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    urllib.request.urlopen(req, timeout=120).read()
