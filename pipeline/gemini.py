"""Мінімальний клієнт Gemini API (REST, лише стандартна бібліотека).

Моделі задаються змінними середовища, щоб їх можна було міняти без коду:
  GEMINI_TEXT_MODEL  (за замовчуванням gemini-2.5-flash)
  GEMINI_TTS_MODEL   (за замовчуванням gemini-3.8-flash-tts, як в AI Studio)
"""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _post(model: str, body: dict, retries: int = 4) -> dict:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY не задано")
    req = urllib.request.Request(API.format(model=model), data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and i < retries - 1:
                time.sleep(15 * (i + 1))
                continue
            raise RuntimeError(f"Gemini {e.code}: {e.read()[:400]!r}") from e
    raise RuntimeError("Gemini: вичерпано спроби")


def generate_json(prompt: str, temperature: float = 0.7) -> dict:
    model = os.environ.get("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
    res = _post(model, {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"}})
    text = "".join(p.get("text", "") for p in res["candidates"][0]["content"]["parts"])
    return json.loads(text)


def list_models() -> list[str]:
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000",
                                 headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return [m["name"].split("/", 1)[1] for m in data.get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]


def _tts_model() -> str:
    if os.environ.get("GEMINI_TTS_MODEL"):
        return os.environ["GEMINI_TTS_MODEL"]
    tts = [m for m in list_models() if "tts" in m]
    print("доступні TTS-моделі:", tts)
    flash = [m for m in tts if "flash" in m] or tts
    if not flash:
        raise RuntimeError("для цього ключа немає жодної TTS-моделі Gemini")
    return sorted(flash)[-1]


def tts_pcm(text: str, voice: str, style: str) -> bytes:
    """Повертає сирий PCM 16-bit mono 24 кГц."""
    model = _tts_model()
    body = {"contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    try:
        res = _post(model, {**({"systemInstruction": {"parts": [{"text": style}]}} if style else {}), **body})
    except RuntimeError as e:
        if not style or "instruction" not in str(e).lower():
            raise
        print("модель TTS не приймає системну інструкцію, озвучую без стилю")  # стиль у тексті модель зачитує вголос
        res = _post(model, body)
    for p in res["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            return base64.b64decode(p["inlineData"]["data"])
    raise RuntimeError("Gemini TTS не повернув аудіо")
