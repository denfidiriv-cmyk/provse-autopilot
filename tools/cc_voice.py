"""Озвучка для Claude Code: текст -> voice.wav + words.json з часом кожного слова.

  python tools/cc_voice.py <голос Gemini> <файл_з_текстом.txt> <папка_виходу>

Створює у папці: voice.wav (24 кГц, паузи підрізані, темп 1.06), words.json ([[слово, секунда], ...]),
END.txt (рекомендована довжина ролика: голос + 1,2 с). Текст має бути лише українською кирилицею, числа словами.
"""
import json
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.voice import synth, tighten_and_align  # noqa: E402

voice, text_file, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
text = " ".join(text_file.read_text(encoding="utf-8").split())
raw = synth(text, voice, out / "voice_raw.wav")
wt = tighten_and_align(raw, text.split(), out / "voice.wav")
(out / "words.json").write_text(json.dumps(wt, ensure_ascii=False), encoding="utf-8")
with wave.open(str(out / "voice.wav")) as w:
    dur = w.getnframes() / w.getframerate()
(out / "END.txt").write_text(f"{dur + 1.2:.2f}")
print(f"голос {dur:.2f} с, слів {len(wt)}; файли в {out}")
