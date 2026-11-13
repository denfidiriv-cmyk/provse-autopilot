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


def mix(voice_wav: Path, end: float, channel: str, cuts: list[float], stamps: list[float], out: Path, vo: float = .2) -> Path:
    v = _read(voice_wav); n = int(end * SR)
    y = np.zeros(n)
    y[int(vo * SR):int(vo * SR) + len(v)] += v[:n - int(vo * SR)] * 1.0
    mus = music(end, CHANNEL_MOOD.get(channel, "bright"))
    talk = np.zeros(n); talk[int(vo * SR):int(vo * SR) + len(v)] = np.abs(v[:n - int(vo * SR)]) > .02
    duck = np.convolve(talk, np.ones(int(.3 * SR)) / int(.3 * SR), "same")
    y += mus[:n] * (1 - .55 * np.clip(duck * 3, 0, 1))
    for i, t in enumerate(cuts):
        s = whoosh() if i else pop(); a = int(t * SR); y[a:a + len(s)] += s[:max(0, n - a)] * .5
    for t in stamps:
        s = thud(); a = int(t * SR); y[a:a + len(s)] += s[:max(0, n - a)] * .7
    y *= .92 / max(1e-6, np.abs(y).max())
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
    return out
