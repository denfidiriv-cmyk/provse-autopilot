# PROВсе Autopilot

Мета: програма на Python, яка сама веде мережу YouTube Shorts каналів «Все про …» (PROВсе Production) на комп'ютері власника з Windows. Вона шукає тренди, пише сценарій, озвучує, рендерить 2D-анімацію з субтитрами й музикою, завантажує відео на правильний канал з назвою, описом і хештегами, а потім аналізує статистику і покращує наступні відео. Мінімум витрат: дешеві API-виклики замість браузерної автоматизації.

## Канали

| Канал | ID | Хендл | Голос Gemini TTS | Що публікуємо |
|---|---|---|---|---|
| Все про дім (Short Films Gray) | UCckPSxt48pjgDWtm-nMv6og | @Fox_films_ff | Kore | дім, побут, комуналка (не здоров'я) |
| Все про економіку | UCuTHeI_iY8QAvXfVdJbyHQA | @provse.ekonomika.production | Charon | як працюють гроші й економіки; загальна інформація, без фінансових порад |
| Все про авто | UCXTceH3zC-lkQeYMkUWMx8A | @provse.avto.production | Iapetus | авто, пальне, закони для водіїв; реальні впізнавані моделі |
| Все про їжу | UCVCyipxXg5EKunmXv40rOqQ | @provse.food.production | Aoede | їжа, ціни на продукти, кухня |
| Все про спорт | UCf0J6E1J8g_gVcFCXKm9Vyw | @provse.sport.production | Fenrir | матчі, бої, рекорди |
| Все про світ | UCfakQTmDnhvMJrVGXUFUKTQ | @provse.svit.production | Zephyr | добрі й дивовижні новини світу; також каруселі-дописи |
| Все про політику | UCsK3BvYW5XH5kc-OH9yB2tg | @provse.politica.production | Orus / Puck | переговори, закони, рішення влади |

Окремо в планах дитячий канал мультиків (Veo 3, власні персонажі, англійські пісеньки; перший тест «Pip and Mo» у docs).

## Правила контенту (обов'язкові)

1. Тема береться з Google Trends: Україна, останні 24 години, сортування за обсягом. Тренд визначає канал. Якщо в каналу немає трендів або він давно без відео, робимо пізнавальне відео на його тему.
2. Теми мають чіпляти життя людини. Нудні нішеві теми (бойлер, накип у чайнику) не беремо.
3. Кожен факт звіряємо щонайменше з двома джерелами, джерела йдуть в опис. Цифри, які хтось «заявив», підписуємо «за словами …».
4. Замість «Росія» кажемо й пишемо «москалі»; замість російського прапора малюємо піратський (череп і кістки).
5. Ніколи не ставити маленькі мітки-заголовки вгорі кадру на кшталт «ЦІКАВЕ · ПОГОДА». Верх кадру порожній.
6. Вертикаль 9:16, 1080×1920, 15–25 секунд. Хук у першу секунду: головна цифра або факт на екрані з першого кадру, ніяких біографій на початку.
7. Зміна в кадрі кожні 2–4 секунди з нерівними інтервалами; кінець закільцьований на перший кадр.
8. Субтитри слово за словом, жирний шрифт з обведенням, ключові слова червоні; жодного тексту в нижніх 320 px і правих 120 px (інтерфейс YouTube).
9. Голос чіткий і енергійний, не глухий. У налаштуваннях стилю TTS: «energetic, upbeat news anchor, clear diction».
10. Музика й звукові ефекти під тему каналу. Стилі між відео різні, щоб усе не виглядало однаково.
11. Для регіонів України використовуємо точну карту (`tools/ua.js`, geoBoundaries ADM1). Київська область не належить до півдня чи центру.
12. Справжні фото місць, будівель і предметів беремо з вільними ліцензіями (Wikimedia Commons тощо) і підписуємо автора й ліцензію на кадрі та в описі.
13. Кінцівка: «Підписуйся, тут усе про …».
14. Назва українською + `#shorts`, короткий опис, джерела, 4–8 хештегів.

Улюблений стиль власника: «стіл розслідувача» у стилі Vox (`templates/vox_desk`). Інші перевірені стилі: паперовий колаж (`templates/collage`), шаблон Shorts з одометром і плашками (`templates/shorts_template`), Canvas-сцени рушія (`engine`, `templates/scene_bodies`), експлейнер-граматики huashu (`templates/huashu_specs`).

## Публікація

За замовчуванням програма вивантажує відео **приватним** і надсилає власнику в Telegram прев'ю з кнопками «Опублікувати» / «Переробити». Параметр `AUTO_PUBLISH=false` у `.env`; власник може сам перемкнути. Ліміт YouTube: телефон каналу верифікований, але все одно стежити за денним лімітом завантажень.

## Архітектура, яку треба побудувати

```
provse_autopilot/
  config/channels.yaml        # таблиця вище: id, голос, стиль, теми, частота
  config/rules/<channel>.md   # правила + висновки аналітики (оновлюються автоматично)
  pipeline/trends.py          # pytrends або парсинг trends.google.com/trending?geo=UA&hours=24
  pipeline/pick.py            # LLM: тренд -> канал -> тема (дешева модель)
  pipeline/research.py        # пошук 2+ джерел, факти з цитатами
  pipeline/script.py          # LLM: сценарій 40–55 слів за правилами + список сцен
  pipeline/tts.py             # Gemini TTS API (голос з config), wav 24 kHz
  pipeline/align.py           # обгортка tools/align_28.py + tools/asr (sherpa-onnx parakeet) -> таймінги слів
  pipeline/render.py          # генерує index.html з шаблону (gen.py-підхід) і рендерить hyperframes
  pipeline/photos.py          # Wikimedia Commons API: пошук, ліцензія, автор, завантаження
  pipeline/mix.py             # tools/mix.py: голос + музика + SFX за подіями
  pipeline/upload.py          # YouTube Data API v3, OAuth токен на кожен канал, privacyStatus=private
  pipeline/notify.py          # Telegram-бот: прев'ю + кнопки
  pipeline/analytics.py       # YouTube Analytics API: перегляди, утримання, CTR; LLM-розбір; дописати висновки в config/rules
  run_channel.py <channel>    # один повний цикл
  run_weekly_review.py
  scheduler/                  # .xml для Windows Task Scheduler
```

Кроки збирання для Claude Code:
1. Прочитай цей файл і `docs/PIPELINE_NOTES.md`. Шляхи в скриптах з `tools/` і `templates/` жорстко прописані під Linux-хмару (`/tmp/claude-0/...`, `/opt/pw-browsers/...`) — заміни на відносні та на Chromium з Playwright.
2. Встанови залежності: Python 3.11+, ffmpeg, Node 20+, `npx hyperframes@0.8.216`, `pip install playwright sherpa-onnx scipy numpy pillow pytrends google-api-python-client google-auth-oauthlib python-telegram-bot pyyaml`, `playwright install chromium`. Модель ASR: sherpa-onnx `nemo-parakeet-tdt-0.6b-v3-int8` (завантажити з релізів sherpa-onnx у `tools/asr/`).
3. Зроби `.env.example`: `ANTHROPIC_API_KEY` або `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `AUTO_PUBLISH=false`. OAuth для YouTube: client_secret.json + окремий токен на кожен канал (бренд-акаунти).
4. Побудуй пілот на одному каналі (наприклад «Все про політику» у стилі vox_desk), прожени повний цикл до приватного завантаження, покажи результат власнику.
5. Тоді розшир на інші канали й додай тижневу аналітику.

LLM-виклики тримай короткими й дешевими: одна відповідь JSON на вибір теми, одна на сценарій, одна на аналітику. Решта — детермінований код.
