"""Готує props для remotion_short (композиція Short) зі специфікації трендового шортса.

  python3 tools/remotion_props.py <spec_name> <cards1.json> [cards2.json ...]

spec_name: docs/trend_shorts/<spec_name>.json (той самий формат, що для trend_short.sh).
cards*.json: списки карток big_card.py (out, big, unit, label, bg, fg, accent). Сцена «img:X.jpg»,
у якої є картка з таким out, рендериться як анімована картка, інакше як фото.
Аудіо береться з <job>/mix.wav (голос + музика від cc_mix.py), фото копіюються в public/media/<name>/.
Фото з файлом <img>/<stem>_cut.png отримують вирізаний без фону предмет поверх розмитого фону.
Пише remotion_short/props/<name>.json.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RS = ROOT / 'remotion_short'


def main():
    name = sys.argv[1]
    spec = json.loads((ROOT / 'docs/trend_shorts' / f'{name}.json').read_text())
    cards = {}
    for p in sys.argv[2:]:
        for c in json.loads(Path(p).read_text()):
            cards[Path(c['out']).name] = c
    words = json.loads((Path(spec['src']) / 'words.json').read_text())
    mix = Path(spec['job']) / 'mix.wav'
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(mix)]).decode())
    media = RS / 'public/media' / name
    media.mkdir(parents=True, exist_ok=True)
    shutil.copy(mix, media / 'mix.wav')
    ts = [w[1] for w in words]
    outro = ts[spec['end_w']]
    ws = []
    for i, (t, s) in enumerate(words):
        e = ts[i + 1] if i + 1 < len(ts) else s + 0.6
        ws.append({'text': t, 'start': s, 'end': max(s + 0.12, e - 0.02)})
    scenes = []
    sc = spec['scenes']
    for i, (wi, src, title, acc) in enumerate(sc):
        start = ts[wi]
        end = ts[sc[i + 1][0]] if i + 1 < len(sc) else outro
        fn = src.split(':', 1)[1]
        s = {'start': round(start, 3), 'end': round(end, 3)}
        if fn in cards:
            c = cards[fn]
            s.update(kind='card', card={k: c.get(k, '') for k in ('big', 'unit', 'label', 'bg', 'fg', 'accent')})
        else:
            img = Path(spec['img']) / fn
            shutil.copy(img, media / fn)
            s.update(kind='photo', src=f'media/{name}/{fn}')
            cut = img.with_name(img.stem + '_cut.png')
            if cut.exists():
                shutil.copy(cut, media / cut.name)
                s['cutout'] = f'media/{name}/{cut.name}'
            if title:
                s.update(title=title, titleAcc=acc)
        scenes.append(s)
    props = {
        'audio': f'media/{name}/mix.wav', 'duration': round(dur, 3), 'accent': spec['accent'],
        'keywords': spec.get('keywords', []), 'scenes': scenes, 'words': ws,
        'outro': {'top': spec['end_text'][0], 'acc': spec['end_text'][1], 'bg': spec['bg'], 'bg2': spec['bg2'], 'start': round(outro, 3)},
    }
    (RS / 'props').mkdir(exist_ok=True)
    out = RS / 'props' / f'{name}.json'
    out.write_text(json.dumps(props, ensure_ascii=False, indent=1))
    print(out, 'dur', dur)


if __name__ == '__main__':
    main()
