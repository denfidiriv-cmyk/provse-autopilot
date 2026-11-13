"""Зведення: голос (EQ, темп) + музика з дакінгом + синтезовані ефекти під стиль каналу.
python3 mix.py <proj> <music.mp3> <music_offset_s>  → <proj>fr/final_mix.wav (і final_voice.wav)
Опційно EN=1: бере <proj>/en_raw.wav як голос → <proj>fr/mix_en.wav (та сама музика й ефекти)."""
import json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
proj, music, moff = sys.argv[1], sys.argv[2], float(sys.argv[3])
EN = os.environ.get('EN') == '1'
P = os.path.join(HERE, '..', proj); FR = P + 'fr'
END = float(open(f'{P}/END.txt').read())
WT = json.load(open(f'{P}/wordtimes_t.json')); VO = 0.2
T = lambda i: WT[i][1] + VO
eras = open(f'{P}/代码工程/eras_{proj}film.js').read()
CUTS = json.loads(open(f'{P}/代码工程/scenes_x/_wt.js').read().split('window.CUTS=')[1].split(';')[0])
rng = np.random.default_rng(7)
t_ = lambda d: np.arange(int(d * SR)) / SR
def env(n, a=0.002, d=0.3):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def sweep(f0, f1, d, shape='sin'):
    t = t_(d); f = f0 * (f1 / f0) ** (t / d); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if shape == 'sin' else (2 * ((ph / (2 * np.pi)) % 1) - 1) if shape == 'saw' else np.sign(np.sin(ph))
# --- бібліотека ефектів
def click(): n = int(.04 * SR); return (hp(rng.standard_normal(n), 1500) * env(n, .0005, .006) * .8 + np.sin(2 * np.pi * 2200 * t_(.04)) * env(n, .0005, .01) * .5)
def boing(): d = .6; t = t_(d); f = 220 + 380 * np.exp(-t * 6) * np.abs(np.cos(t * 30)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .003, .25) * .8
def whoosh(d=.45, lo=400, hi=4000): n = int(d * SR); x = rng.standard_normal(n); x = bp(x, lo, hi); e = np.sin(np.pi * np.arange(n) / n) ** 2; return x * e * .5
def ding(f=1320, d=1.0): t = t_(d); return sum(a * np.sin(2 * np.pi * f * k * t) for k, a in [(1, .6), (2.01, .25), (3.02, .12)]) * env(len(t), .001, d / 3)
def coin(): t = t_(.5); return sum(a * np.sin(2 * np.pi * f * t) for f, a in [(3100, .4), (4700, .3), (6300, .2)]) * env(len(t), .0005, .12)
def kaching():
    x = np.zeros(int(1.1 * SR))
    for k, o in enumerate([0, .05, .1]): c = coin(); s = int(o * SR); x[s:s + len(c)] += c * (.8 - k * .15)
    b = ding(2100, .9); x[int(.12 * SR):int(.12 * SR) + len(b)] += b * .7; return x
def pop(): d = .09; t = t_(d); return sweep(700, 140, d) * env(len(t), .001, .03) * .9
def boom(): d = .7; t = t_(d); return (np.sin(2 * np.pi * 70 * t) * env(len(t), .002, .18) + lp(rng.standard_normal(len(t)), 300) * env(len(t), .001, .05) * .6) * .9
def rev(): d = 1.0; t = t_(d); f = 55 + 120 * (t / d) ** .7; s = 2 * ((np.cumsum(f) / SR) % 1) - 1; s += .5 * (2 * ((np.cumsum(f * 2.01) / SR) % 1) - 1); return lp(s, 900) * np.minimum(1, t / .1) * np.exp(-np.maximum(0, t - .7) * 8) * .35
def beep(f=1000, d=.08): t = t_(d); return np.sign(np.sin(2 * np.pi * f * t)) * env(len(t), .001, d) * .18
def shimmer(): d = 1.0; t = t_(d); x = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-((t - rng.uniform(0, .5)) ** 2) / .02) for f in rng.uniform(3000, 7000, 9)); return x * .08
def tick(): n = int(.02 * SR); return hp(rng.standard_normal(n), 3000) * env(n, .0003, .004) * .7
def clang(): t = t_(1.0); return sum(a * np.sin(2 * np.pi * f * t) for f, a in [(420, .4), (1130, .3), (1870, .2), (2690, .1)]) * env(len(t), .001, .25) * .7
def whistle(): d = .9; t = t_(d); return sweep(900, 1700, d) * np.minimum(1, t / .1) * np.exp(-np.maximum(0, t - .6) * 10) * .25
def zap(): d = .25; t = t_(d); return sweep(1800, 200, d, 'sq') * env(len(t), .001, .08) * .15
def thud(): d = .3; t = t_(d); return np.sin(2 * np.pi * 110 * t * np.exp(-t * 3)) * env(len(t), .001, .07)
def tickTock(): x = np.zeros(int(1.2 * SR)); [x.__setitem__(slice(int(k * .3 * SR), int(k * .3 * SR) + int(.02 * SR)), tick() * (1 if k % 2 else .6)) for k in range(4)]; return x
def squish(): d = .25; t = t_(d); return lp(rng.standard_normal(len(t)), 900) * env(len(t), .01, .08) * .6 + sweep(300, 120, d) * env(len(t), .005, .06) * .4
def sniff(): return whoosh(.35, 2000, 7000) * .7
def slide(): d = .5; t = t_(d); return sweep(400, 1200, d) * env(len(t), .01, .4) * .3

STY = {
 'lamp': lambda: dict(cut=lambda: whoosh(.35, 600, 5000) * .7, ev=[*[(T(3) + k * .33, click, .8) for k in range(6)], (T(9), boing, .7), (T(12), slide, .8), *[(T(15) + k * .25, click, .5) for k in range(8)],
        (T(29) + .3, beep, 1.0), (T(36), coin, .6), (T(46), ding, .6), (T(55), squish, .8), (T(61), shimmer, 1.0), (T(69) - .05, boom, 1.0), (T(73), click, 1.0), (T(75), whistle, .8), (T(84) - .1, pop, .9)]),
 'money': lambda: dict(cut=lambda: whoosh(.4, 300, 3000) * .5, ev=[*[(.1 + k * .18, coin, .5) for k in range(5)], (T(8), thud, .5), (T(11), thud, .5), (T(15), kaching, .7), (T(21), tick, .8), (T(31) + .3, whoosh, .8), (T(33), coin, .6), (T(34), coin, .5), (T(42), ding, .5),
        (T(50), boom, .8), (T(54) + .2, slide, .5), (T(59), kaching, .7), (T(64) + .2, whoosh, .5), (T(72), thud, .5), (T(85), pop, .9)]),
 'tesla': lambda: dict(cut=lambda: whoosh(.3, 800, 8000) * .9, ev=[(0.05, rev, 1.0), (T(6), boom, .6), (T(12), beep, 1), (T(12) + .12, beep, 1), (T(15), whoosh, .6), (T(29), boom, .9), (T(38), boom, 1.0), (T(48), zap, .7), (T(53), zap, 1.0),
        (T(57), whoosh, .7), (T(65), whoosh, .7), (T(71), rev, .7), (T(76), beep, .8), (T(83), pop, .9)]),
 'meat': lambda: dict(cut=lambda: pop() * .6, ev=[(0.2, thud, .8), (T(7), pop, .9), (T(8), pop, .9), (T(11), sniff, .9), (T(16), squish, .8), (T(17), squish, .6), (T(21), boing, .5), (T(40), ding, .7), (T(44), tick, .8),
        (T(47), tickTock, .8), (T(54), click, 1.0), (T(61), shimmer, 1.2), (T(66), pop, .8), (T(74), clang, .6), (T(76), clang, .8), (T(83), pop, .9)]),
 'marko': lambda: dict(cut=lambda: whoosh(.4, 300, 3000) * .5, ev=[(T(3), kaching, .7), (T(6), pop, .8), (T(8), pop, .8), (T(10), slide, .6), (T(10) + .35, thud, .7), (T(16), ding, .5), (T(19), whoosh, .6), (T(23), zap, .8), (T(32), boing, .6), (T(34), thud, .6), (T(39), ding, .7), (T(44), kaching, .8), (T(49), tick, 1.0), (T(50), tick, 1.0), (T(52), boom, .7), (T(56), pop, .8), (T(58), boing, .5), (T(62), pop, .9)]),
 'scr': lambda: dict(cut=lambda: whoosh(.4, 300, 3000) * .5, ev=[(.1, boom, .7), (T(6), kaching, .8), (T(13), thud, .8), (T(24), pop, .8), (T(25), pop, .8), (T(27), pop, .8), (T(31), tick, 1.0), (T(31) + .28, tick, 1.0), (T(31) + .56, tick, 1.0), (T(34), thud, .5), (T(35), slide, .6), (T(38), kaching, .7), (T(44) - .05, boom, 1.0), (T(48), ding, .5), (T(51), tickTock, .8), (T(55), zap, .7), (T(57), coin, .6), (T(57) + .2, coin, .5), (T(57) + .4, coin, .5), (T(60), thud, .9), (T(64), slide, .6), (T(69), slide, .4), (T(71) + .1, thud, .8), (T(74), ding, .6), (T(79), ding, .7), (T(81), pop, .9)]),
 'pol': lambda: dict(cut=lambda: whoosh(.4, 300, 3000) * .5, ev=[(.1, boom, .6), (T(4), slide, .7), (T(9), thud, .8), (T(10), kaching, .6), (T(15), slide, .5), (T(17), slide, .6), (T(20), beep, .9), (T(21), ding, .6), (T(24), coin, .6), (T(24) + .2, coin, .5), (T(28), thud, .9), (T(30), pop, .8), (T(34), pop, .8), (T(38), thud, .7), (T(48), slide, .6), (T(55), pop, .8), (T(56), ding, .7), (T(62), slide, .5), (T(64), pop, .9)]),
 'ban': lambda: dict(cut=lambda: whoosh(.4, 300, 3000) * .5, ev=[(.1, boom, .6), (T(1), slide, .6), (T(3), slide, .6), (T(5), zap, .6), (T(9), ding, .8), (T(15), pop, .7), (T(23), thud, .8), (T(30), zap, .7), (T(34), slide, .6), (T(35), kaching, .8), (T(39), thud, .8), (T(45), pop, .7), (T(46), pop, .7), (T(47), pop, .7), (T(49), pop, .7), (T(52), slide, .5), (T(55), thud, 1.0), (T(59), coin, .6), (T(59) + .2, coin, .5), (T(63), slide, .5), (T(70), pop, .9)]),
 'spt': lambda: dict(cut=lambda: whoosh(.4, 300, 3000) * .6, ev=[(.1, boom, .8), (T(5), whoosh_k if False else zap, .6), (T(5) + .9, thud, .9), (T(9), pop, .8), (T(12), pop, .8), (T(16), slide, .6), (T(19), slide, .6), (T(20), boom, .5), (T(22), ding, .6), (T(26) + .05, thud, 1.0), (T(26) + .55, thud, 1.0), (T(26) + 1.05, thud, 1.0), (T(37), slide, .6), (T(40), slide, .6), (T(45), thud, .8), (T(47), boom, .6), (T(50), pop, .7), (T(53), slide, .6), (T(57), ding, .8), (T(62), slide, .6), (T(67), slide, .6), (T(71), slide, .6), (T(79), pop, .8), (T(83), pop, .9)]),
 'rzv': lambda: dict(cut=lambda: whoosh(.4, 300, 3000) * .5, ev=[(.05, pop, .7), (.2, pop, .7), (.35, pop, .7), (.5, pop, .7), (T(2), ding, .8), (T(12), thud, .9), (T(22), tick, .8), (T(29), ding, .9), (T(35), pop, .6), (T(40), pop, .5), (T(43), slide, .6), (T(48), pop, .6), (T(56), whoosh_dummy, .0) if False else (T(56), slide, .7), (T(63), kaching, .8), (T(70), slide, .5), (T(74), pop, .7), (T(77), pop, .9)]),
 'frz': lambda: dict(cut=lambda: whoosh(.4, 300, 3000) * .5, ev=[(T(1), zap, .6), (T(4), slide, .5), (T(5), pop, .7), (T(7), ding, .6), (T(10), thud, .6), (T(14), thud, .9), (T(16), slide, .6), (T(23), slide, .6), (T(27), slide, .6), (T(31), ding, .7), (T(41), pop, .6), (T(45), ding, .8), (T(49), pop, .6), (T(50), pop, .6), (T(52), pop, .6), (T(54), tick, .8), (T(57), slide, .5), (T(60), thud, .9), (T(61), slide, .6), (T(65), slide, .6), (T(68), slide, .6), (T(71), ding, .8), (T(76), thud, .8), (T(80), pop, .9)]),
 'akb': lambda: dict(cut=lambda: whoosh(.4, 300, 3000) * .5, ev=[(.1, whoosh_x, .0) if False else (.1, slide, .5), (T(4), tick, 1.0), (T(4) + .25, tick, 1.0), (T(4) + .5, tick, .8), (T(5), pop, .7), (T(8), thud, .7), (T(13), slide, .6), (T(19), thud, .9), (T(29), zap, .7), (T(31), zap, .9), (T(38), slide, .5), (T(41), pop, .7), (T(48), pop, .6), (T(49), pop, .6), (T(50), pop, .6), (T(55), ding, .8), (T(60), pop, .9)]),
 'blr': lambda: dict(cut=lambda: whoosh(.35, 400, 4000) * .5, ev=[(.1, thud, .7), (T(1), zap, .5), *[(T(1) + k * .3, tick, .7) for k in range(14)], (T(14), kaching, .7), (T(18), boing, .5), (T(21), pop, .8), (T(23), slide, .6), (T(25), ding, .6), (T(28), squish, .6), (T(29), pop, .8), (T(31), click, .9), (T(36), slide, .5), (T(41), coin, .6), (T(43), coin, .6), (T(47), kaching, .8), (T(49), pop, .8), (T(51), click, 1.0), (T(53), thud, .8), (T(57), slide, .5), (T(61), ding, .7), (T(63) - .1, pop, .9)]),
 'pgd': lambda: dict(cut=lambda: whoosh(.35, 600, 6000) * .5, ev=[(.1, whoosh, .5), *[(.25 + k * .07, tick, .5) for k in range(14)], (T(7), boing, .5), (T(11), slide, .6), (T(14), ding, .6), (T(17), pop, .7), (T(22), pop, .7), (T(26), pop, .7), (T(30), ding, .7), (T(32), thud, .7), (T(36), tick, 1.0), (T(41), whoosh, .6), (T(46), clang, .6), (T(52), click, .9), (T(55) - .1, pop, .9)]),
 'zst': lambda: dict(cut=lambda: whoosh(.35, 500, 5000) * .5, ev=[(.1, whoosh, .5), (T(4), shimmer, .8), (T(6), boing, .6), (T(9), pop, .8), (T(9) + .2, ding, .5), (T(12), pop, .8), (T(12) + .15, thud, .6), (T(13), boom, .5), (T(16), squish, .7), (T(19), kaching if False else thud, .7), (T(23), tick, .8), (T(28), zap, .6), (T(31), thud, .8), (T(35), clang, .5), (T(41), slide, .5), (T(46), pop, .7), (T(49), tickTock, .7), (T(52), ding, .8), (T(55), whoosh, .6), (T(59), pop, .7), (T(60) - .1, pop, .9)]),
 'vkn': lambda: dict(cut=lambda: whoosh(.35, 500, 5000) * .5, ev=[(.1, whoosh, .5), (T(6), slide, .5), (T(12), thud, .9), (T(12) + .1, boing, .5), (T(19), pop, .7), (T(20), pop, .7), (T(22), pop, .7), (T(25), squish, .6), (T(29), ding, .7), (T(33), tick, .8), (T(39), squish, .9), (T(43), slide, .6), (T(44), pop, .7), (T(51), shimmer, .6), (T(53), whoosh, .6), (T(55), thud, .6), (T(56), ding, .7), (T(58), pop, .7), (T(64), whoosh, .7), (T(70), tickTock, .7), (T(72) - .1, pop, .9)]),
 'abu': lambda: dict(cut=lambda: whoosh(.35, 400, 4000) * .5, ev=[(.05, thud, .8), (T(2), pop, .7), (T(5), slide, .6), (T(9), pop, .7), (T(10), pop, .7), (T(12), pop, .7), (T(13), ding, .6), (T(23), slide, .6), (T(26), slide, .6), (T(30), slide, .6), (T(28), pop, .6), (T(36), thud, .7), (T(41), whoosh, .6), (T(43), boing, .4), (T(47), ding, .6), (T(51), whoosh, .6), (T(55), pop, .7), (T(61), whoosh, .6), (T(63), pop, .7), (T(64) - .1, pop, .9)]),
 'yrm': lambda: dict(cut=lambda: whoosh(.35, 500, 5000) * .5, ev=[(.05, thud, .8), (T(1), boing, .5), (T(8), slide, .6), (T(8) + .2, pop, .7), (T(14), slide, .6), (T(19), thud, .8), (T(24), clang, .6), (T(28), tick, .9), (T(28) + .9, ding, .7), (T(32), slide, .5), (T(36), tick, .9), (T(41), kaching, .7), (T(44), tick, .9), (T(47), slide, .5), (T(52), thud, .8), (T(54) - .1, pop, .9)]),
 'd12': lambda: dict(cut=lambda: whoosh(.35, 600, 6000) * .5, ev=[(.05, slide, .6), (T(2), pop, .7), (T(8), whoosh, .5), (T(9), boing, .4), (T(13), shimmer, .7), (T(19), ding, .6), (T(21), pop, .7), (T(25), slide, .5), (T(30), shimmer, .6), (T(34), pop, .7), (T(35), pop, .7), (T(36), pop, .7), (T(37), pop, .7), (T(38), pop, .7), (T(40), pop, .7), (T(41), ding, .7), (T(43) - .1, pop, .9)]),
 'axi': lambda: dict(cut=lambda: whoosh(.35, 400, 4000) * .5, ev=[(.05, thud, .8), (T(1), pop, .6), (T(10), pop, .7), (T(12), pop, .7), (T(14), whoosh, .7), (T(18), ding, .6), (T(27), slide, .6), (T(32), slide, .6), (T(36), thud, .6), (T(44), pop, .8), (T(45), ding, .6), (T(51), thud, .8), (T(55), slide, .6), (T(61), pop, .7), (T(63), pop, .7), (T(64) - .1, pop, .9)]),
 'svt': lambda: dict(cut=lambda: whoosh(.35, 400, 4000) * .5, ev=[(.05, zap, .6), (.6, click, .9), (1.0, click, .9), (T(6), thud, .7), (T(9), pop, .7), (T(17), boom, .6), (T(18), pop, .6), (T(21), slide, .6), (T(24), tickTock, .6), (T(26), thud, .6), (T(42), pop, .7), (T(44), pop, .7), (T(47), slide, .6), (T(48), zap, .4), (T(50), click, .9), (T(51) - .1, pop, .9)]),
 'mae': lambda: dict(cut=lambda: whoosh(.35, 400, 4000) * .5, ev=[(.05, thud, .8), (T(4), kaching, .8), (T(8), pop, .7), (T(14), pop, .7), (T(20), pop, .7), (T(21), slide, .6), (T(25), thud, .6), (T(37), coin, .7), (T(40), coin, .7), (T(55), clang, .6), (T(60), pop, .7), (T(62) - .1, pop, .9)]),
 'p13': lambda: dict(cut=lambda: whoosh(.35, 400, 4000) * .5, ev=[(.05, slide, .6), (.5, boom, .7), (1.6, thud, .5), (T(3), pop, .7), (T(7), clang, .5), (T(11), thud, .8), (T(14), pop, .7), (T(16), pop, .7), (T(20), shimmer, .6), (T(24), pop, .7), (T(28), squish, .7), (T(29), whoosh, .8), (T(32), tick, .8), (T(38), whoosh, .7), (T(43), pop, .7), (T(44), shimmer, .6), (T(52), ding, .7), (T(55), slide, .5), (T(59) - .1, pop, .9)]),
 'nvd': lambda: dict(cut=lambda: whoosh(.35, 400, 4000) * .5, ev=[(.02, boom, .9), (.08, thud, .9), (T(3), pop, .7), (T(7) - .1, slide, .6), (T(13), pop, .7), (T(14), squish, .6), (T(17) - .1, slide, .6), (T(21), clang, .8), (T(24), pop, .7), (T(26), pop, .7), (T(28) - .1, slide, .6), (T(33), ding, .6), (T(36), tick, .8), (T(41) - .1, pop, .9)]),
    'vtk': lambda: dict(cut=lambda: whoosh(.35, 400, 4000) * .5, ev=[(.02, boom, .8), (.1, thud, .9), (T(6), clang, .6), (T(7) - .1, slide, .6), (T(11) - .1, slide, .6), (T(17), clang, .8), (T(19) - .1, slide, .6), (T(22), pop, .7), (T(29), ding, .6), (T(30) - .1, slide, .6), (T(34), pop, .7), (T(39) - .1, pop, .9)]),
 'nvp': lambda: dict(cut=lambda: whoosh(.35, 400, 4000) * .5, ev=[(.02, boom, .9), (.08, thud, .9), (T(3), pop, .7), (T(7) - .1, slide, .6), (T(13), pop, .7), (T(14), squish, .6), (T(17) - .1, slide, .6), (T(21), clang, .8), (T(24), pop, .7), (T(26), pop, .7), (T(28) - .1, slide, .6), (T(33), ding, .6), (T(36), tick, .8), (T(41) - .1, pop, .9)]),
 'mw': lambda: dict(cut=lambda: whoosh(.3, 500, 4500) * .6, ev=[(T(3), squish, .8), (T(7), boing, .5), (T(16), zap, .7), (T(22), squish, .9), (T(26), boing, .6), (T(29), ding, .5), *[(T(37) - .1 + k * .09, pop, .9 - k * .03) for k in range(14)], (T(45), clang, .4), (T(48) - .03, boom, 1.0), (T(48) + .1, squish, 1.0), (T(54), ding, .5), (T(60), boing, .6), (T(70), zap, .6), (T(72), pop, .6), (T(77), shimmer, 1.0), (T(88) - .02, boom, 1.0), (T(88) + .05, thud, 1.0), (T(98), beep, .9), (T(98) + .15, beep, .9), (T(101), ding, .7), (T(103), squish, .9), (T(107), boing, .5)]),
 'taras': lambda: dict(cut=lambda: whoosh(.3, 500, 4500) * .6, ev=[(T(1) - .25, click, 1.0), (T(1) - .2, boom, .8), (T(5), thud, .8), (T(5) + .25, beep, .9), (T(8), pop, .9), (T(10), tickTock, .8), (T(12), tickTock, .8), (T(14), slide, .7), (T(14) + .3, thud, .7), (T(15), boing, .8), (T(19), zap, 1.0), (T(21), boom, .6), (T(23), pop, .8), (T(25), click, .9), (T(27), ding, .5), (T(34), shimmer, 1.0), (T(35), ding, .7), (T(38), tick, 1.0), (T(39), tick, 1.0), (T(42), click, 1.0), (T(46), whoosh, .7), (T(48), boing, .5), (T(52), pop, .9)]),
 'kettle': lambda: dict(cut=lambda: whoosh(.35, 600, 5000) * .7, ev=[(0.1, boing, .7), (T(5), ding, .5), (T(8), slide, .7), (T(15), pop, .9), (T(17), pop, .9), (T(22), ding, .6), (T(28), shimmer, 1.0), (T(32), boom, .7), (T(36), tickTock, .8), (T(40), clang, .7),
        (T(42) - .05, boom, 1.0), (T(46), squish, .8), (T(49), shimmer, 1.0), (T(56), boing, .6), (T(57) - .1, pop, .9)]),
 'bond': lambda: dict(cut=lambda: whoosh(.4, 300, 3000) * .5, ev=[(.1, coin, .5), (T(2), ding, .5), (T(5), tick, .8), (T(9), coin, .6), (T(14), coin, .5), (T(16), coin, .5), (T(19), kaching, .7), (T(23), slide, .5), (T(27), coin, .6), (T(29), coin, .6),
        (T(35), kaching, .7), (T(40), thud, .6), (T(42), ding, .6), (T(48), whoosh, .6), (T(50), boom, .7), (T(56) - .1, pop, .9)]),
 'fuel': lambda: dict(cut=lambda: whoosh(.3, 800, 8000) * .9, ev=[(0.05, rev, 1.0), (T(2), beep, 1), (T(6), beep, 1), (T(9), whoosh, .6), (T(17), boom, .6), (T(20), kaching, .6), (T(27), boom, .6), (T(31), kaching, .6), (T(35), boom, .9),
        (T(44), rev, .7), (T(48), kaching, .8), (T(54), beep, .8), (T(59), whoosh, .7), (T(60) - .1, pop, .9)]),
 'refr': lambda: dict(cut=lambda: pop() * .6, ev=[(0.2, thud, .8), (T(6), pop, .9), (T(7), ding, .5), (T(9), pop, .9), (T(10), ding, .8), (T(13), pop, .8), (T(19), click, 1.0), (T(21), slide, .8), (T(24), shimmer, 1.2), (T(30), ding, .6),
        (T(35), thud, .8), (T(37), tickTock, .8), (T(39), clang, .6), (T(42), boom, .7), (T(47), pop, .8), (T(51), boing, .5), (T(54) - .1, pop, .9)]),
}[proj]()

def load(path, extra=''):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', path, '-af', extra or 'anull', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']); return np.frombuffer(raw, np.float32).astype(np.float64)
N = int((END) * SR)
tempo = 1.0
r = float(open(f'{P}/tempo.txt').read()) if os.path.exists(f'{P}/tempo.txt') else 1.0
EQ = 'highpass=f=80,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=3,equalizer=f=8000:t=h:w=1:g=1.5,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=80'
if EN:
    v = load(f'{P}/en_raw.wav', EQ + (f',atempo={r}' if r != 1 else ''))
    # EN довший? стиснути до довжини UA голосу
    ua = load(f'{P}/vt_t.wav');
    if len(v) > len(ua) * 1.02:
        k = len(v) / (len(ua) * 1.0); v = load(f'{P}/en_raw.wav', EQ + f',atempo={min(1.5, r * k):.4f}')
else:
    v = load(f'{P}/vt_t.wav', EQ)
voice = np.zeros(N); s0 = int(VO * SR); voice[s0:s0 + len(v)] = v[:max(0, N - s0)]
def lufs_norm(x, target):
    open('/tmp/_n.f32', 'wb').write(x.astype(np.float32).tobytes())
    out = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '/tmp/_n.f32', '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(out[out.rfind('{'):]); g = 10 ** ((target - float(j['input_i'])) / 20); return x * g
voice = lufs_norm(voice, -16)
m = load(music, f'atrim=start={moff}')
m = np.tile(m, int(np.ceil(N / len(m))) + 1)[:N]
fade = np.ones(N); fl = int(1.4 * SR); fade[-fl:] = np.linspace(1, 0, fl); fi = int(.3 * SR); fade[:fi] = np.linspace(0, 1, fi)
m = lufs_norm(m, -29) * fade
# дакінг по огинаючій голосу
envv = np.convolve(np.abs(voice), np.ones(int(.12 * SR)) / int(.12 * SR), 'same'); duck = 1 - 0.45 * np.clip(envv / (np.percentile(envv, 90) + 1e-9), 0, 1)
duck = np.convolve(duck, np.ones(int(.08 * SR)) / int(.08 * SR), 'same'); m *= duck
fx = np.zeros(N)
def put(t, x, g):
    s = int(t * SR); e = min(N, s + len(x))
    if s < N and e > s: fx[s:e] += x[:e - s] * g
for c in CUTS[1:-1]: put(c - .12, STY['cut'](), .7)
for t, f, g in STY['ev']: put(t, f(), g)
fx = fx / (np.max(np.abs(fx)) + 1e-9) * 0.5
mix = voice + m + fx * 0.55
mix = lufs_norm(mix, -14); pk = np.max(np.abs(mix));
if pk > .95: mix *= .95 / pk
name = 'mix_en.wav' if EN else 'final_mix.wav'
os.makedirs(FR, exist_ok=True)
wavfile.write(f'{FR}/{name}', SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
if not EN: wavfile.write(f'{FR}/final_voice.wav', SR, (voice * 32767).astype(np.int16))
print(name, 'END', END, 'len', len(v) / SR)
