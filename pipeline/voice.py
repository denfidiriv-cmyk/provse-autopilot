"""Озвучка (Gemini TTS) і таймінги слів без ASR: тиша → сегменти мовлення → DP за складами.
Той самий алгоритм, що tools/align_28.py, яким ми вирівнювали всі ручні ролики.
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np

from . import gemini

STYLE = "Read this as an energetic, confident Ukrainian news anchor. Fast pace, bright, punchy, very clear diction:"
VOWELS = set("аеєиіїоуюяАЕЄИІЇОУЮЯ")
SR = 24000


def synth(text: str, voice: str, out_wav: Path) -> Path:
    pcm = gemini.tts_pcm(text, voice, STYLE)
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)
    return out_wav


def _read(path: Path) -> np.ndarray:
    with wave.open(str(path)) as w:
        assert w.getsampwidth() == 2
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16)
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(1).astype(np.int16)
        if w.getframerate() != SR:
            raise ValueError("очікую 24 кГц")
    return x


def tighten_and_align(raw: Path, words: list[str], out_wav: Path, tempo: float = 1.06) -> list[list]:
    """Обрізає довгі паузи, прискорює на tempo і повертає [[слово, час_початку_с], ...] для out_wav."""
    x = _read(raw); xf = x.astype(float) / 32768
    h = int(SR * 0.01); n = len(x) // h
    db = 20 * np.log10(np.array([np.sqrt(np.mean(xf[i * h:(i + 1) * h] ** 2)) for i in range(n)]) + 1e-9)
    on = db > -30; segs = []; i = 0
    while i < n:
        if on[i]:
            j = i
            while j < n and (on[j] or on[j:j + 12].any()):
                j += 1
            if (j - i) * 0.01 > 0.08:
                segs.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    MAXG, pad = 0.28, 0.03
    parts = [np.zeros(int(0.05 * SR), dtype=x.dtype)]; t = 0.05; prev = None; ns = []
    for a, b in segs:
        a0 = max(0, a - pad); b0 = min(len(x) / SR, b + pad)
        if prev is not None:
            g = min(max(0, a0 - prev), MAXG); parts.append(x[int(prev * SR):int((prev + g) * SR)]); t += g
        parts.append(x[int(a0 * SR):int(b0 * SR)]); ns.append((t + (a - a0), t + (a - a0) + (b - a))); t += b0 - a0; prev = b0
    y = np.concatenate(parts)
    tmp = out_wav.with_suffix(".tight.wav")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())
    segs = ns
    ws = np.array([max(1, sum(c in VOWELS for c in wd)) for wd in words], float)
    D = np.array([b - a for a, b in segs]); rate = D.sum() / ws.sum()
    W, S = len(words), len(segs); cs = np.concatenate([[0], np.cumsum(ws)])
    INF = 1e18; dp = np.full((S + 1, W + 1), INF); bk = np.zeros((S + 1, W + 1), int); dp[0][0] = 0
    for j in range(1, S + 1):
        for k in range(0, W + 1):
            best, arg = INF, -1
            if dp[j - 1][k] < INF:
                best, arg = dp[j - 1][k] + (D[j - 1] ** 2) * 3, k
            for i in range(max(0, k - 14), k):
                if dp[j - 1][i] >= INF:
                    continue
                c = dp[j - 1][i] + (D[j - 1] - rate * (cs[k] - cs[i])) ** 2
                if c < best:
                    best, arg = c, i
            dp[j][k], bk[j][k] = best, arg
    k = W; assign = []
    for j in range(S, 0, -1):
        i = bk[j][k]; assign.append((j - 1, i, k)); k = i
    res: list = [None] * W
    for j, i, k in reversed(assign):
        if k <= i:
            continue
        a, b = segs[j]; tot = cs[k] - cs[i]
        for q in range(i, k):
            res[q] = [words[q], a + (cs[q] - cs[i]) / tot * (b - a)]
    for q in range(W):  # заповнюємо пропуски лінійно
        if res[q] is None:
            res[q] = [words[q], res[q - 1][1] + 0.3 if q else 0.05]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-af", f"atempo={tempo}", str(out_wav)], check=True)
    tmp.unlink(missing_ok=True)
    return [[w, round(t / tempo, 3)] for w, t in res]
