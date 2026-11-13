"""Сценарій під тренд: один запит до Gemini (JSON) + жорстка перевірка правил кодом."""
from __future__ import annotations

import json
import re

import os
from pathlib import Path

from . import gemini

TOPIC = {"dim": "дім", "ekonomika": "економіку", "yizha": "їжу", "avto": "авто", "sport": "спорт",
         "svit": "світ", "polityka": "політику"}

CHANNEL_NOTES = {
    "ekonomika": "Лише загальна інформація про гроші й економіку. Жодних фінансових порад (не кажи купувати, продавати, інвестувати).",
    "svit": "Канал ЛИШЕ добрих і дивовижних новин світу, про які мало говорять: тварини, природа, відкриття, рекорди, неочікувані позитивні історії. Жодних криз, трагедій, конференцій, заяв політиків.",
    "dim": "Побут, комуналка, світло, тепло. Практична користь для звичайної родини. Без медичних порад.",
    "yizha": "Ціни на продукти, їжа, кухня. Практично й зрозуміло.",
    "avto": "Авто, пальне, правила для водіїв. Реальні моделі, конкретні цифри.",
    "sport": "Матчі, бої, рекорди. Емоційно, з рахунками й цифрами.",
    "polityka": "Факти про рішення влади й переговори без власних оцінок. Чужі заяви подавай через «за словами …».",
}

RULES = (Path(__file__).resolve().parents[1] / "docs" / "RULES.md").read_text(encoding="utf-8")

PROMPT = """Ти сценарист українського YouTube Shorts каналу «Все про {topic}». {note}

Нижче головні правила власника. Дотримуйся КОЖНОГО пункту.
<rules>
{rules}
</rules>

Тренд Google в Україні зараз: «{query}».
Матеріали (використовуй ЛИШЕ факти звідси, нічого не вигадуй):
{materials}

Обери оформлення, яке найвлучніше пасує саме до цієї історії (настрій, тема, кольори), з цього списку:
{styles}
І настрій музики з: tense, upbeat, warm, epic, playful, calm.

Напиши текст для диктора за правилами вище (35–50 слів, хук до 8 слів, лише кирилиця, числа словами, кінцівка «Підписуйся, тут усе про {topic}!»).
Якщо тема не підходить каналу або немає двох незалежних джерел, поверни "ok": false і поясни чому.

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
{{"ok": true/false, "reject_reason": "", "style": "назва стилю зі списку", "music_mood": "...", "script": "...", "title": "назва до 70 символів, закінчується на #shorts",
 "description": "2–4 речення фактів", "hashtags": ["5–7 хештегів без #"],
 "sources": [{{"name": "видання", "url": "посилання з матеріалів"}}],
 "highlight": ["ключові слова сценарію для підсвітки, 5–10"],
 "scenes": [{{"type": "...", "from_word": 0, ...}}]}}
"""

BANNED = re.compile(r"\b(росі[яїюєй]\w*|россия\w*|російськ\w*|российск\w*|рф)\b", re.I)


def words(text: str) -> list[str]:
    return text.split()


def _clean(x):
    if isinstance(x, str):
        return x.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ")
    if isinstance(x, list):
        return [_clean(i) for i in x]
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    return x


def validate(s: dict, channel: str, allowed_urls: set[str]) -> list[str]:
    s.update(_clean({k: v for k, v in s.items() if k not in ("sources",)}))
    errs = []
    if not s.get("ok"):
        return ["модель відмовилась: " + s.get("reject_reason", "")]
    w = words(s.get("script", ""))
    if re.search(r"[A-Za-z]", s.get("script", "")):
        errs.append("у тексті для диктора є латинські літери: " + ", ".join(sorted(set(re.findall(r"[A-Za-z][A-Za-z-]*", s["script"])))[:5]) + " (пиши українською транслітерацією)")
    if not s.get("script", "").split(".")[0] or len(re.split(r"[.!?]", s.get("script", ""))[0].split()) > 9:
        errs.append("перше речення (хук) довше за 8 слів")
    if not 33 <= len(w) <= 55:
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


def write_script(query: str, channel: str, materials: list[dict], styles: str = "", tries: int = 2) -> dict:
    mats = "\n\n".join(f"[{i + 1}] {m['source']} · {m['title']}\n{m['url']}\n{m['text'][:1800]}" for i, m in enumerate(materials))
    prompt = PROMPT.format(topic=TOPIC[channel], note=CHANNEL_NOTES[channel], query=query, materials=mats, styles=styles or "- blueprint__bold", rules=RULES.replace("{", "(").replace("}", ")"))
    allowed = {m["url"] for m in materials}
    last = []
    for _ in range(tries):
        if os.environ.get("ANTHROPIC_API_KEY"):
            from . import claude
            s = claude.generate_json(prompt)
        else:
            s = gemini.generate_json(prompt)
        last = validate(s, channel, allowed)
        if not last:
            return s
        prompt += "\n\nПопередня відповідь порушила правила: " + "; ".join(last) + ". Виправ і поверни JSON ще раз."
    raise ValueError("сценарій не пройшов перевірку: " + "; ".join(last))


if __name__ == "__main__":  # швидка перевірка валідатора
    demo = json.loads(open("tests/fixtures/script_demo.json", encoding="utf-8").read())
    print(validate(demo, "ekonomika", {x["url"] for x in demo["sources"]}))
