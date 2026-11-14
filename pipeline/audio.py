"""Музика й звукові ефекти кодом (без чужих треків, тож жодних проблем з авторськими правами) + мікс з голосом."""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SR = 48000
rng = np.random.default_rng(7)

MOODS = {  # акорди (MIDI), темп, характер
    "bright": dict(bpm=112, chords=[[60, 64, 67, 72], [57, 60, 64, 69], [65, 69, 72, 77], [67, 71, 74, 79]]),
    "tense": dict(bpm=100, chords=[[57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67], [52, 55, 59, 64]]),
    "drive": dict(bpm=124, chords=[[62, 66, 69, 74], [59, 62, 66, 71], [55, 59, 62, 67], [57, 61, 64, 69]]),
}
CHANNEL_MOOD = {"svit": "bright", "dim": "bright", "yizha": "bright", "ekonomika": "tense", "polityka": "tense", "sport": "drive", "avto": "drive"}


def f(m): return 440 * 2 ** ((m - 69) / 12)
def t_(d): return np.arange(int(d * SR)) / SR
def env(n, a, d): x = np.ones(n); na = max(1, int(a * SR)); x[:na] = np.linspace(0, 1, na); return x * np.exp(-np.maximum(0, np.arange(n) / SR - a) / d)


def music(dur: float, mood: str) -> np.ndarray:
    m = MOODS[mood]; beat = 60 / m["bpm"]; bar = 4 * beat
    out = np.zeros(int((dur + 1) * SR))
    for b in range(int(dur / bar) + 1):
        ch = m["chords"][b % 4]; s = int(b * bar * SR); tt = t_(bar)
        pad = sum(np.sin(2 * np.pi * f(n) * tt) + .3 * np.sin(2 * np.pi * 2 * f(n) * tt) for n in ch) / len(ch)
        pad *= np.minimum(1, tt / .3) * np.minimum(1, (bar - tt) / .3) * .18
        bass = np.sin(2 * np.pi * f(ch[0] - 24) * tt) * .25
        seg = pad + bass
        for q in range(8):  # арпеджіо восьмими
            st = int(q * beat / 2 * SR); n = ch[q % 4] + 12; tq = t_(beat / 2)
            seg[st:st + len(tq)] += np.sin(2 * np.pi * f(n) * tq) * env(len(tq), .005, .12) * .12
        for q in range(4):  # бочка й хай-хет
            st = int(q * beat * SR); tk = t_(.25)
            seg[st:st + len(tk)] += np.sin(2 * np.pi * 55 * tk * np.exp(-tk * 12)) * env(len(tk), .001, .08) * .5
            hh = int((q + .5) * beat * SR); n = int(.03 * SR)
            seg[hh:hh + n] += rng.standard_normal(n) * env(n, .0005, .01) * .06
        out[s:s + len(seg)] += seg[:len(out) - s]
    return out[:int(dur * SR)]


def whoosh(): n = int(.4 * SR); x = rng.standard_normal(n); x = np.convolve(x, np.ones(8) / 8, "same"); return x * np.sin(np.pi * np.arange(n) / n) ** 2 * .35
def pop(): tt = t_(.09); fr = np.linspace(700, 140, len(tt)); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(len(tt), .001, .03) * .8
def thud(): tt = t_(.3); return np.sin(2 * np.pi * 110 * tt * np.exp(-tt * 3)) * env(len(tt), .001, .07)


def _read(p: Path) -> np.ndarray:
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768; sr = w.getframerate()
    idx = np.arange(0, len(x), sr / SR)
    return np.interp(idx, np.arange(len(x)), x)


# Треки з YouTube Audio Library лежать у приватному репозиторії provse-music (MUSIC_DIR).
TRACKS = {
    "tense": ["False Vacuum Decay", "In Battery", "Friction"],
    "epic": ["Risen", "In Battery", "Friction"],
    "upbeat": ["Friction", "Travelling Light", "Chromatic Rag"],
    "warm": ["Island Summer Breeze", "Travelling Light", "Sirius Jazz"],
    "playful": ["Chromatic Rag", "Island Summer Breeze", "Sirius Jazz"],
    "calm": ["Sirius Jazz", "Travelling Light", "Island Summer Breeze"],
}


def track(mood: str, dur: float) -> np.ndarray | None:
    import os, random, subprocess, tempfile
    d = Path(os.environ.get("MUSIC_DIR", "music"))
    if not d.exists():
        return None
    alls = sorted(d.glob("*.mp3"))
    if not alls:
        return None
    # Чергування: беремо трек, який звучав найдавніше (історія в state/music_recent.json), бажано під настрій
    import json
    hist_p = Path(os.environ.get("MUSIC_HISTORY", "state/music_recent.json"))
    try:
        recent = json.loads(hist_p.read_text())
    except Exception:
        recent = []
    fresh = [f for f in alls if f.name not in recent[-max(1, len(alls) - 2):]] or alls
    mood_fit = [f for f in fresh if any(f.name.startswith(t) for t in TRACKS.get(mood, []))]
    f = random.choice(mood_fit or fresh)
    try:
        hist_p.parent.mkdir(parents=True, exist_ok=True); hist_p.write_text(json.dumps((recent + [f.name])[-20:], ensure_ascii=False))
    except Exception:
        pass
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        start = random.uniform(4, 25)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.1f}", "-i", str(f), "-t", f"{dur + 1:.1f}",
                        "-ac", "1", "-ar", str(SR), tmp.name], check=True)
        x = _read(Path(tmp.name))
    print("музика:", f.name)
    fade = np.ones(len(x)); k = int(1.5 * SR)
    fade[:int(.3 * SR)] = np.linspace(0, 1, int(.3 * SR)); fade[-k:] = np.linspace(1, 0, k)
    return x * fade / max(1e-6, np.abs(x).max())


def mix(voice_wav: Path, end: float, channel: str, cuts: list[float], stamps: list[float], out: Path, vo: float = .2, mood: str = "") -> Path:
    v = _read(voice_wav); n = int(end * SR)
    y = np.zeros(n)
    y[int(vo * SR):int(vo * SR) + len(v)] += v[:n - int(vo * SR)] * 1.0
    mus = track(mood or {"svit": "warm", "polityka": "tense", "sport": "epic"}.get(channel, "upbeat"), end)
    if mus is None:
        mus = music(end, CHANNEL_MOOD.get(channel, "bright")) * .5
    mus = np.pad(mus, (0, max(0, n - len(mus))))[:n]
    talk = np.zeros(n); talk[int(vo * SR):int(vo * SR) + len(v)] = np.abs(v[:n - int(vo * SR)]) > .02
    duck = np.convolve(talk, np.ones(int(.3 * SR)) / int(.3 * SR), "same")
    # тихий фон: близько −28 дБ під голосом, −20 дБ у паузах
    y += mus * (.10 - .065 * np.clip(duck * 3, 0, 1))
    for i, t in enumerate(cuts):
        s = whoosh() if i else pop(); a = int(t * SR); y[a:a + len(s)] += s[:max(0, n - a)] * .15
    for t in stamps:
        s = thud(); a = int(t * SR); y[a:a + len(s)] += s[:max(0, n - a)] * .4
    y *= .92 / max(1e-6, np.abs(y).max())
    k = int(.6 * SR); y[-k:] *= np.linspace(1, 0, k) ** 2   # м'яке затухання в кінці, без різкого обриву
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
    # Гучність як у звичайних Shorts, без «крику»: −18 LUFS, пік не вище −2 дБ
    import subprocess
    tmp = out.with_suffix(".ln.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-af", "loudnorm=I=-18:TP=-2:LRA=9", "-ar", str(SR), str(tmp)], check=True)
    tmp.replace(out)
    return out
