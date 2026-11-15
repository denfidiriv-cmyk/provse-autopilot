"""Синтезовані звукові ефекти для довгих роликів (без ліцензійних питань).
python tools/sfx_lib.py  -> assets_cache/sfx/*.wav (48 кГц, моно)"""
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(11)
t_ = lambda d: np.arange(int(d * SR)) / SR
def env(n, a=.002, d=.3): t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def sweep(f0, f1, d): t = t_(d); f = f0 * (f1 / f0) ** (t / d); return np.sin(2 * np.pi * np.cumsum(f) / SR)

def whoosh(d=.45, lo=300, hi=5000):
    n = int(d * SR); x = rng.standard_normal(n)
    # частотна розгортка: шум, що «пролітає»
    out = np.zeros(n); k = 6
    for i in range(k):
        a, b = i * n // k, (i + 1) * n // k
        f = lo * (hi / lo) ** (i / (k - 1)) if i < k / 2 else hi * (lo / hi) ** ((i - k / 2) / (k / 2))
        out[a:b] = bp(x[a:b], max(80, f * .5), min(20000, f * 1.6))
    e = np.sin(np.pi * np.arange(n) / n) ** 3
    return out * e * .9
def boom(): d = 1.4; t = t_(d); f = 55 * np.exp(-t * 1.2) + 30; return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .003, .45) + lp(rng.standard_normal(len(t)), 250) * env(len(t), .001, .08) * .7) * .95
def hit(): d = .5; t = t_(d); return (np.sin(2 * np.pi * 90 * t) * env(len(t), .001, .12) + hp(rng.standard_normal(len(t)), 2000) * env(len(t), .0005, .02) * .5) * .9
def pop(): d = .1; t = t_(d); return sweep(900, 180, d) * env(len(t), .001, .035) * .8
def shutter():
    x = np.zeros(int(.35 * SR))
    for o, g in [(0, 1), (.09, .7)]:
        n = int(.03 * SR); s = int(o * SR); x[s:s + n] += hp(rng.standard_normal(n), 1800) * env(n, .0003, .006) * g
    return x * .9
def scratch():
    d = .55; t = t_(d); speed = np.sin(2 * np.pi * 3.2 * t) * 2.2
    src = lp(rng.standard_normal(len(t) * 3), 3000)
    idx = np.clip((np.cumsum(np.abs(speed)) * 1.5).astype(int), 0, len(src) - 1)
    return bp(src[idx], 300, 4000) * env(len(t), .005, .3) * 1.4
def riser(): d = 1.6; t = t_(d); return (bp(rng.standard_normal(len(t)), 500, 6000) * (t / d) ** 2.5 * .6 + sweep(200, 1400, d) * (t / d) ** 3 * .25)
def ding(): t = t_(1.2); return sum(a * np.sin(2 * np.pi * 1320 * k * t) for k, a in [(1, .6), (2.01, .25), (3.02, .12)]) * env(len(t), .001, .35)
def tick(): n = int(.02 * SR); return hp(rng.standard_normal(n), 3000) * env(n, .0003, .004) * .7
def typewriter():
    x = np.zeros(int(.9 * SR))
    for k in range(7):
        c = tick(); s = int(k * .12 * SR + rng.uniform(0, .02) * SR); x[s:s + len(c)] += c
    return x

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets_cache" / "sfx"; out.mkdir(parents=True, exist_ok=True)
    for name, fn in dict(whoosh=whoosh, whoosh_fast=lambda: whoosh(.28, 800, 8000), boom=boom, hit=hit, pop=pop, shutter=shutter,
                         scratch=scratch, riser=riser, ding=ding, typewriter=typewriter).items():
        x = fn(); x = x / max(1e-9, np.abs(x).max()) * .9
        wavfile.write(out / f"{name}.wav", SR, (x * 32767).astype(np.int16))
    print("sfx ->", out)
