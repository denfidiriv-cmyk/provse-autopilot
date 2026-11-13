"""Клієнт Claude API (Anthropic Messages API, лише стандартна бібліотека) для сценаріїв.

Змінні середовища:
  ANTHROPIC_API_KEY   ключ з console.anthropic.com
  CLAUDE_MODEL        за замовчуванням claude-sonnet-5-5 (дешевше: claude-haiku-5-5)
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request

API = "https://api.anthropic.com/v1/messages"
SYSTEM = "Ти досвідчений сценарист українських YouTube Shorts. Відповідай ЛИШЕ одним JSON-об'єктом, без пояснень і без ```."


def generate_json(prompt: str, temperature: float = 0.7, max_tokens: int = 8000) -> dict:
    key = os.environ["ANTHROPIC_API_KEY"]
    body = {"model": os.environ.get("CLAUDE_MODEL") or "claude-sonnet-5-5", "max_tokens": max_tokens,
            "system": SYSTEM, "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST",
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                res = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 529) and i < 3:
                time.sleep(20 * (i + 1)); continue
            raise RuntimeError(f"Claude {e.code}: {e.read()[:400]!r}") from e
    text = "".join(b.get("text", "") for b in res.get("content", []) if b.get("type") == "text")
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"Claude не повернув JSON (stop_reason={res.get('stop_reason')}, блоки={[b.get('type') for b in res.get('content', [])]}): {text[:300]!r}")
    return json.loads(m.group(0))
