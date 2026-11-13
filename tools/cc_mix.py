"""Мікс для ролика: голос + тиха музика з music/ (за настроєм) + легкі whoosh на склейках і удари на штампах.

  python tools/cc_mix.py <job_dir> <mood> "<склейки, с через кому>" ["<удари, с через кому>"]

mood: tense | epic | upbeat | warm | playful | calm. Голос іде без зсуву, тож час слів з words.json збігається з міксом.
Результат: <job_dir>/mix.wav (48 кГц). Склейки передавай ті самі, що в Kit.cut.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline import audio  # noqa: E402

job, mood = Path(sys.argv[1]), sys.argv[2]
cuts = [float(x) for x in sys.argv[3].split(",") if x.strip()] if len(sys.argv) > 3 else []
hits = [float(x) for x in sys.argv[4].split(",") if x.strip()] if len(sys.argv) > 4 else []
end = float((job / "END.txt").read_text())
cuts = [0.0] + [c for c in cuts if c > 0.05]  # перший елемент: м'який акцент на старті, далі whoosh на кожній склейці
audio.mix(job / "voice.wav", end, "", cuts, hits, job / "mix.wav", vo=0.0, mood=mood)
print("мікс:", job / "mix.wav")
