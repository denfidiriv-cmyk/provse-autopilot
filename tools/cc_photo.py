"""Фото з Wikimedia Commons з вільною ліцензією, без людей.

  python tools/cc_photo.py "<запит англійською>" <файл.jpg>

Друкує JSON {path, credit, page} або null. credit обов'язково показати на кадрі й додати в опис.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.photos import find_photo  # noqa: E402

print(json.dumps(find_photo(sys.argv[1], Path(sys.argv[2])), ensure_ascii=False))
