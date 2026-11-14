"""Точний час слів за справжнім розпізнаванням мови (sherpa-onnx parakeet), а не за оцінкою по голосних.

  python tools/cc_align.py <job_dir>

Бере <job_dir>/voice.wav і текст зі script.txt, переписує <job_dir>/words.json ([[слово, секунда], ...]).
Запускай ПІСЛЯ сповільнення голосу (atempo) і ДО kit_new.py, інакше текст у кадрі біжить попереду диктора.
Модель: tools/asr/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8 (завантаження з релізів sherpa-onnx, asr-models).
"""
import difflib
import glob
import json
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx

ROOT = Path(__file__).resolve().parent.parent
job = Path(sys.argv[1])
script = (job / "script.txt").read_text(encoding="utf-8").split()
d = glob.glob(str(ROOT / "tools" / "asr" / "sherpa-onnx-nemo-*"))[0]
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{d}/encoder.int8.onnx", decoder=f"{d}/decoder.int8.onnx", joiner=f"{d}/joiner.int8.onnx",
    tokens=f"{d}/tokens.txt", model_type="nemo_transducer", num_threads=4)
with tempfile.NamedTemporaryFile(suffix=".wav") as t:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(job / "voice.wav"), "-ac", "1", "-ar", "16000", t.name], check=True)
    w = wave.open(t.name)
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
s = rec.create_stream(); s.accept_waveform(16000, a); rec.decode_stream(s)
aw = []
for tok, ts in zip(s.result.tokens, s.result.timestamps):
    if tok.startswith(" ") or not aw:
        aw.append([tok.strip(), ts])
    else:
        aw[-1][0] += tok
norm = lambda x: re.sub(r"[^\wʼ'’]", "", x.lower()).replace("unk", "")
A = [norm(x) for x, _ in aw]; S = [norm(x) for x in script]
sa, aa = "".join(S), "".join(A)
amap = {}
for b in difflib.SequenceMatcher(None, sa, aa, autojunk=False).get_matching_blocks():
    for k in range(b.size):
        amap[b.a + k] = b.b + k
ct = []  # час кожної літери розпізнаного тексту
for i, (_, t0) in enumerate(aw):
    n = len(A[i]); t1 = aw[i + 1][1] if i + 1 < len(aw) else t0 + .4
    ct += [t0 + (t1 - t0) * k / max(n, 1) * .6 for k in range(n)]
out, pos = [], 0
for word, sw in zip(script, S):
    t = next((ct[amap[pos + k]] - k * .06 for k in range(len(sw)) if pos + k in amap), None)
    out.append([word, t]); pos += len(sw)
for i, (_, t) in enumerate(out):  # слова, яких не розпізнало: між сусідами
    if t is None:
        prev = out[i - 1][1] if i else 0.0
        nxt = next((x[1] for x in out[i + 1:] if x[1] is not None), prev + .4)
        out[i][1] = (prev + nxt) / 2
for i in range(1, len(out)):
    out[i][1] = max(out[i][1], out[i - 1][1] + .05)
out[0][1] = min(out[0][1], .05)
(job / "words.json").write_text(json.dumps([[x, round(t, 3)] for x, t in out], ensure_ascii=False), encoding="utf-8")
print("розпізнано:", " ".join(x for x, _ in aw))
print(f"час слів оновлено: {len(out)} слів, останнє на {out[-1][1]:.2f} с")
