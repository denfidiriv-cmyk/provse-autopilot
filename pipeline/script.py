"""Сценарій під тренд: один запит до Gemini (JSON) + жорстка перевірка правил кодом."""
from __future__ import annotations

import json
import re

from . import gemini

TOPIC = {"dim": "дім", "ekonomika": "економіку", "yizha": "їжу", "avto": "авто", "sport": "спорт",
         "svit": "світ", "polityka": "політику"}

CHANNEL_NOTES = {
    "ekonomika": "Лише загальна інформація про гроші й економіку. Жодних фінансових порад (не кажи купувати, продавати, інвестувати).",
    "svit": "Канал добрих і дивовижних новин світу. Тон світлий, без трагедій.",
    "dim": "Побут, комуналка, світло, тепло. Практична користь для звичайної родини. Без медичних порад.",
    "yizha": "Ціни на продукти, їжа, кухня. Практично й зрозуміло.",
    "avto": "Авто, пальне, правила для водіїв. Реальні моделі, конкретні цифри.",
    "sport": "Матчі, бої, рекорди. Емоційно, з рахунками й цифрами.",
    "polityka": "Факти про рішення влади й переговори без власних оцінок. Чужі заяви подавай через «за словами …».",
}

PROMPT = """Ти сценарист українського YouTube Shorts каналу «Все про {topic}». {note}

Тренд Google в Україні зараз: «{query}».
Матеріали (використовуй ЛИШЕ факти звідси, нічого не вигадуй):
{materials}

Напиши сценарій на 40–55 слів українською для озвучки диктором.
Обов'язкові правила:
1. Перше речення і є хук: головна цифра або найсильніший факт, жодних вступів і біографій.
2. Числа пиши СЛОВАМИ (диктор читає текст), наприклад «вісім тисяч шістсот сорок сім гривень».
3. Кожен факт має бути у щонайменше двох різних джерелах із матеріалів. Цифри, які хтось заявив, подавай «за словами …».
4. Ніколи не пиши «Росія», «російський», «РФ»: замість цього «москалі», «московський».
5. Останнє речення дослівно: «Підписуйся, тут усе про {topic}!»
6. Без фінансових чи медичних порад. Без сенсацій, яких немає в джерелах.
7. Якщо матеріалів замало для двох незалежних джерел або тема не підходить каналу, поверни "ok": false.

Також розбий відео на 4–6 сцен для анімації. "from_word" — номер слова сценарію (з нуля), з якого сцена починається; перша сцена завжди type "hook" з from_word 0, остання сцена починається зі слова «Підписуйся». Типи сцен і поля:
- "hook": {{"big": коротке число або 1–2 слова цифрами, "unit": одиниця або "", "headline": до 7 слів, "photo_query": англійський запит для Wikimedia Commons (місце, предмет, тварина; НІКОЛИ люди)}}
- "number": {{"value": число цифрами з пробілами між тисячами, "unit": "", "label": до 6 слів}}
- "compare": {{"a_label": "", "a_value": число, "b_label": "", "b_value": число, "unit": ""}}
- "quote": {{"text": коротка цитата або позиція до 10 слів, "author": "хто сказав"}}
- "list": {{"items": [3 короткі пункти до 4 слів]}}
- "photo_fact": {{"headline": до 7 слів, "photo_query": англійський запит для Commons, без людей}}
- "cta": {{}}
Будь-якій сцені можна додати "stamp": штамп 1–3 слова великими літерами.

Поверни JSON:
{{"ok": true/false, "reject_reason": "", "script": "...", "title": "назва до 70 символів, закінчується на #shorts",
 "description": "2–4 речення фактів", "hashtags": ["5–7 хештегів без #"],
 "sources": [{{"name": "видання", "url": "посилання з матеріалів"}}],
 "highlight": ["ключові слова сценарію для підсвітки, 5–10"],
 "scenes": [{{"type": "...", "from_word": 0, ...}}]}}
"""

BANNED = re.compile(r"\b(росі[яїюєй]\w*|россия\w*|російськ\w*|российск\w*|рф)\b", re.I)


def words(text: str) -> list[str]:
    return text.split()


def validate(s: dict, channel: str, allowed_urls: set[str]) -> list[str]:
    errs = []
    if not s.get("ok"):
        return ["модель відмовилась: " + s.get("reject_reason", "")]
    w = words(s.get("script", ""))
    if not 35 <= len(w) <= 62:
        errs.append(f"довжина {len(w)} слів")
    end = f"Підписуйся, тут усе про {TOPIC[channel]}!"
    if not s.get("script", "").strip().endswith(end):
        errs.append("немає кінцівки «" + end + "»")
    if BANNED.search(s.get("script", "") + " " + s.get("title", "") + " " + s.get("description", "")):
        errs.append("заборонене слово (Росія/РФ)")
    srcs = [x for x in s.get("sources", []) if x.get("url") in allowed_urls]
    if len({x.get("name") for x in srcs}) < 2:
        errs.append("менше двох джерел із наданих матеріалів")
    if channel == "ekonomika" and re.search(r"\b(купуйте|продавайте|інвестуйте|вкладайте)\b", s.get("script", ""), re.I):
        errs.append("схоже на фінансову пораду")
    sc = s.get("scenes", [])
    if not 3 <= len(sc) <= 7 or sc[0].get("type") != "hook" or sc[0].get("from_word") != 0:
        errs.append("сцени: перша має бути hook з from_word 0, всього 3–7")
    fw = [x.get("from_word", -1) for x in sc]
    if fw != sorted(fw) or len(set(fw)) != len(fw) or (fw and fw[-1] >= len(w)):
        errs.append("from_word мають зростати й бути в межах сценарію")
    if not s.get("title", "").endswith("#shorts"):
        s["title"] = s.get("title", "").rstrip() + " #shorts"
    return errs


def write_script(query: str, channel: str, materials: list[dict], tries: int = 2) -> dict:
    mats = "\n\n".join(f"[{i + 1}] {m['source']} · {m['title']}\n{m['url']}\n{m['text'][:1800]}" for i, m in enumerate(materials))
    prompt = PROMPT.format(topic=TOPIC[channel], note=CHANNEL_NOTES[channel], query=query, materials=mats)
    allowed = {m["url"] for m in materials}
    last = []
    for _ in range(tries):
        s = gemini.generate_json(prompt)
        last = validate(s, channel, allowed)
        if not last:
            return s
        prompt += "\n\nПопередня відповідь порушила правила: " + "; ".join(last) + ". Виправ і поверни JSON ще раз."
    raise ValueError("сценарій не пройшов перевірку: " + "; ".join(last))


if __name__ == "__main__":  # швидка перевірка валідатора
    demo = json.loads(open("tests/fixtures/script_demo.json", encoding="utf-8").read())
    print(validate(demo, "ekonomika", {x["url"] for x in demo["sources"]}))
