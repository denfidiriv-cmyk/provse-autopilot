# Як зараз зроблено кожне відео (перевірений ручний конвеєр)

1. Озвучка: Gemini TTS (AI Studio, модель flash TTS), голос із таблиці каналів, стиль «energetic, upbeat news anchor». Результат wav.
2. Вирівнювання: `ffmpeg -i voice.wav -ar 24000 -ac 1 v_raw.wav`, далі `python3 tools/align_28.py v_raw.wav vt.wav words.txt wt_dp.json` (прибирає паузи, дає часи слів через DP). Потім ASR: `ffmpeg -i vt.wav -ar 16000 -ac 1 p16.wav; python3 tools/asr/run.py p16.wav` -> tok.json; `python3 tools/asr/align2.py tok.json words.txt wordtimes.json wt_dp.json` уточнює часи.
3. Розрізи й темп: `python3 tools/mkcuts.py <proj> <tempo 1.04> '[індекси слів-склейок]' a,b,c <proj>.js` -> END.txt, wordtimes_t.json (часи після прискорення), vt_t.wav.
4. Візуал, два шляхи:
   a. HTML + GSAP + hyperframes (рекомендовано): `templates/*/gen.py` читає `wordtimes_t.json` і `END.txt`, будує `index.html` з однією паузованою GSAP-таймлінією, де кожна подія прив'язана до часу слова `T(i)`. Рендер: `npx hyperframes@0.8.216 render --fps 30 --quality delivery`. Субтитри вже всередині шаблону.
   b. Canvas-рушій (`engine/`): сцени в `scenes_x/<p>.js` (збирати з `tools/common_head.js` + `templates/scene_bodies/<p>.js`), рендер `python3 render.py --film <p>film --fps 30 --out film_raw.mp4`, потім субтитри шаблоном `templates/captions` через `tools/finish.sh <p>`.
5. Мікс: у `tools/mix.py` профіль на проєкт (`ev=[(T(i), sfx, gain)...]`), запуск `python3 tools/mix.py <p> "<music.mp3>" 0` -> final_mix.wav. Музика: бібліотека YouTube Audio Library у папці власника.
6. Збирання: `ffmpeg -i render.mp4 -i final_mix.wav -map 0:v -map 1:a -c:v libx264 -b:v 2600k -preset slow -pix_fmt yuv420p -c:a aac -b:a 160k -shortest -movflags +faststart out.mp4`.
7. Завантаження (зараз через браузер, у програмі через YouTube Data API): назва, опис, «не для дітей», «змінений контент: ні», публічний доступ лише після підтвердження власника.

Мультик-тест «Pip and Mo» (Veo 3 у Gemini, особистий акаунт): Gemini продовжує попереднє відео в тому ж чаті, тому кожен наступний промпт дає ролик на 10 с довший. Персонажі в промпті описуються щоразу дослівно однаково.
